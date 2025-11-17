# Copyright (C) 2025-now  p.fernandezf <p@fernandezf.es> & iago.rivas <delthia@delthia.com>

from django import forms
from django.utils import timezone

from gestion.models import Participante, Presencia, RestriccionAlimentaria, TipoPase


class ParticipanteForm(forms.ModelForm):
    class Meta:
        model = Participante
        fields = [
            # Datpos personales
            "nombre",
            "dni",
            "correo",
            "telefono",
            "fecha_nacimiento",
            "genero",
            "talla_camiseta",
            "ciudad",
            # Restricciones alimentarias
            "restricciones_alimentarias",
            "detalle_restricciones_alimentarias",
            # Estudios
            "nivel_estudio",
            "centro_estudio",
            "nombre_estudio",
            "curso",
            "quiere_creditos",
            # Otros
            "motivacion",
            "cv",
            "compartir_cv",
            "notas",
        ]

        labels = {
            "restricciones_alimentarias": "Restricciones alimentarias",
            "curso": "Curso (si aplica)",
            "quiere_creditos": "¿Quieres solicitar créditos?",
            "compartir_cv": "¿Autorizas compartir tu CV con los patrocinadores?",
            "motivacion": "Motivación para participar en el HackUDC",
        }

        help_texts = {
            "cv": "Currículum vitae en formato PDF. Lo usaremos para conocerte mejor y lo haremos llegar a nuestros patrocinadores si lo deseas.",
            "motivacion": "Se usará conjuntamente con el CV para aceptar las mejores inscripciones en caso de tener más solicitudes que plazas.",
            "notas": "Otros datos que consideres relevantes.",
            "quiere_creditos": "Para estudiantes de la UDC",
        }

        widgets = {
            "fecha_nacimiento": forms.DateInput(
                attrs={"type": "date"}, format="%Y-%m-%d"
            ),
            "restricciones_alimentarias": forms.CheckboxSelectMultiple(),
            "notas": forms.Textarea(attrs={"rows": 2}),
            "cv": forms.ClearableFileInput(attrs={"accept": ".pdf"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["restricciones_alimentarias"].queryset = (
            RestriccionAlimentaria.objects.all().order_by("id_restriccion")
        )

    class Media:
        css = {"all": ["css/registro.css"]}


class RevisarParticipanteForm(ParticipanteForm):
    class Meta(ParticipanteForm.Meta):
        exclude = [
            "cv",
            "notas",
        ]

    class Media(ParticipanteForm.Media):
        pass

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # for field_name in self.Meta.fields:
        #     if field_name not in self.Meta.exclude:
        #         field = self.fields[field_name]
        #         field.disabled = True


class Registro(forms.Form):
    persona = forms.CharField(label="Correo a registrar", max_length=100)
    acreditacion = forms.CharField(
        label="Acreditación a asignar", max_length=6, required=False
    )


# Necesario porque se accede a la persona por la acreditación
class PaseForm(forms.Form):
    tipo_pase = forms.ModelChoiceField(
        queryset=TipoPase.objects.all().order_by("inicio_validez")
    )
    acreditacion = forms.CharField(label="Acreditación", max_length=6)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["tipo_pase"].initial = (
            TipoPase.objects.filter(inicio_validez__lte=timezone.now())
            .order_by("-inicio_validez")
            .first()
        )


class EditarPresenciaForm(forms.ModelForm):
    class Meta:
        model = Presencia
        fields = ["entrada", "salida"]
        labels = {
            "entrada": "Hora de entrada",
            "salida": "Hora de salida",
        }
        widgets = {
            "entrada": forms.DateTimeInput(
                attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"
            ),
            "salida": forms.DateTimeInput(
                attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.entrada:
            self.fields["entrada"].disabled = True

        if self.instance and self.instance.salida:
            self.fields["salida"].disabled = True
