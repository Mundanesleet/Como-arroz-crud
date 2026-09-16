from django.urls import path

from . import views_cocina as views

app_name = "cocina"

urlpatterns = [
    path("", views.cocina_lista, name="lista"),
    path("<int:pk>/avanzar/", views.cocina_avanzar, name="avanzar"),
]
