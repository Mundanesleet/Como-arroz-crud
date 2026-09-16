from django.contrib import admin

from .models import LineaPedido, Pedido, PuntoRecogida


class LineaPedidoInline(admin.TabularInline):
    model = LineaPedido
    extra = 0
    readonly_fields = ("producto", "variante", "nombre_producto", "nombre_variante", "precio_unitario", "subtotal")


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = (
        "id", "cliente_nombre", "tipo_pedido", "metodo_pago",
        "estado_pago", "estado_pedido", "total", "fecha",
    )
    list_filter = ("tipo_pedido", "metodo_pago", "estado_pago", "estado_pedido")
    search_fields = ("cliente_nombre", "cliente_telefono")
    inlines = [LineaPedidoInline]
    readonly_fields = ("subtotal", "total", "fecha", "creado_en", "actualizado_en")


@admin.register(PuntoRecogida)
class PuntoRecogidaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "direccion", "activo", "orden")
    list_editable = ("orden", "activo")
