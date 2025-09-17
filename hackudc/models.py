from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from hackudc.constantes import (
    GENEROS,
    NIVELES_ESTUDIO,
    TALLAS_CAMISETA,
    RESTRICCIONES_ALIMENTARIAS,
)


# Create your models here.
class Persona(models.Model):
    correo = models.EmailField(max_length=254, unique=True, primary_key=True)
    nombre = models.CharField(max_length=100)
    dni = models.CharField(max_length=9, unique=True, null=True, blank=True)
    genero = models.CharField(max_length=10, choices=GENEROS, null=True, blank=True)
    notas = models.TextField(null=True, blank=True)
    uuid = models.UUIDField(unique=True, null=True, blank=True, default=None)
    aceptado = models.BooleanField(default=False)

    restricciones_alimentarias = models.ManyToManyField(
        "RestriccionAlimentaria",
        blank=True,
        related_name="personas",
        db_table="persona_restriccion_alimentaria",
    )


class Patrocinador(Persona):
    empresa = models.CharField(max_length=100)

    class Meta:
        verbose_name = "Patrocinador"
        verbose_name_plural = "Patrocinadores"

    def __str__(self):
        return f"PATROCINADOR: {self.nombre} - {self.empresa}"


class Mentor(Persona):
    tamano_camiseta = models.CharField(
        max_length=10, choices=TALLAS_CAMISETA, null=True, blank=True
    )
    compartir_cv = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Mentor"
        verbose_name_plural = "Mentores"

    def __str__(self):
        return f"MENTOR: {self.nombre}"


class Participante(Persona):
    telefono = models.CharField(max_length=16, null=True, blank=True)
    ano_nacimiento = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[
            MinValueValidator(1970, "El año debe ser mayor o igual a 1970."),
            MaxValueValidator(2015, "El año debe ser menor o igual a 2015."),
        ],
    )
    nivel_estudio = models.CharField(
        null=True, blank=True, max_length=128, choices=NIVELES_ESTUDIO
    )
    nombre_estudio = models.CharField(max_length=128, null=True, blank=True)
    centro_estudio = models.CharField(max_length=128, null=True, blank=True)
    curso = models.CharField(max_length=128, null=True, blank=True)
    ciudad = models.CharField(max_length=128, null=True, blank=True)
    quiere_creditos = models.BooleanField(default=False)
    talla_camiseta = models.CharField(
        max_length=10, choices=TALLAS_CAMISETA, null=True, blank=True
    )
    motivacion = models.TextField(null=True, blank=True)
    compartir_cv = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Participante"
        verbose_name_plural = "Participantes"

    def __str__(self):
        return f"PARTICIPANTE: {self.nombre} ({'No aceptado' if not self.aceptado else 'Aceptado'})"


class RestriccionAlimentaria(models.Model):
    id_restriccion = models.AutoField(primary_key=True)
    nombre = models.CharField(
        max_length=100, unique=True, choices=RESTRICCIONES_ALIMENTARIAS
    )

    class Meta:
        verbose_name = "Restricción Alimentaria"
        verbose_name_plural = "Restricciones Alimentarias"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Presencia(models.Model):
    id_presencia = models.AutoField(primary_key=True)
    participante = models.ForeignKey(
        Participante, on_delete=models.CASCADE, related_name="tiempo_acceso"
    )
    fecha_entrada = models.DateTimeField()
    fecha_salida = models.DateTimeField()

    class Meta:
        verbose_name = "Presencia"
        verbose_name_plural = "Presencias"

        unique_together = ("participante", "fecha_entrada", "fecha_salida")

    def __str__(self):
        return f"Presencia de {self.participante.correo.nombre} desde {self.fecha_entrada} hasta {self.fecha_salida}"


class TipoPase(models.Model):
    id_tipo_pase = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100, unique=True)
    fecha_inicio_validez = models.DateTimeField()

    class Meta:
        verbose_name = "Tipo de Pase"
        verbose_name_plural = "Tipos de Pase"
        ordering = ["fecha_inicio_validez"]

    def __str__(self):
        return f"{self.nombre} (Desde {self.fecha_inicio_validez})"


class Pase(models.Model):
    id_pase = models.AutoField(primary_key=True)
    participante = models.ForeignKey(
        Participante, on_delete=models.CASCADE, related_name="pases"
    )
    tipo_pase = models.ForeignKey(
        TipoPase, on_delete=models.CASCADE, related_name="pases"
    )
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Pase"
        verbose_name_plural = "Pases"
        ordering = ["fecha"]

        unique_together = ("participante", "tipo_pase", "fecha")

    def __str__(self):
        return f"Pase '{self.tipo_pase}' de {self.participante.correo.nombre} - {self.tipo_pase.nombre} ({self.fecha})"
