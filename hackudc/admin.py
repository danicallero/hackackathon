from django.contrib import admin, messages
from django.utils.translation import ngettext

from hackudc.models import *


def aceptar_participante(modeladmin, request, queryset):
    ya_aceptados = sum(1 for _ in queryset.filter(aceptado=True))
    actualizados = queryset.update(aceptado=True) - ya_aceptados

    if ya_aceptados:
        modeladmin.message_user(
            request,
            ngettext(
                "%d participante ya estaba aceptado.",
                "%d participantes ya estaban aceptados.",
                ya_aceptados,
            )
            % ya_aceptados,
            messages.WARNING,
        )
    if actualizados:
        modeladmin.message_user(
            request,
            ngettext(
                "%d participante aceptado.", "%d participantes aceptados.", actualizados
            )
            % actualizados,
            messages.SUCCESS,
        )
    else:
        modeladmin.message_user(request, "No se ha aceptado a ningún participante.")


class ParticipanteAdmin(admin.ModelAdmin):
    list_display = [
        "correo",
        "nombre",
        "nombre_estudio",
        "centro_estudio",
        "ciudad",
        "quiere_creditos",
        "aceptado",
    ]
    list_filter = ["aceptado", "centro_estudio", "ciudad"]
    actions = [aceptar_participante]


# Register your models here.
admin.site.register(Patrocinador)
admin.site.register(Mentor)
admin.site.register(Participante, ParticipanteAdmin)
admin.site.register(RestriccionAlimentaria)
admin.site.register(Presencia)
admin.site.register(TipoPase)
admin.site.register(Pase)
