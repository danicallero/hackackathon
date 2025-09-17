from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from hackudc.forms import ParticipanteForm


# Create your views here.
def inicio(request: HttpRequest):
    return HttpResponse("Si")


@require_http_methods(["GET", "POST"])
def registro(request: HttpRequest):
    if request.method == "GET":
        return render(request, "registro.html", {"form": ParticipanteForm()})

    form = ParticipanteForm(request.POST)
    if form.is_valid():
        form.save()
        return HttpResponse("OK")
    else:
        return render(request, "registro.html", {"form": form})
