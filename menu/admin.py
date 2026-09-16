from django.contrib import admin

from .models import Categoria, Combo, Producto, Variante


class VarianteInline(admin.TabularInline):
    model = Variante
    extra = 1


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "orden", "activa")
    list_editable = ("orden", "activa")
    prepopulated_fields = {"slug": ("nombre",)}


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "categoria", "activo", "orden")
    list_editable = ("orden", "activo")
    list_filter = ("categoria", "activo")
    search_fields = ("nombre",)
    inlines = [VarianteInline]


@admin.register(Combo)
class ComboAdmin(admin.ModelAdmin):
    list_display = ("nombre", "precio", "activo", "orden")
    list_editable = ("orden", "activo")
