# Copyright (C) 2025-now  p.fernandezf <p@fernandezf.es> & iago.rivas <delthia@delthia.com>

import logging
from datetime import datetime, timedelta

from django.core.management import BaseCommand
from django.utils import timezone

from gestion.models import Participante, Token
from gestion.utils import enviar_correo_confirmacion

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
            fecha_expiracion = (timezone.now() + timedelta(days=dias)).replace(
                hour=23, minute=59, second=59
            )

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
                self.style.WARNING(
                    f"{participantes_con_token.count()} participantes ya tenían un token de confirmación"
                )
            )

            # # No enviar correo de confirmación a los usuarios a los que ya se les haya enviado
            # participantes.exclude(correo__in=participantes_con_token.values("correo"))

        for participante in participantes:
            estado = enviar_correo_confirmacion(participante, fecha_expiracion)
            if estado != 0:
                self.stdout.write(
                    self.style.ERROR(
                        f"Error al mandar el correo a {participante.correo}"
                    )
                )
                break

            self.stdout.write(
                self.style.HTTP_INFO(f"Mensaje enviado a {participante.correo}")
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    "Todos los correos de confirmación enviados correctamente"
                )
            )
