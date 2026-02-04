# Copyright (C) 2026-now  danicallero <hola@danicallero.es>

from __future__ import annotations

import io
import logging
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass

import qrcode
from PIL import Image, ImageFilter, ImageOps, ImageDraw

try:
    from wallet.models import Pass, Barcode, BarcodeFormat, EventTicket
except ImportError:
    Pass = Barcode = BarcodeFormat = EventTicket = None

from gestion import passkit_config as pk
from gestion.models import Persona

logger = logging.getLogger(__name__)


@dataclass
class PassResult:
    """Resultado de la generación de un pase."""
    pkpass: bytes
    qr_png: bytes
    acreditacion: str = ""  # Acreditación de la persona para el nombre del archivo


@dataclass
class SavePassResult:
    """Resultado del guardado de un pase en disco."""
    pkpass_path: Path
    qr_path: Path

# ============================================================================
# GESTIÓN DE CERTIFICADOS
# ============================================================================
def extract_p12_certificates(p12_path: str | Path, password: str, tmp_dir: Path) -> tuple[str, str]:
    """Extrae certificado y clave privada de un P12 a archivos PEM usando openssl.
    
    Args:
        p12_path: Ruta al archivo P12
        password: Contraseña del P12
        tmp_dir: Directorio temporal para guardar los PEM
        
    Returns:
        Tupla (ruta_certificado_pem, ruta_clave_privada_pem)
    """
    p12_path = Path(p12_path)
    if not p12_path.exists():
        raise FileNotFoundError(f"Archivo P12 no encontrado: {p12_path}")

    cert_pem = tmp_dir / "cert.pem"
    key_pem = tmp_dir / "key.pem"
    pass_arg = f"pass:{password or ''}"
    
    cmd_base = ["openssl", "pkcs12", "-in", str(p12_path), "-passin", pass_arg]

    try:
        subprocess.run(cmd_base + ["-clcerts", "-nokeys", "-out", str(cert_pem)], 
                      check=True, capture_output=True)
        subprocess.run(cmd_base + ["-nocerts", "-nodes", "-out", str(key_pem)], 
                      check=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        # Reintento con -legacy para versiones antiguas de OpenSSL
        try:
            subprocess.run(cmd_base + ["-legacy", "-clcerts", "-nokeys", "-out", str(cert_pem)], 
                          check=True, capture_output=True)
            subprocess.run(cmd_base + ["-legacy", "-nocerts", "-nodes", "-out", str(key_pem)], 
                          check=True, capture_output=True)
            logger.warning("Certificado extraído usando el flag -legacy de OpenSSL")
        except subprocess.CalledProcessError as e_legacy:
            logger.error(f"Error OpenSSL: {e_legacy.stderr.decode()}")
            raise RuntimeError("No se pudieron extraer los certificados del P12. Revisa la contraseña.") from e_legacy

    return str(cert_pem), str(key_pem)


def ensure_wwdr_pem(wwdr_path: str | Path, tmp_dir: Path) -> str:
    """Asegura que el certificado WWDR esté en formato PEM.
    
    Args:
        wwdr_path: Ruta al certificado WWDR (PEM o DER)
        tmp_dir: Directorio temporal
        
    Returns:
        Ruta al certificado WWDR en formato PEM
    """
    wwdr_path = Path(wwdr_path)
    if not wwdr_path.exists():
        raise FileNotFoundError(f"Certificado WWDR no encontrado: {wwdr_path}")

    # Si ya es PEM, retornar directamente
    with open(wwdr_path, 'rb') as f:
        if b'BEGIN CERTIFICATE' in f.read(100):
            return str(wwdr_path)

    # Convertir de DER a PEM
    pem_path = tmp_dir / "wwdr.pem"
    try:
        subprocess.run(
            ["openssl", "x509", "-inform", "DER", "-in", str(wwdr_path), "-out", str(pem_path)],
            check=True, capture_output=True, text=True
        )
        return str(pem_path)
    except subprocess.CalledProcessError as e:
        logger.error(f"Error OpenSSL al convertir WWDR: {e.stderr}")
        raise RuntimeError("No se pudo convertir el certificado WWDR a PEM") from e

# ============================================================================
# SUSTITUCIÓN DE PLACEHOLDERS
# ============================================================================
def _get_role(persona: Persona) -> str:
    """Determina el rol de una persona."""
    if hasattr(persona, "mentor") and persona.mentor:
        return "Mentor"
    elif hasattr(persona, "patrocinador") and persona.patrocinador:
        return "Sponsor"
    return "Hacker"


def _format_date_values(date: datetime) -> dict[str, str]:
    """Formatea una fecha en diferentes formatos para usar en placeholders.
    
    Returns:
        Dict con claves: 'completa', 'hora', 'fecha'
    """
    if not date:
        return {"completa": "", "hora": "", "fecha": ""}
    
    meses = ["", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
             "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
    
    return {
        "completa": f"{date.day} de {meses[date.month]} de {date.year}, {date.strftime('%H:%M')}h",
        "hora": date.strftime('%H:%M'),
        "fecha": date.strftime('%d-%m-%Y'),
    }


def build_substitution_context(persona: Persona) -> dict[str, str]:
    """Prepara el diccionario de valores para sustituir placeholders.
    
    Example:
        Si en passkit_config tienes "{nombre}" y "{rol}", estos se sustituirán
        con los valores reales de la persona.
    """
    role = _get_role(persona)
    date_values = _format_date_values(pk.PASSKIT_EVENT.get("DATE"))
    
    return {
        "{nombre}": persona.nombre,
        "{correo}": persona.correo,
        "{dni}": getattr(persona, "dni", ""),
        "{rol}": role,
        "{fecha_completa}": date_values["completa"],
        "{hora}": date_values["hora"],
        "{fecha}": date_values["fecha"],
    }


def process_fields(fields_list: list[dict], context: dict[str, str], area: str = "") -> list[dict]:
    """Aplica sustituciones de placeholders en una lista de campos.
    
    Sustituye placeholders en los campos 'value' y 'label'.
    Para campos "back" con URLs, añade información de enlace.
    """
    processed = []
    for field in fields_list:
        item = field.copy()
        for key in ["value", "label"]:
            value = str(item.get(key, ""))
            for placeholder, real_value in context.items():
                value = value.replace(placeholder, str(real_value))
            item[key] = value
        
        # Para campos back con URLs, marcar como clickable
        if area == "back" and item["value"].startswith("http"):
            item["is_link"] = True
        
        processed.append(item)
    return processed

# ============================================================================
# GENERACIÓN DE IMÁGENES
# ============================================================================
def _resize_with_upscaling(img: Image.Image, target_size: int, sharpen: bool = True) -> Image.Image:
    """Redimensiona una imagen para cubrir un área cuadrada sin pixelado.
    
    Usa upscaling intermedio + LANCZOS + (opcional) unsharp mask.
    (Es la única forma en la que conseguí un resultado decente en Apple Wallet)
    """
    max_src = max(img.size)
    upscale_factor = 4 if max_src < target_size * 2 else 2
    intermediate_size = (target_size * upscale_factor, target_size * upscale_factor)
    
    img_high = ImageOps.fit(img, intermediate_size, Image.Resampling.LANCZOS, centering=(0.5, 0.5))
    img_out = img_high.resize((target_size, target_size), Image.Resampling.LANCZOS)
    
    if sharpen:
        img_out = img_out.filter(ImageFilter.UnsharpMask(radius=0.5, percent=80, threshold=1))
    
    return img_out


def _make_squircle_mask(size: int, n: float = 3.8) -> Image.Image:
    """Crea una máscara cuadrada redondeada (superelipse).
    
    La famosa formita de los iconos de Apple
    """
    mask = Image.new("L", (size, size), 0)
    pixels = mask.load()
    
    for y in range(size):
        v = (2.0 * y) / (size - 1) - 1.0
        for x in range(size):
            u = (2.0 * x) / (size - 1) - 1.0
            if (abs(u) ** n + abs(v) ** n) <= 1.0:
                pixels[x, y] = 255
    
    return mask


def _apply_squircle(img: Image.Image, size: int, n: float = 3.8) -> Image.Image:
    """Aplica máscara squircle a una imagen redimensionada."""
    mask = _make_squircle_mask(size, n)
    resized = img.resize((size, size), Image.Resampling.LANCZOS)
    
    out = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    out.paste(resized, (0, 0), mask)
    return out


def _load_image_from_source(source: str | Path, fallback_dir: Path = None) -> Image.Image | None:
    """Carga una imagen desde URL o ruta local.
    
    Args:
        source: URL (http/https) o ruta local
        fallback_dir: Directorio donde buscar si source falla
        
    Returns:
        Image en RGBA o None si no se pudo cargar
    """
    if isinstance(source, str) and source.startswith("http"):
        try:
            import urllib.request
            resp = urllib.request.urlopen(source, timeout=10)
            data = resp.read()
            
            # Detectar SVG
            if b"<svg" in data or source.lower().endswith('.svg'):
                try:
                    import cairosvg
                    png_bytes = cairosvg.svg2png(bytestring=data)
                    return Image.open(io.BytesIO(png_bytes)).convert("RGBA")
                except Exception:
                    logger.exception(f"Error convirtiendo SVG a PNG desde {source}")
                    return None
            else:
                return Image.open(io.BytesIO(data)).convert("RGBA")
        except Exception as e:
            logger.exception(f"Error descargando imagen de {source}: {e}")
            return None
    
    # Cargar desde ruta local
    source_path = Path(source) if source else None
    if source_path and source_path.exists():
        try:
            return Image.open(source_path).convert("RGBA")
        except Exception as e:
            logger.exception(f"Error abriendo imagen local {source_path}: {e}")
            return None
    
    return None


def _save_icon(icon_img: Image.Image | None, tmp_dir: Path):
    """Genera y guarda el icono del pase en @2x y 1x."""
    if icon_img is None:
        icon_img = _load_image_from_source(_find_fallback("icon.png", _get_assets_dir()))
    
    if icon_img is None:
        # Crear placeholder
        placeholder = Image.new("RGBA", (58, 58), (40, 40, 40, 255))
        placeholder = _apply_squircle(placeholder, 58, n=3.8)
        placeholder.save(tmp_dir / "icon@2x.png")
        placeholder.resize((29, 29), Image.Resampling.LANCZOS).save(tmp_dir / "icon.png")
        logger.warning("Se generó icono placeholder")
        return
    
    # Procesar icono real
    icon_2x = _resize_with_upscaling(icon_img, 58, sharpen=False)
    icon_2x = _apply_squircle(icon_2x, 58, n=3.8)
    icon_2x.save(tmp_dir / "icon@2x.png")
    
    icon_1x = _resize_with_upscaling(icon_img, 29, sharpen=True)
    icon_1x = _apply_squircle(icon_1x, 29, n=3.8)
    icon_1x.save(tmp_dir / "icon.png")


def _save_logo(logo_img: Image.Image | None, tmp_dir: Path):
    """Genera y guarda el logo del pase."""
    if logo_img is None:
        logo_img = _load_image_from_source(_find_fallback("logo.png", _get_assets_dir()))
    
    if logo_img is None:
        logger.warning("No se encontró logo, usando icono como fallback")
        return
    
    # Canvas estándar de Apple: 320x100 para @2x
    canvas_2x = Image.new("RGBA", (320, 100), (0, 0, 0, 0))
    logo_scaled = logo_img.copy()
    logo_scaled.thumbnail((300, 85), Image.Resampling.LANCZOS)
    
    y_offset = (100 - logo_scaled.height) // 2
    canvas_2x.paste(logo_scaled, (0, y_offset), logo_scaled)
    canvas_2x.save(tmp_dir / "logo@2x.png")
    canvas_2x.resize((160, 50), Image.Resampling.LANCZOS).save(tmp_dir / "logo.png")


def _save_strip(strip_path: str | Path, tmp_dir: Path):
    """Genera y guarda el strip (banner) del pase."""
    strip_path = Path(strip_path)
    if not strip_path.exists():
        logger.warning(f"Strip no encontrado en {strip_path}")
        return
    
    try:
        img = Image.open(strip_path).convert("RGBA")
        
        # Dimensiones de Apple (@2x)
        target_w, target_h = 1125, 369
        img_ratio = img.width / img.height
        target_ratio = target_w / target_h
        
        # Calcular tamaño para cubrir
        if img_ratio > target_ratio:
            new_h = target_h
            new_w = int(target_h * img_ratio)
        else:
            new_w = target_w
            new_h = int(target_w / img_ratio)
        
        img_resized = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        
        # Recorte centrado
        left = (new_w - target_w) / 2
        top = (new_h - target_h) / 2
        right = (new_w + target_w) / 2
        bottom = (new_h + target_h) / 2
        
        strip_final = img_resized.crop((left, top, right, bottom))
        strip_final.save(tmp_dir / "strip@2x.png")
        strip_final.resize((375, 123), Image.Resampling.LANCZOS).save(tmp_dir / "strip.png")
    except Exception as e:
        logger.exception(f"Error procesando strip: {e}")


def _get_assets_dir() -> Path:
    """Obtiene el directorio de assets configurado."""
    return Path(getattr(pk, "PASSKIT_ASSETS_DIR", Path(pk.BASE_DIR) / "staticfiles" / "img"))


def _find_fallback(filename: str, search_dir: Path) -> str | None:
    """Busca un archivo en el directorio de fallbacks."""
    candidates = [
        search_dir / filename,
        search_dir / "gpul.png",
        search_dir / "hackudc.png",
    ]
    
    for path in candidates:
        if path.exists():
            return str(path)
    
    return None


def generate_pass_assets(tmp_dir: Path):
    """Genera todos los assets necesarios para el pase."""
    style = pk.PASSKIT_STYLE
    assets_dir = _get_assets_dir()
    
    # Icono
    icon_source = style.get("ICON")
    icon_img = _load_image_from_source(icon_source, assets_dir)
    _save_icon(icon_img, tmp_dir)
    
    # Logo
    logo_source = style.get("LOGO")
    logo_img = _load_image_from_source(logo_source, assets_dir)
    _save_logo(logo_img, tmp_dir)
    
    # Strip
    strip_path = style.get("STRIP", assets_dir / "strip.png")
    _save_strip(strip_path, tmp_dir)


# ============================================================================
# GENERACIÓN DEL PASE
# ============================================================================
def generate_pass(persona: Persona, skip_cert_check: bool = False) -> PassResult:
    """Genera el archivo .pkpass y el QR para una Persona.
    
    Args:
        persona: Instancia de Persona para la cual generar el pase
        skip_cert_check: Si True, solo genera QR sin firmar el pase (para testing)
        
    Returns:
        PassResult con pkpass (bytes), qr_png (bytes) y acreditacion (str)
        
    Raises:
        RuntimeError: Si wallet no está instalado o hay error de certificados
    """
    if not EventTicket:
        raise RuntimeError("La librería 'wallet-py3k' no está instalada")

    acreditacion = getattr(persona, "acreditacion", "")

    with tempfile.TemporaryDirectory() as tmp_str:
        tmp_dir = Path(tmp_str)
        
        # Generar assets (icono, logo, strip)
        generate_pass_assets(tmp_dir)

        # Generar QR
        qr_buffer = io.BytesIO()
        qrcode.make(persona.correo).save(qr_buffer, format="PNG")
        qr_bytes = qr_buffer.getvalue()

        # Si solo queremos el QR, retornar sin firmar
        if skip_cert_check:
            logger.info(f"Modo skip_cert_check: solo QR para {persona.correo}")
            return PassResult(pkpass=b"", qr_png=qr_bytes, acreditacion=acreditacion)

        # Construir el pase
        ticket = EventTicket()
        context = build_substitution_context(persona)
        
        # Añadir campos procesados
        for area, campos_config in pk.PASSKIT_FIELDS.items():
            method_name = f"add{area.capitalize()}Field"
            if hasattr(ticket, method_name):
                method = getattr(ticket, method_name)
                processed = process_fields(campos_config, context, area)
                for field in processed:
                    # Para campos con URLs, usar el formato especial de wallet
                    if field.get("is_link"):
                        # wallet-py3k interpreta URLs automáticamente si comienzan con http
                        method(field["key"], field["value"], field["label"])
                    else:
                        method(field["key"], field["value"], field["label"])

        # Configuración del pase
        auth = pk.PASSKIT_AUTH
        event_info = pk.PASSKIT_EVENT
        style = pk.PASSKIT_STYLE

        pass_obj = Pass(
            ticket,
            passTypeIdentifier=auth["PASS_TYPE_ID"],
            organizationName=event_info["ORG"],
            teamIdentifier=auth["TEAM_ID"]
        )
        
        pass_obj.serialNumber = persona.correo
        pass_obj.description = event_info["DESC"]
        pass_obj.foregroundColor = style["FG_COLOR"]
        pass_obj.backgroundColor = style["BG_COLOR"]
        pass_obj.labelColor = style["LABEL_COLOR"]
        pass_obj.barcode = Barcode(message=persona.correo, format=BarcodeFormat.QR)
        
        if event_info.get("DATE"):
            pass_obj.relevantDate = event_info["DATE"].isoformat()
        if event_info.get("LOCATION"):
            pass_obj.locations = [event_info["LOCATION"]]

        # Añadir imágenes
        for img_file in tmp_dir.glob("*.png"):
            with open(img_file, "rb") as f:
                pass_obj.addFile(img_file.name, f)

        # Firmar el pase
        cert_pem, key_pem = extract_p12_certificates(auth["P12_PATH"], auth["P12_PASSWORD"], tmp_dir)
        wwdr_pem = ensure_wwdr_pem(auth["WWDR_CERT"], tmp_dir)

        pkpass_buffer = io.BytesIO()
        pass_obj.create(cert_pem, key_pem, wwdr_pem, "", zip_file=pkpass_buffer)
        pkpass_bytes = pkpass_buffer.getvalue()

    return PassResult(pkpass=pkpass_bytes, qr_png=qr_bytes, acreditacion=acreditacion)


def save_pass(persona: Persona, destination: Path | None = None, skip_cert_check: bool = False) -> SavePassResult:
    """Genera y guarda un pase .pkpass y QR en disco.
    
    Estructura de directorios:
    - destination/pkpass/  → Archivos .pkpass
    - destination/qr/      → Imágenes QR
    
    Args:
        persona: Instancia de Persona
        destination: Carpeta base (si None, usa 'passkit' dentro del proyecto)
        skip_cert_check: Si True, solo genera QR sin firmar
        
    Returns:
        SavePassResult con rutas de pkpass_path y qr_path
        
    Raises:
        Exception: Si hay error durante la generación o guardado
    """
    # Usar 'passkit' como carpeta base si no se especifica destination
    # BASE_DIR es el directorio del backend
    base_dir = Path(destination) if destination else Path(pk.BASE_DIR) / "passkit"
    pkpass_dir = base_dir / "pkpass"
    qr_dir = base_dir / "qr"
    
    # Crear directorios si no existen
    pkpass_dir.mkdir(parents=True, exist_ok=True)
    qr_dir.mkdir(parents=True, exist_ok=True)

    try:
        result = generate_pass(persona, skip_cert_check)
        
        # Nombre seguro basado en correo
        safe_email = persona.correo.replace("@", "_").replace(".", "_")
        pkpass_path = pkpass_dir / f"{safe_email}.pkpass"
        qr_path = qr_dir / f"{safe_email}.qr.png"
        
        if result.pkpass:
            pkpass_path.write_bytes(result.pkpass)
            logger.info(f"Pase guardado: {pkpass_path}")
        else:
            logger.warning(f"No se generó pkpass para {persona.correo} (skip_cert_check=True)")
        
        qr_path.write_bytes(result.qr_png)
        logger.info(f"QR guardado: {qr_path}")
        
        return SavePassResult(pkpass_path=pkpass_path, qr_path=qr_path)
    except Exception as e:
        logger.exception(f"Error guardando pase para {persona.correo}")
        raise