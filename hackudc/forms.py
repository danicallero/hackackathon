from django import forms

# from hackudc.constantes import GENEROS, NIVELES_ESTUDIO, TALLAS_CAMISETA
from hackudc.models import Participante, RestriccionAlimentaria


class ParticipanteForm(forms.ModelForm):
    class Meta:
        model = Participante
        fields = [
            "nombre",
            "correo",
            "dni",
            "genero",
            "restricciones_alimentarias",
            "telefono",
            "ano_nacimiento",
            "nivel_estudio",
            "nombre_estudio",
            "centro_estudio",
            "curso",
            "ciudad",
            "quiere_creditos",
            "talla_camiseta",
            "compartir_cv",
            "motivacion",
            "notas",
        ]

        labels = {
            "dni": "DNI",
            "genero": "Género",
            "restricciones_alimentarias": "Restricciones alimentarias",
            "ano_nacimiento": "Año de nacimiento",
            "nivel_estudio": "Nivel actual de estudios",
            "nombre_estudio": "Nombre de los estudios",
            "centro_estudio": "Centro de estudios",
            "curso": "Curso (si aplica)",
            "ciudad": "Ciudad de residencia",
            "quiere_creditos": "¿Quieres solicitar créditos?",
            "talla_camiseta": "Talla de camiseta",
            "compartir_cv": "¿Autorizas compartir tu CV con los patrocinadores?",
            "motivacion": "Motivación para participar en el HackUDC",
            "notas": "Notas",
        }

        help_texts = {
            "notas": "Otros datos que consideres relevantes (alergias, etc.).",
        }

        widgets = {
            # "genero": forms.Select(choices=GENEROS),
            "restricciones_alimentarias": forms.CheckboxSelectMultiple(),
            # "nivel_estudio": forms.Select(choices=NIVELES_ESTUDIO),
            # "talla_camiseta": forms.Select(choices=TALLAS_CAMISETA),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["restricciones_alimentarias"].queryset = (
            RestriccionAlimentaria.objects.all().order_by("id_restriccion")
        )
