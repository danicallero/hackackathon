from django.urls import path

from hackudc import views

urlpatterns = [
    path("", views.inicio, name="inicio"),
    path("registro", views.registro, name="registro"),
]
