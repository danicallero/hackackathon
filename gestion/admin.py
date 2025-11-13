# Copyright (C) 2025-now  p.fernandezf <p@fernandezf.es> & iago.rivas <delthia@delthia.com>

from django.contrib import admin, messages
from django.utils import timezone
from django.utils.translation import ngettext

from gestion.models import (
    Mentor,
    Participante,
    Pase,
    Patrocinador,
    Presencia,
    RestriccionAlimentaria,
    TipoPase,
    Token,
)


@admin.action(permissions=["aceptar"])
def aceptar_participante(modeladmin, request, queryset):
    if not request.user.has_perm("gestion.aceptar_participante"):
        modeladmin.message_user(
            request, "No tienes permiso para realizar esta acción", messages.ERROR
        )
        return

    verificados = queryset.filter(fecha_verificacion_correo__isnull=False)
    no_verificados = queryset.filter(fecha_verificacion_correo__isnull=True)

    ya_aceptados = verificados.filter(fecha_aceptacion__isnull=False).count()
    actualizados = verificados.filter(fecha_aceptacion__isnull=True).update(
        fecha_aceptacion=timezone.now()
    )

    if no_verificados.exists():
        modeladmin.message_user(
            request,
            ngettext(
                "%d participante no tiene el correo verificado y no se ha podido aceptar.",
                "%d participantes no tienen el correo verificado y no se han podido aceptar.",
                no_verificados.count(),
            )
            % no_verificados.count(),
            messages.ERROR,
        )

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


class EstadoParticipanteListFilter(admin.SimpleListFilter):
    title = "Estado"
    parameter_name = "estado"

    def lookups(self, request, model_admin):
        return [
            ("registrado", "Registrado (sin verificar correo)"),
            ("error_verificacion", "Error de verificación del correo"),
            ("verificado", "Correo verificado"),
            ("aceptado", "Aceptado"),
            ("confirmado", "Plaza confirmada"),
            ("rechazo", "Plaza rechazada"),
        ]

    def queryset(self, request, queryset):
        match self.value():
            case "registrado":
                return queryset.filter(
                    fecha_registro__isnull=False,
                    motivo_error_correo_verificacion__isnull=True,
                    fecha_verificacion_correo__isnull=True,
                    fecha_aceptacion__isnull=True,
                    fecha_confirmacion_plaza__isnull=True,
                    fecha_rechazo_plaza__isnull=True,
                )
            case "error_verificacion":
                return queryset.filter(
                    fecha_registro__isnull=False,
                    motivo_error_correo_verificacion__isnull=False,
                    fecha_verificacion_correo__isnull=True,
                    fecha_aceptacion__isnull=True,
                    fecha_confirmacion_plaza__isnull=True,
                    fecha_rechazo_plaza__isnull=True,
                )
            case "verificado":
                return queryset.filter(
                    fecha_registro__isnull=False,
                    fecha_verificacion_correo__isnull=False,
                    fecha_aceptacion__isnull=True,
                    fecha_confirmacion_plaza__isnull=True,
                    fecha_rechazo_plaza__isnull=True,
                )
            case "aceptado":
                return queryset.filter(
                    fecha_registro__isnull=False,
                    fecha_verificacion_correo__isnull=False,
                    fecha_aceptacion__isnull=False,
                    fecha_confirmacion_plaza__isnull=True,
                    fecha_rechazo_plaza__isnull=True,
                )
            case "confirmado":
                return queryset.filter(
                    fecha_registro__isnull=False,
                    fecha_verificacion_correo__isnull=False,
                    fecha_aceptacion__isnull=False,
                    fecha_confirmacion_plaza__isnull=False,
                    fecha_rechazo_plaza__isnull=True,
                )
            case "rechazo":
                return queryset.filter(
                    fecha_registro__isnull=False,
                    fecha_verificacion_correo__isnull=False,
                    fecha_aceptacion__isnull=False,
                    fecha_rechazo_plaza__isnull=False,
                )


