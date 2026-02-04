# Copyright (C) 2026-now  danicallero <hola@danicallero.es>

import os
from pathlib import Path
from django.conf import settings

BASE_DIR = Path(settings.BASE_DIR)

# --- Certificates (Environment) ---
PASSKIT_AUTH = {
    "TEAM_ID": os.getenv("PASSKIT_TEAM_ID"),
    "PASS_TYPE_ID": os.getenv("PASSKIT_PASS_TYPE_ID"),
    "P12_PATH": os.getenv("PASSKIT_CERT_P12_PATH"),
    "P12_PASSWORD": os.getenv("PASSKIT_CERT_P12_PASSWORD"),
    "WWDR_CERT": os.getenv("PASSKIT_WWDR_CERT_PATH"),
}

# --- Event Info ---
PASSKIT_EVENT = {
    "ORG": "GPUL - HackUDC 2026",
    "NAME": "HackUDC 2026",
    "DESC": "HackUDC 2026 - Pase de acceso al evento",
    "DATE": getattr(settings, 'FECHA_INICIO_EVENTO', None),
    "LOCATION": {
        "latitude": 43.3332,
        "longitude": -8.4115,
        "relevantText": "Presenta este pase en la entrada del evento."
    }
}

# --- Visuals ---
PASSKIT_STYLE = {
    "FG_COLOR": "rgb(255, 255, 255)",
    "BG_COLOR": "rgb(40, 40, 40)",
    "LABEL_COLOR": "rgb(255, 255, 255)",
    # Puedes usar una URL pública (SVG/PNG) o una ruta local. Si es una URL, el generador
    # descargará y convertirá el SVG automáticamente (requiere 'cairosvg' instalado).
    "ICON": "https://hackudc.gpul.org/_astro/gpul-small.DA8wWUJz_1LQhtY.svg",
    "LOGO": BASE_DIR / "staticfiles/img/logo_w@2x.png",
}

# --- Pass Fields Structure ---
PASSKIT_FIELDS = {
    "header": [{"key": "hour", "label": "{hora}", "value": "{fecha}"}],
    "primary": [],
    "secondary": [
        {"key": "name", "label": "Nombre", "value": "{nombre}"},
        {"key": "role", "label": "Rol", "value": "{rol}"},
    ],
    "auxiliary": [{"key": "email", "label": "Correo", "value": "{correo}"}],
    "back": [
        {"key": "event_info", "label": "Evento", "value": PASSKIT_EVENT["NAME"]},
        {"key": "loc", "label": "Ubicación", "value": "Facultade de Informática, UDC, A Coruña"},
        {"key": "entry_info", "label": "Información de Entrada", "value": "Presenta este pase cuando hagas el check-in."},
        {"key": "terms", "label": "Términos y Condiciones", "value": "https://hackudc.gpul.org/terms"},
        {"key": "web_link", "label": "Más Información", "value": "https://live.hackudc.gpul.org"},
        {"key": "gpul", "label": "Organizado por", "value": "Grupo de Programadores y Usuarios de Linux (GPUL)"},
    ]
}

# --- Assets & Debug ---
PASSKIT_ASSETS_DIR = str(BASE_DIR / "staticfiles" / "img")
PASSKIT_DEBUG_DIR = str(BASE_DIR / "passkit")

# Directorios de salida configurables
# - `PASSKIT_PKPASS_DIR`: donde se guardan los .pkpass para su envío
# - `PASSKIT_QR_DIR`: carpeta `qr` donde se colocan los QR (p.ej. para adjuntar a correos)
# Ambos pueden configurarse vía variables de entorno si es necesario
PASSKIT_PKPASS_DIR = os.getenv("PASSKIT_PKPASS_DIR", str(Path(PASSKIT_DEBUG_DIR) / "pkpasses"))
PASSKIT_QR_DIR = os.getenv("PASSKIT_QR_DIR", str(Path(PASSKIT_DEBUG_DIR) / "qr"))