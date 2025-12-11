# Copyright (C) 2025-now  p.fernandezf <p@fernandezf.es> & iago.rivas <delthia@delthia.com>

import logging
from datetime import datetime, timedelta

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.core.management import BaseCommand, CommandError
from django.template.loader import render_to_string
from django.utils import timezone

from gestion.models import Participante, Token


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = (
        "Envía un correo de confirmación a los participantes aceptados no confirmados"
    )

    def add_arguments(self, parser):
        grupo_fecha_expiracion = parser.add_mutually_exclusive_group()
        grupo_fecha_expiracion.add_argument(
            "-d",
            "--dias",
            help="Días de duración del token. (default=14)",
            type=int,
            default=14,
        )
        grupo_fecha_expiracion.add_argument(
            "-e",
            "--expiracion",
            help="Fecha de expiración para todos los tokens. Formato ISO 8601.",
        )

    def handle(self, *args, **options):
        dias = options.get("dias")
        expiracion = options.get("expiracion")
        if expiracion:
            fecha_expiracion = datetime.fromisoformat(expiracion).astimezone(
                timezone.get_current_timezone()
            )
        else:
            fecha_expiracion = timezone.now() + timedelta(days=dias)

        if fecha_expiracion < timezone.now():
            raise ValueError("La fecha de expiración es anterior a este instante")

        # Participantes aceptados pero sin confirmar la plaza
        participantes = Participante.objects.filter(
            fecha_aceptacion__isnull=False,
            fecha_confirmacion_plaza__isnull=True,
            fecha_rechazo_plaza__isnull=True,
        )

        participantes_con_token = Token.objects.filter(
            tipo="CONFIRMACION", persona__in=participantes
        )
        if participantes_con_token.exists():
            self.stdout.write(
                self.style.ERROR(
                    f"{participantes_con_token.count()} participantes ya tenían un token de confirmación"
                )
            )

        for participante in participantes:
            token = Token(
                tipo="CONFIRMACION",
                persona=participante,
                fecha_expiracion=fecha_expiracion.astimezone(
                    timezone.get_default_timezone()
                ).replace(hour=23, minute=59, second=59),
            )
            token.save()

            try:
                params = {
                    "nombre": participante.nombre,
                    "token": token.token,
                    "expiracion": fecha_expiracion,
                    "host": settings.HOST_REGISTRO,
                }
                email = EmailMultiAlternatives(
                    settings.EMAIL_CONFIRMACION_ASUNTO,
                    render_to_string("correo/confirmacion_plaza.txt", params),
                    to=(participante.correo,),
                    reply_to=("hackudc@gpul.org",),
                    headers={
                        "Message-ID": f"hackudc-{token.fecha_creacion.timestamp()}"
                    },
                )
                email.attach_alternative(
                    render_to_string("correo/confirmacion_plaza.html", params),
                    "text/html",
                )
                email.send(fail_silently=False)
            except ConnectionRefusedError as e:
                logger.error(f"Error en el envío del correo de confirmación:")
                logger.error(e, stack_info=True, extra={"correo": participante.correo})
                self.stdout.write(
                    self.style.ERROR(
                        f"Error al mandar el correo a {participante.correo}"
                    )
                )
                break
            self.stdout.write(
                self.style.SUCCESS(f"Mensaje enviado a {participante.correo}")
            )