class TokenValidoListFilter(admin.SimpleListFilter):
    title = "Validez"
    parameter_name = "validez"

    def lookups(self, request, model_admin):
        return [
            ("valido", "Válido"),
            ("expirado", "Expirado"),
        ]

    def queryset(self, request, queryset):
        match self.value():
            case "valido":
                return queryset.filter(fecha_expiracion__gte=timezone.now())
            case "expirado":
                return queryset.filter(fecha_expiracion__lt=timezone.now())


class ParticipanteAdmin(admin.ModelAdmin):
    fieldsets = [
        (
            "Personal",
            {
                "fields": [
                    "nombre",
                    "correo",
                    "genero",
                    "fecha_nacimiento",
                    "ciudad",
                    "telefono",
                    "dni",
                    "cv",
                    "compartir_cv",
                ]
            },
        ),
        (
            "Estudios",
            {
                "fields": [
                    "nivel_estudio",
                    "nombre_estudio",
                    "centro_estudio",
                    "curso",
                    "quiere_creditos",
                ]
            },
        ),
        (
            "Evento",
            {
                "fields": [
                    "acreditacion",
                    "restricciones_alimentarias",
                    "detalle_restricciones_alimentarias",
                    "talla_camiseta",
                    "fecha_registro",
                    "fecha_verificacion_correo",
                    "fecha_aceptacion",
                    "fecha_confirmacion_plaza",
                    "fecha_rechazo_plaza",
                    "motivo_error_correo_verificacion",
                    "motivacion",
                    "notas",
                ]
            },
        ),
    ]

    readonly_fields = [
        "cv",
        "fecha_registro",
        "fecha_verificacion_correo",
        "fecha_aceptacion",
        "fecha_confirmacion_plaza",
        "fecha_rechazo_plaza",
        "motivo_error_correo_verificacion",
    ]

    list_display = [
        "correo",
        "nombre",
        "nombre_estudio",
        "centro_estudio",
        "ciudad",
        "quiere_creditos",
        "fecha_registro",
        "verificado",
        "aceptado",
        "confirmado",
        "rechazo",
        "error_verificacion",
    ]
    list_filter = [EstadoParticipanteListFilter, "centro_estudio", "ciudad"]
    actions = [aceptar_participante]

    def change_view(self, request, object_id, form_url="", extra_context=None):
        # Permiso para ver el CV
        if not request.user.has_perm("gestion.ver_cv_participante"):
            personal = self.fieldsets[0][1]["fields"]
            if "cv" in personal:
                personal.remove("cv")

        # Permiso para ver DNI y teléfono
        if not request.user.has_perm("gestion.ver_dni_telefono_participante"):
            personal = self.fieldsets[0][1]["fields"]
            if "dni" in personal:
                personal.remove("dni")
            if "telefono" in personal:
                personal.remove("telefono")

        return super(ParticipanteAdmin, self).change_view(
            request, object_id, form_url, extra_context
        )

    def has_aceptar_permission(self, request):
        return request.user.has_perm("gestion.aceptar_participante")


class TokenAdmin(admin.ModelAdmin):
    fields = [
        "token",
        "tipo",
        "persona",
        "fecha_creacion",
        "fecha_expiracion",
        "fecha_uso",
    ]
    readonly_fields = [
        "token",
        "fecha_creacion",
    ]

    radio_fields = {"tipo": admin.HORIZONTAL}

    list_display = [
        "persona",
        "tipo",
        "fecha_creacion",
        "valido",
    ]
    list_filter = [
        "tipo",
        TokenValidoListFilter,
    ]

    search_fields = [
        "persona__nombre",
        "persona__correo",
        "token",
    ]


# Register your models here.
admin.site.register(Patrocinador)
admin.site.register(Mentor)
admin.site.register(Participante, ParticipanteAdmin)
admin.site.register(RestriccionAlimentaria)
admin.site.register(Presencia)
admin.site.register(TipoPase)
admin.site.register(Pase)
admin.site.register(Token, TokenAdmin)
