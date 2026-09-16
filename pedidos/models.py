from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from menu.models import Producto, Variante


class PuntoRecogida(models.Model):
    nombre = models.CharField(max_length=80)
    direccion = models.CharField(max_length=200, blank=True)
    activo = models.BooleanField(default=True)
    orden = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["orden", "nombre"]
        verbose_name = "punto de recogida"
        verbose_name_plural = "puntos de recogida"

    def __str__(self):
        return self.nombre


class Pedido(models.Model):
    class TipoPedido(models.TextChoices):
        DOMICILIO = "domicilio", "Domicilio"
        RECOGER = "recoger", "Recoger en el restaurante"

    class MetodoPago(models.TextChoices):
        EFECTIVO = "efectivo", "Efectivo"
        TRANSFERENCIA = "transferencia", "Transferencia"
        TARJETA = "tarjeta", "Tarjeta"

    class EstadoPago(models.TextChoices):
        PENDIENTE = "pendiente", "Pendiente"
        POR_VERIFICAR = "por_verificar", "Por verificar"
        CONFIRMADO = "confirmado", "Confirmado"
        RECHAZADO = "rechazado", "Rechazado"
        PAGADO = "pagado", "Pagado"

    class EstadoPedido(models.TextChoices):
        PENDIENTE = "pendiente", "Pendiente"
        CONFIRMADO = "confirmado", "Confirmado"
        EN_PREPARACION = "en_preparacion", "En preparación"
        LISTO = "listo", "Listo"
        EN_CAMINO = "en_camino", "En camino"
        ENTREGADO = "entregado", "Entregado"
        CANCELADO = "cancelado", "Cancelado"

    fecha = models.DateTimeField(auto_now_add=True)

    cliente_nombre = models.CharField(max_length=120)
    cliente_telefono = models.CharField(max_length=20)

    tipo_pedido = models.CharField(max_length=15, choices=TipoPedido.choices)
    direccion = models.CharField(max_length=200, blank=True)
    barrio = models.CharField(max_length=100, blank=True)
    referencia = models.CharField(max_length=200, blank=True)
    punto_recogida = models.ForeignKey(
        PuntoRecogida, on_delete=models.PROTECT,
        null=True, blank=True, related_name="pedidos",
    )

    metodo_pago = models.CharField(max_length=15, choices=MetodoPago.choices)
    estado_pago = models.CharField(
        max_length=15, choices=EstadoPago.choices, default=EstadoPago.PENDIENTE,
    )
    comprobante_pago = models.ImageField(
        upload_to="comprobantes/", blank=True, null=True,
    )
    verificado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="pagos_verificados",
    )
    verificado_en = models.DateTimeField(null=True, blank=True)

    estado_pedido = models.CharField(
        max_length=15, choices=EstadoPedido.choices, default=EstadoPedido.PENDIENTE,
    )

    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0"))
    costo_domicilio = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0"))
    total = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0"))

    observaciones = models.TextField(blank=True)

    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-fecha"]

    def __str__(self):
        return f"Pedido #{self.pk}"

    def clean(self):
        if self.metodo_pago == self.MetodoPago.TARJETA and self.tipo_pedido == self.TipoPedido.DOMICILIO:
            raise ValidationError(
                "El pago con tarjeta solo está disponible para pedidos que se recogen en el restaurante."
            )

    def recalcular_totales(self, guardar=False):
        self.subtotal = sum((linea.subtotal for linea in self.lineas.all()), Decimal("0"))
        self.total = self.subtotal + self.costo_domicilio
        if guardar:
            self.save(update_fields=["subtotal", "total"])


class LineaPedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name="lineas")

    producto = models.ForeignKey(
        Producto, on_delete=models.SET_NULL, null=True, related_name="lineas_pedido",
    )
    variante = models.ForeignKey(
        Variante, on_delete=models.SET_NULL, null=True, blank=True, related_name="lineas_pedido",
    )

    # Snapshot: el pedido no debe cambiar si luego se edita o borra el producto/variante.
    nombre_producto = models.CharField(max_length=120)
    nombre_variante = models.CharField(max_length=60, blank=True)

    cantidad = models.PositiveIntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.cantidad} x {self.nombre_producto}"

    def save(self, *args, **kwargs):
        self.subtotal = self.precio_unitario * self.cantidad
        super().save(*args, **kwargs)
