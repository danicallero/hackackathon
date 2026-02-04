# Copyright (C) 2026-now  danicallero <hola@danicallero.es>

from pathlib import Path

from django.core.management.base import BaseCommand

from gestion.models import Persona
from gestion.pkpass import save_pass


class Command(BaseCommand):
    help = "Genera pases de Apple Wallet de forma masiva o individual"

    def add_arguments(self, parser):
        parser.add_argument(
            "--correo",
            help="Generar pase solo para este correo específico",
        )
        parser.add_argument(
            "--todos",
            action="store_true",
            help="Generar pases para todos los correos de la base de datos",
        )
        parser.add_argument(
            "--destino",
            help="Carpeta donde guardar los .pkpass (default=./passkit/pkpasses)",
        )
        parser.add_argument(
            "--skip-cert-check",
            action="store_true",
            help="Solo genera el QR sin firmar el pase (útil para testing)",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Muestra qué pases se generarían sin generarlos realmente",
        )

    def handle(self, *args, **options):
        correo = options.get("correo")
        todos = options.get("todos")
        destino = options.get("destino")
        skip_cert_check = options.get("skip_cert_check")
        dry_run = options.get("dry_run")

        destino_path = Path(destino) if destino else None

        if not correo and not todos:
            self.stdout.write(
                self.style.ERROR(
                    "Debes especificar --correo o --todos"
                )
            )
            return

        if correo:
            # Generar pase individual
            try:
                persona = Persona.objects.get(correo=correo)
            except Persona.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f"No existe persona con correo: {correo}")
                )
                return

            if dry_run:
                self.stdout.write(
                    self.style.SUCCESS(f"Se generaría pase para: {persona.correo}")
                )
            else:
                result = save_pass(
                    persona, destination=destino_path, skip_cert_check=skip_cert_check
                )
                self.stdout.write(
                    self.style.SUCCESS(
                        f"✓ Pase generado para {persona.correo}\n"
                        f"  PKPass: {result.pkpass_path}\n"
                        f"  QR:     {result.qr_path}"
                    )
                )

        elif todos:
            # Generar pases para todos los correos
            personas = Persona.objects.all()
            total = personas.count()

            if total == 0:
                self.stdout.write(
                    self.style.WARNING("No hay personas en la base de datos")
                )
                return

            self.stdout.write(
                self.style.SUCCESS(f"Generando pases para {total} personas...")
            )

            if dry_run:
                for persona in personas:
                    self.stdout.write(f"  - {persona.correo}")
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Se generarían {total} pases (modo dry-run)"
                    )
                )
                return

            exitosos = 0
            errores = 0

            for i, persona in enumerate(personas, 1):
                try:
                    result = save_pass(
                        persona, destination=destino_path, skip_cert_check=skip_cert_check
                    )
                    exitosos += 1
                    self.stdout.write(
                        f"[{i}/{total}] ✓ {persona.correo}\n"
                        f"           PKPass: {result.pkpass_path.name}\n"
                        f"           QR:     {result.qr_path.name}"
                    )
                except Exception as e:
                    errores += 1
                    self.stdout.write(
                        self.style.ERROR(
                            f"[{i}/{total}] ✗ {persona.correo}: {str(e)}"
                        )
                    )

            self.stdout.write("")
            self.stdout.write(
                self.style.SUCCESS(
                    f"Completado: {exitosos} exitosos, {errores} errores"
                )
            )
