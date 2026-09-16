from django.urls import path

from . import views_panel as views

app_name = "menu_panel"

urlpatterns = [
    path("categorias/", views.CategoriaListView.as_view(), name="categoria_list"),
    path("categorias/nueva/", views.CategoriaCreateView.as_view(), name="categoria_create"),
    path("categorias/<int:pk>/editar/", views.CategoriaUpdateView.as_view(), name="categoria_update"),
    path("categorias/<int:pk>/eliminar/", views.CategoriaDeleteView.as_view(), name="categoria_delete"),

    path("productos/", views.ProductoListView.as_view(), name="producto_list"),
    path("productos/nuevo/", views.producto_form, name="producto_create"),
    path("productos/<int:pk>/editar/", views.producto_form, name="producto_update"),
    path("productos/<int:pk>/eliminar/", views.ProductoDeleteView.as_view(), name="producto_delete"),

    path("combos/", views.ComboListView.as_view(), name="combo_list"),
    path("combos/nuevo/", views.ComboCreateView.as_view(), name="combo_create"),
    path("combos/<int:pk>/editar/", views.ComboUpdateView.as_view(), name="combo_update"),
    path("combos/<int:pk>/eliminar/", views.ComboDeleteView.as_view(), name="combo_delete"),
]
