from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("api/menu/productos/", views.api_productos, name="api_productos"),
]
