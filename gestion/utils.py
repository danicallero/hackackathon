# Copyright (C) 2025-now  p.fernandezf <p@fernandezf.es> & iago.rivas <delthia@delthia.com>

import logging
from datetime import timedelta

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone

from gestion.models import Persona, Token

logger = logging.getLogger(__name__)


def enviar_correo_verificacion(persona: Persona) -> int:
    """
    Envía la verificación de correo a la Persona indicada.
    Si la Persona tiene un token válido lo reutiliza, modificando la fecha de expiración.
    En caso contrario, crea uno nuevo

    Argumentos:
        persona: `Persona` a la que reenviar el correo

    Salida:
        0: Envío correcto
        1: Error en el envío
    """

    token = Token.objects.filter(persona=persona, tipo="VERIFICACION").first()
    if not token:
        token = Token(persona=persona, tipo="VERIFICACION")

    token.fecha_expiracion = (
        (timezone.now() + timedelta(days=7))
        .astimezone(timezone.get_default_timezone())
        .replace(hour=23, minute=59, second=59)
    )
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

    logger.info("Correo de verificación reenviado", extra={"correo": persona.correo})
    return 0
