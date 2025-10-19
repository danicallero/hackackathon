from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_not_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from hackudc.forms import EditarPresenciaForm, ParticipanteForm, PaseForm, Registro
from hackudc.models import Pase, Persona, Presencia, TipoPase


@login_not_required
@require_http_methods(["GET", "POST"])
def registro(request: HttpRequest):
    if request.method == "GET":
        return render(request, "registro.html", {"form": ParticipanteForm()})

    form = ParticipanteForm(request.POST, request.FILES)
    if form.is_valid():
        form.save()
        return HttpResponse("OK")
    else:
        return render(request, "registro.html", {"form": form})


def gestion(request: HttpRequest):
    return render(request, "gestion/index.html")


@require_http_methods(["GET", "POST"])
def alta(request: HttpRequest):
    """Check-in del evento. Asocia un participante a una acreditación

    1. Se devuelve la página con el formulario
    2. Petición post con el correo del participante. Devuelve los datos
    3. Petición post con el participante y la acreditación. Se asigna en la base de datos
    """
    # 1. Formulario de registro vacío
    if request.method == "GET":
        return render(request, "gestion/registro.html", {"form": Registro()})

    form = Registro(request.POST)

    if form.is_valid():
        datos = form.cleaned_data

        persona = Persona.objects.filter(correo=datos["correo"]).first()

        if not persona:
            messages.error(request, "No se encontró el participante")
            return redirect("alta")

        if persona.fecha_aceptacion is None:
            messages.error(request, "El participante no ha sido aceptado")
            return redirect("alta")

        if persona.acreditacion:
            messages.error(request, "El participante ya está registrado")
            return redirect("alta")

        # 2. Petición solo con el correo
        # Mostrar los datos y el formulario precompletado con el correo
        if not datos["acreditacion"]:
            messages.info(request, f"{persona.nombre} - {persona.talla_camiseta}")
            return render(request, "gestion/registro.html", {"form": form})

        # 3. Petición completa
        # Asignar la acreditación. Página de éxito con timeout y volver a la original
        persona.acreditacion = datos["acreditacion"]
        persona.save()

        messages.success(
            request,
            f"Asignada acreditación {persona.acreditacion} a {persona.correo}",
        )
        return redirect("alta")

    else:
        messages.error(request, "Datos incorrectos")
        return redirect("alta")


@require_http_methods(["GET", "POST"])
def pases(request: HttpRequest):
    """Pases del evento. Registra un pase y muestra si es la primera vez que ese participante utiliza ese pase"""

    if not (TipoPase.objects.filter(inicio_validez__lte=timezone.now()).exists()):
        messages.error(
            request, "No hay pases disponibles. Crea uno en el panel de administración."
        )
        return render(request, "gestion/pases.html", {"form": PaseForm()})

    if request.method == "GET":
        return render(request, "gestion/pases.html", {"form": PaseForm()})

    form = PaseForm(request.POST)

    if form.is_valid():
        datos = form.cleaned_data
        persona = Persona.objects.filter(acreditacion=datos["acreditacion"]).first()

        if persona:
            pase = Pase(persona=persona, tipo_pase=datos["tipo_pase"])
            pase.save()
            messages.success(request, f"Pase creado")
        else:
            messages.error(request, "No existe la acreditación")
    else:
        messages.error(request, "Datos incorrectos")

    return redirect("pases")


@require_http_methods(["GET"])
def presencia(request: HttpRequest, acreditacion: str = ""):
    if not acreditacion:
        return render(request, "gestion/presencia.html")

    persona = Persona.objects.filter(acreditacion=acreditacion).first()

    if not persona:
        messages.error(request, "No existe la acreditación")
        return redirect("presencia")

    presencias = Presencia.objects.filter(persona=persona).order_by("-entrada")

    tiempo_total = timedelta()
    for presencia in presencias:
        if presencia.entrada and presencia.salida:
            tiempo_total += presencia.salida - presencia.entrada

    tiempo_total = str(tiempo_total).split(".")[0]  # Remove microseconds

    if not presencias.exists():
        messages.warning(request, "No hay presencias registradas")

    presencias_sin_entrada = presencias.filter(entrada__isnull=True).exists()

    return render(
        request,
        "gestion/presencia.html",
        {
            "persona": persona,
            "presencias": presencias,
            "presencias_sin_entrada": presencias_sin_entrada,
            "tiempo_total": tiempo_total,
        },
    )


@require_http_methods(["GET"])
def presencia_entrada(request: HttpRequest, acreditacion: str):
    persona = Persona.objects.filter(acreditacion=acreditacion).first()
    if not persona:
        messages.error(request, "No existe la acreditación")
        return redirect("presencia")

    presencias = Presencia.objects.filter(persona=persona)
    ultima = presencias.order_by("-entrada").first()

    if not ultima:
        messages.error(request, "No había ninguna entrada")
    elif not ultima.salida:
        messages.warning(request, "No hay salida registrada de la última presencia")

    # Guardar entrada
    entrada = Presencia(persona=persona, entrada=timezone.now())
    entrada.save()

    return redirect("presencia", acreditacion=acreditacion)


@require_http_methods(["GET"])
def presencia_salida(request: HttpRequest, acreditacion: str):
    persona = Persona.objects.filter(acreditacion=acreditacion).first()
    if not persona:
        messages.error(request, "No existe la acreditación")
        return redirect("presencia")

    presencias = Presencia.objects.filter(persona=persona)
    ultima = presencias.order_by("-entrada").first()

    if not ultima:
        messages.error(request, "No había ninguna entrada")
    elif ultima.salida:
        messages.warning(request, "La última presencia ya tiene salida registrada")

    # Guardar salida
    ultima = Presencia(persona=persona, salida=timezone.now())
    ultima.save()

    return redirect("presencia", acreditacion=acreditacion)


@require_http_methods(["GET", "POST"])
def presencia_editar(request: HttpRequest, id_presencia: str):
    presencia = Presencia.objects.filter(id_presencia=id_presencia).first()
    if not presencia:
        messages.error(request, "No existe la presencia")
        return redirect("presencia")

    if request.method == "GET":
        return render(
            request,
            "gestion/editar_presencia.html",
            {"presencia": presencia, "form": EditarPresenciaForm(instance=presencia)},
        )

    # POST
    form = EditarPresenciaForm(request.POST, instance=presencia)
    if form.is_valid():
        form.save()
        messages.success(request, "Presencia actualizada")
    else:
        messages.error(request, "Datos incorrectos")

    return redirect("presencia", acreditacion=presencia.persona.acreditacion)
