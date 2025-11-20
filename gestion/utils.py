# Copyright (C) 2025-now  p.fernandezf <p@fernandezf.es> & iago.rivas <delthia@delthia.com>

import logging
from datetime import datetime, timedelta

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone

from gestion.models import Persona, Token

logger = logging.getLogger(__name__)


def enviar_correo_verificacion(
    persona: Persona, fecha_expiracion: datetime | None
) -> int:
    """
    Envía la verificación de correo a la Persona indicada.
    Si la Persona tiene un token válido lo reutiliza, modificando la fecha de expiración.
    En caso contrario, crea uno nuevo.

    Argumentos:
        persona: `Persona` a la que enviar el correo.
        fecha_expiracion: Fecha de expiración del token de confirmación (Opcional).

    Salida:
        0: Envío correcto.
        1: Error en el envío.
    """

    token = Token.objects.filter(
        persona=persona, tipo="VERIFICACION", fecha_uso__isnull=True
    ).first()
    if not token:
        token = Token(persona=persona, tipo="VERIFICACION")

    if not fecha_expiracion:
        fecha_expiracion = (
            (timezone.now() + timedelta(days=7))
            .astimezone(timezone.get_default_timezone())
            .replace(hour=23, minute=59, second=59)
        )

    token.fecha_expiracion = fecha_expiracion
    token.save()

    params = {
        "nombre": persona.nombre,
        "token": token.token,
        "host": settings.HOST_REGISTRO,
    }
    email = EmailMultiAlternatives(
        settings.EMAIL_VERIFICACION_ASUNTO,
        render_to_string("correo/verificacion_correo.txt", params),
        to=(persona.correo,),
        reply_to=("hackudc@gpul.org",),
        headers={"Message-ID": f"hackudc-{token.fecha_creacion.timestamp()}"},
    )
    email.attach_alternative(
        render_to_string("correo/verificacion_correo.html", params), "text/html"
    )

    try:
        email.send(fail_silently=False)

    except Exception as e:
        persona.motivo_error_correo_verificacion = str(e)[:4096]
        persona.save()

        logger.error("Error al enviar el correo de verificación:")
        logger.error(e, stack_info=True, extra={"correo": persona.correo})

        return 1

    logger.info("Correo de verificación enviado", extra={"correo": persona.correo})
    return 0


def enviar_correo_confirmacion(
    persona: Persona, fecha_expiracion: datetime | None
) -> int:
    """
    Envía la confirmación de plaza a la Persona indicada.
    Si la Persona tiene un token válido lo reutiliza, modificando la fecha de expiración.
    En caso contrario, crea uno nuevo.

    Argumentos:
        persona: `Persona` a la que enviar el correo.
        fecha_expiracion: Fecha de expiración del token de confirmación (Opcional).

    Salida:
        0: Envío correcto.
        1: Error en el envío.
    """
    token = Token.objects.filter(
        persona=persona, tipo="CONFIRMACION", fecha_uso__isnull=True
    ).first()
    if not token:
        token = Token(persona=persona, tipo="CONFIRMACION")

    if not fecha_expiracion:
        fecha_expiracion = (
            (timezone.now() + timedelta(days=7))
            .astimezone(timezone.get_default_timezone())
            .replace(hour=23, minute=59, second=59)
        )

    token.fecha_expiracion = fecha_expiracion
    token.save()

    params = {
        "nombre": persona.nombre,
        "token": token.token,
        "expiracion": fecha_expiracion,
        "host": settings.HOST_REGISTRO,
    }
    email = EmailMultiAlternatives(
        settings.EMAIL_CONFIRMACION_ASUNTO,
        render_to_string("correo/confirmacion_plaza.txt", params),
        to=(persona.correo,),
        reply_to=("hackudc@gpul.org",),
        headers={"Message-ID": f"hackudc-{token.fecha_creacion.timestamp()}"},
    )
    email.attach_alternative(
        render_to_string("correo/confirmacion_plaza.html", params),
        "text/html",
    )
    try:
        email.send(fail_silently=False)
    except ConnectionRefusedError as e:
        logger.error(f"Error en el envío del correo de confirmación:")
        logger.error(e, stack_info=True, extra={"correo": persona.correo})

        return 1

    logger.info("Correo de confirmación enviado", extra={"correo": persona.correo})
    return 0
