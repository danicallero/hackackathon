# Copyright (C) 2025-now  p.fernandezf <p@fernandezf.es> & iago.rivas <delthia@delthia.com>

from rest_framework import serializers

from gestion.models import (
    Pase,
    Persona,
    Presencia,
    RestriccionAlimentaria,
    TipoPase,
)


class RolPersonaMixin:
    rol = serializers.SerializerMethodField()

    def get_rol(self, obj: Persona) -> str:
        if hasattr(obj, "mentor"):
            return "Mentor"
        if hasattr(obj, "participante"):
            return "Hacker"
        return "Hacker"


class VerPersonaSerializer(RolPersonaMixin, serializers.ModelSerializer):
    restricciones_alimentarias = serializers.PrimaryKeyRelatedField(
        many=True, read_only=True
    )
    rol = serializers.SerializerMethodField()

    class Meta:
        model = Persona
        fields = [
            "correo",
            "nombre",
            "dni",
            "rol",
            "restricciones_alimentarias",
            "detalle_restricciones_alimentarias",
            "compartir_cv",
            "talla_camiseta",
            "fecha_registro",
            "fecha_verificacion_correo",
            "fecha_aceptacion",
            "fecha_confirmacion_plaza",
            "acreditacion",
            "notas",
        ]
        read_only_fields = [
            "fecha_registro",
            "fecha_verificacion_correo",
            "fecha_aceptacion",
            "fecha_confirmacion_plaza",
        ]


class AsignarAcreditacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Persona
        fields = ["correo", "acreditacion"]


class PersonaReducidaSerializer(RolPersonaMixin, serializers.ModelSerializer):
    rol = serializers.SerializerMethodField()

    class Meta:
        model = Persona
        fields = ["correo", "nombre", "acreditacion", "rol"]


class TipoPaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoPase
        fields = "__all__"
        # fields = ["id_tipo_pase", "nombre", "inicio_validez"]


class RestriccionAlimentariaSerializer(serializers.ModelSerializer):
    class Meta:
        model = RestriccionAlimentaria
        fields = ["id_restriccion", "nombre"]


class PaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pase
        fields = "__all__"
        # fields = ["id_pase", "fecha", "persona", "tipo_pase"]
        # depth = 1  # 0 = Solo PK


class PresenciaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Presencia
        fields = "__all__"
        # fields = ["id_presencia", "persona", "entrada", "salida"]
