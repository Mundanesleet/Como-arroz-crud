from django.urls import path

from . import views_panel as views

app_name = "cuentas_panel"

urlpatterns = [
    path("usuarios/", views.UsuarioListView.as_view(), name="usuario_list"),
    path("usuarios/nuevo/", views.UsuarioCreateView.as_view(), name="usuario_create"),
    path("usuarios/<int:pk>/editar/", views.UsuarioUpdateView.as_view(), name="usuario_update"),
    path("usuarios/<int:pk>/contrasena/", views.usuario_password, name="usuario_password"),
    path("usuarios/<int:pk>/toggle/", views.usuario_toggle_activo, name="usuario_toggle"),
]
