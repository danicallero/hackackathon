from django.db import migrations

from hackudc.constantes import RESTRICCIONES_ALIMENTARIAS


def agregar_restricciones_alimentarias(apps, schema_editor):
    RestriccionAlimentaria = apps.get_model("hackudc", "RestriccionAlimentaria")
    for _, nombre in RESTRICCIONES_ALIMENTARIAS:
        RestriccionAlimentaria.objects.get_or_create(nombre=nombre)


class Migration(migrations.Migration):

    dependencies = [
        ("hackudc", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(agregar_restricciones_alimentarias),
    ]
