from django.urls import path

from . import views_panel as views

app_name = "pedidos_panel"

urlpatterns = [
    path("puntos-recogida/", views.PuntoRecogidaListView.as_view(), name="punto_list"),
    path("puntos-recogida/nuevo/", views.PuntoRecogidaCreateView.as_view(), name="punto_create"),
    path("puntos-recogida/<int:pk>/editar/", views.PuntoRecogidaUpdateView.as_view(), name="punto_update"),
    path("puntos-recogida/<int:pk>/eliminar/", views.PuntoRecogidaDeleteView.as_view(), name="punto_delete"),

    path("pedidos/", views.PedidoListView.as_view(), name="pedido_list"),
    path("pedidos/<int:pk>/", views.pedido_detail, name="pedido_detail"),
]
