from django.urls import path

from . import views

app_name = "pedidos"

urlpatterns = [
    path("pedidos/crear/", views.crear_pedido, name="crear_pedido"),
    path("pedidos/<int:pedido_id>/confirmacion/", views.confirmacion, name="confirmacion"),
]
