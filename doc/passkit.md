# Configuración de PassKit (Apple Wallet)

## Resumen

El sistema genera pases personalizados de Apple Wallet con QR que contiene el correo del participante. Los pases se nombran usando el correo electrónico del usuario y se pueden generar de forma masiva o individual.

## Requisitos previos

1. **Cuenta de Apple Developer**
2. **Pass Type ID** registrado en Apple Developer
3. **Certificados de firma**:
   - Certificado de Pass Type ID (exportado como .p12)
   - Certificado WWDR (Apple Worldwide Developer Relations)
4. **Dependencias Python**
   - `wallet-py3k` (módulo `wallet`)
   - `qrcode`
   - `Pillow`
   - `cairosvg`

## Setup inicial en Apple Developer

### 1. Crear Pass Type ID

1. Ve a [Certificates, Identifiers & Profiles](https://developer.apple.com/account/resources/identifiers/list/passTypeId)
2. Crea un nuevo **Pass Type ID**
   - Identificador: `pass.org.gpul.hackudc` (ejemplo)
   - Descripción: `HackUDC Check-in Pass`

### 2. Generar certificado

1. En el Pass Type ID, crea un **Certificate**
2. Sigue el asistente para generar un CSR desde Keychain Access (macOS)
3. Descarga el certificado generado (`pass.cer`)
4. Descarga también el certificado **WWDR** (G4) desde la [página de certificados de Apple](https://www.apple.com/certificateauthority/)

## Preparar certificados para producción

### Opción A: Usar P12 (recomendado)

```bash
# En macOS con Keychain Access:
# 1. Importa pass.cer en Keychain
# 2. Busca el certificado y su clave privada
# 3. Selecciona ambos → Exportar → formato .p12
# 4. Establece una contraseña

# El .p12 contiene certificado + clave privada
```

### Opción B: Usar PEM (solo si necesitas verificar manualmente)

> El backend usa el .p12 y extrae el PEM internamente con OpenSSL.
> Si quieres comprobar certificados a mano, puedes convertirlos con OpenSSL.

## Despliegue en servidor

### 1. Crear estructura de directorios

```bash
# Como root o con sudo
sudo mkdir -p /etc/hackudc/certs
sudo chown debian:debian /etc/hackudc/certs
sudo chmod 700 /etc/hackudc/certs
```

### 2. Copiar certificados

```bash
# Desde tu máquina local
scp pass.p12 AppleWWDRCAG4.cer servidor:/etc/hackudc/certs/

# En el servidor
sudo chmod 600 /etc/hackudc/certs/*
sudo chown debian:debian /etc/hackudc/certs/*
```

### 3. Configurar `.env`

```bash
# En /ruta/proyecto/.env
PASSKIT_TEAM_ID=ABCD1234XY
PASSKIT_PASS_TYPE_ID=pass.org.gpul.hackudc
PASSKIT_CERT_P12_PATH=/etc/hackudc/certs/pass.p12
PASSKIT_CERT_P12_PASSWORD=tu_password_del_p12
PASSKIT_WWDR_CERT_PATH=/etc/hackudc/certs/AppleWWDRCAG4.cer
```

### 4. Personalizar el pase

La configuración del diseño y campos del pase se encuentra en:
[backend/gestion/passkit_config.py](backend/gestion/passkit_config.py)

Edita este archivo para personalizar:
- Colores y estilo visual
- Campos mostrados en el pase (nombre, rol, correo, etc.)
- Imágenes (icono, logo, banner/strip)
- Ubicación del evento (coordenadas GPS)
- Fecha y hora del evento (usa `FECHA_INICIO_EVENTO` de `.env`)

## Uso del comando para generar pases

El comando unificado `generar_pases` permite generar pases de forma masiva o individual:

### Generar pase para un correo específico

```bash
./manage.py generar_pases --correo usuario@example.com
```

### Generar pases para todos los correos de la base de datos

```bash
./manage.py generar_pases --todos
```

### Opciones adicionales

```bash
# Ver qué se generaría sin hacerlo realmente
./manage.py generar_pases --todos --dry-run

# Guardar en una carpeta específica
./manage.py generar_pases --todos --destino /ruta/custom

# Generar solo QR sin firmar (útil para testing sin certificados)
./manage.py generar_pases --correo test@test.com --skip-cert-check
```

> Nota: con `--skip-cert-check` solo se genera el QR y **no** se guarda el `.pkpass`, que sería inútil sin certificados porque las apps de Wallet no lo aceptarían.

### Nombres de archivos

Los pases se guardan con el formato:
- `correo_usuario_com.pkpass` - Archivo del pase
- `correo_usuario_com.qr.png` - Imagen del código QR

Por ejemplo, para `test@example.com`:
- `test_example_com.pkpass`
- `test_example_com.qr.png`

## Estructura de archivos

```
backend/
├── gestion/
│   ├── passkit_config.py       # Configuración del pase (EDITAR AQUÍ)
│   ├── pkpass.py               # Código de generación
│   └── management/commands/
│       └── generar_pases.py         # Generación de pases
└── passkit/
   ├── pkpass/     ← Archivos .pkpass (si no se usa --destino)
   └── qr/         ← Imágenes QR (.qr.png)
```

## Características del pase

- **QR Code**: Contiene el correo electrónico del participante
- **Fecha formateada**: Formato en español (ej: "6 de Febrero de 2026, 18:00h")
- **Ubicación GPS**: Notifica cuando el usuario está cerca del evento
- **Campos personalizables**:
  - Nombre del participante
  - Rol (Hacker, Mentor, Sponsor)
  - Correo electrónico
  - Ubicación del evento
- **Diseño customizable**: Colores, logos, banner

## Personalización

### Colores y textos

Edita [backend/gestion/passkit_config.py](backend/gestion/passkit_config.py):

```python
PASSKIT_STYLE = {
   "FG_COLOR": "rgb(255, 255, 255)",
   "BG_COLOR": "rgb(40, 40, 40)",
   "LABEL_COLOR": "rgb(255, 255, 255)",
   "ICON": "https://.../icon.svg",  # URL o ruta local
   "LOGO": BASE_DIR / "staticfiles/img/logo_w@2x.png",
}

PASSKIT_EVENT = {
   "ORG": "GPUL",
   "NAME": "HackUDC 2026",
   "DESC": "HackUDC 2026 - Entrada al evento",
   "DATE": getattr(settings, "FECHA_INICIO_EVENTO", None),
   "LOCATION": {
      "latitude": 43.3332,
      "longitude": -8.4115,
      "relevantText": "Facultade de Informática, UDC",
   },
}
```

### Campos del pase

En [backend/gestion/passkit_config.py](backend/gestion/passkit_config.py), personaliza `PASSKIT_FIELDS`:

```python
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
   ],
}
```

Variables disponibles: `{nombre}`, `{correo}`, `{dni}`, `{rol}`, `{fecha_completa}`, `{hora}`, `{fecha}`

### Nota sobre assets

Si no se encuentra un icono o logo, se intentará usar `icon.png` / `logo.png`
en `staticfiles/img/`. El banner/strip usa `strip.png` si existe.

## Uso

### Generación

```bash
# Generar pase para una persona existente (requiere certificados)
./manage.py generar_pases --correo persona@ejemplo.com

# Solo QR sin certificados (no genera .pkpass)
./manage.py generar_pases --correo persona@ejemplo.com --skip-cert-check

# Guardar en carpeta específica
./manage.py generar_pases --correo persona@ejemplo.com --destino /tmp/passes
```

### Uso programático (ejemplo)

```python
from gestion.pkpass import save_pass, SavePassResult
from gestion.models import Persona

persona = Persona.objects.get(correo="usuario@example.com")
result: SavePassResult = save_pass(persona)
# result.pkpass_path -> Path al .pkpass
# result.qr_path -> Path al PNG del QR

# Adjuntar a correo (ejemplo):
email.attach_file(str(result.pkpass_path), mimetype="application/vnd.apple.pkpass")
email.attach_file(str(result.qr_path), mimetype="image/png")
```

> Nota: `save_pass(..., skip_cert_check=True)` generará solo el QR y no escribirá `.pkpass`.

### Variables de entorno (recapitulación)

Ejemplo de variables mínimas necesarias en `.env`:

```bash
# Obligatorias
PASSKIT_TEAM_ID=ABCD1234XY
PASSKIT_PASS_TYPE_ID=pass.org.gpul.hackudc
PASSKIT_WWDR_CERT_PATH=/etc/hackudc/certs/AppleWWDRCAG4.cer
```

Puedes proporcionar las credenciales por **P12** o **PEM**:

# Opción A - P12
```bash
PASSKIT_CERT_P12_PATH=/etc/hackudc/certs/pass.p12
PASSKIT_CERT_P12_PASSWORD=tu_password_del_p12
```

# Opción B - PEM
```bash
PASSKIT_CERT_PATH=/etc/hackudc/certs/pass.pem
PASSKIT_KEY_PATH=/etc/hackudc/certs/pass-key.pem
PASSKIT_CERT_PASSWORD=  # solo si la clave privada tiene contraseña
```

> El backend extrae automáticamente los PEM desde el `.p12` usando OpenSSL si se proporciona `PASSKIT_CERT_P12_PATH`.

## Troubleshooting

### Error: "Faltan variables de PassKit"

Verifica que en `.env` estén definidas:
- `PASSKIT_TEAM_ID`
- `PASSKIT_PASS_TYPE_ID`

### Error: "Falta PASSKIT_WWDR_CERT_PATH"

Necesitas el certificado WWDR de Apple. Descárgalo de:
https://www.apple.com/certificateauthority/

### Error al firmar el pase

1. Verifica permisos de los archivos de certificados
2. Comprueba que el certificado no haya expirado
3. Verifica que el TEAM_ID y PASS_TYPE_ID coincidan con los del certificado

```bash
# Verificar certificado dentro del .p12
openssl pkcs12 -in /etc/hackudc/certs/pass.p12 -clcerts -nokeys -passin pass:TU_PASS | openssl x509 -text -noout | grep -A2 "Subject:"

# Verificar fechas de validez
openssl pkcs12 -in /etc/hackudc/certs/pass.p12 -clcerts -nokeys -passin pass:TU_PASS | openssl x509 -dates -noout
```

### El pase no se muestra correctamente en Wallet

1. Verifica que las imágenes (icon.png, logo.png) existan en `staticfiles/img/`
2. Comprueba los colores (deben ser formato `rgb(r,g,b)`)
3. Revisa que los campos tengan valores válidos

## Seguridad

⚠️ **IMPORTANTE:**

1. **Nunca subas certificados a ningún repositorio**
   - Añade `*.pem`, `*.p12`, `*.cer` a `.gitignore`
   
2. **Permisos restrictivos en servidor**
   ```bash
   chmod 600 /etc/hackudc/certs/*
   ```

3. **Usuario correcto**
   - Los certificados deben pertenecer al usuario que ejecuta Django (ej: `debian`)

4. **Backup de certificados**
   - Guarda copias seguras de los certificados y claves privadas
   - Si pierdes la clave privada, tendrás que generar un nuevo certificado

## Referencias

- [PassKit Package Format Reference](https://developer.apple.com/documentation/walletpasses/creating-the-source-for-a-pass)
- [Apple Developer - Passes](https://developer.apple.com/wallet/)
- [wallet-py3k (PyPI)](https://pypi.org/project/wallet-py3k/)
