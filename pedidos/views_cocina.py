from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from config.mixins import usuario_es_cocina

from .models import Pedido

cocina_required = user_passes_test(usuario_es_cocina, login_url="panel_login")

# (estado_actual) -> [(accion, estado_siguiente, tipo_pedido_requerido_o_None), ...]
TRANSICIONES = {
    Pedido.EstadoPedido.PENDIENTE: [("aceptar", Pedido.EstadoPedido.CONFIRMADO, None)],
    Pedido.EstadoPedido.CONFIRMADO: [("preparar", Pedido.EstadoPedido.EN_PREPARACION, None)],
    Pedido.EstadoPedido.EN_PREPARACION: [("listo", Pedido.EstadoPedido.LISTO, None)],
    Pedido.EstadoPedido.LISTO: [
        ("enviar", Pedido.EstadoPedido.EN_CAMINO, Pedido.TipoPedido.DOMICILIO),
        ("entregar", Pedido.EstadoPedido.ENTREGADO, Pedido.TipoPedido.RECOGER),
    ],
    Pedido.EstadoPedido.EN_CAMINO: [("entregar", Pedido.EstadoPedido.ENTREGADO, Pedido.TipoPedido.DOMICILIO)],
}

ETIQUETA_BOTON = {
    "aceptar": "Aceptar pedido",
    "preparar": "En preparación",
    "listo": "Marcar como listo",
    "enviar": "Enviar",
    "entregar": "Entregado",
}


def _pago_listo_para_cocina(pedido):
    """Transferencia debe estar confirmada antes de pasar a cocina;
    efectivo/tarjeta entran de inmediato (el pago se resuelve al entregar/recoger)."""
    if pedido.metodo_pago == Pedido.MetodoPago.TRANSFERENCIA:
        return pedido.estado_pago in (Pedido.EstadoPago.CONFIRMADO, Pedido.EstadoPago.PAGADO)
    return True


def _accion_disponible(pedido):
    opciones = TRANSICIONES.get(pedido.estado_pedido, [])
    for accion, _siguiente, tipo_requerido in opciones:
        if tipo_requerido is None or tipo_requerido == pedido.tipo_pedido:
            return accion, ETIQUETA_BOTON[accion]
    return None, None


@cocina_required
def cocina_lista(request):
    activos = (
        Pedido.objects.exclude(estado_pedido__in=[Pedido.EstadoPedido.ENTREGADO, Pedido.EstadoPedido.CANCELADO])
        .exclude(Q(metodo_pago=Pedido.MetodoPago.TRANSFERENCIA) & ~Q(estado_pago__in=[Pedido.EstadoPago.CONFIRMADO, Pedido.EstadoPago.PAGADO]))
        .prefetch_related("lineas")
        .order_by("fecha")
    )

    pedidos_con_accion = []
    for pedido in activos:
        accion, etiqueta = _accion_disponible(pedido)
        pedidos_con_accion.append({"pedido": pedido, "accion": accion, "etiqueta_boton": etiqueta})

    pendientes_pago = Pedido.objects.filter(
        metodo_pago=Pedido.MetodoPago.TRANSFERENCIA,
        estado_pago=Pedido.EstadoPago.POR_VERIFICAR,
    ).exclude(estado_pedido__in=[Pedido.EstadoPedido.ENTREGADO, Pedido.EstadoPedido.CANCELADO]).count()

    return render(request, "cocina/lista.html", {
        "pedidos_con_accion": pedidos_con_accion,
        "pendientes_pago": pendientes_pago,
    })


@cocina_required
def cocina_avanzar(request, pk):
    if request.method != "POST":
        return redirect("cocina:lista")

    pedido = get_object_or_404(Pedido, pk=pk)
    accion_solicitada = request.POST.get("accion")

    if not _pago_listo_para_cocina(pedido):
        messages.error(request, f"El pedido #{pedido.id} todavía no tiene el pago confirmado.")
        return redirect("cocina:lista")

    opciones = TRANSICIONES.get(pedido.estado_pedido, [])
    nuevo_estado = None
    for accion, siguiente, tipo_requerido in opciones:
        if accion == accion_solicitada and (tipo_requerido is None or tipo_requerido == pedido.tipo_pedido):
            nuevo_estado = siguiente
            break

    if not nuevo_estado:
        messages.error(request, f"No se pudo actualizar el pedido #{pedido.id}: acción inválida.")
        return redirect("cocina:lista")

    pedido.estado_pedido = nuevo_estado
    pedido.save(update_fields=["estado_pedido"])
    messages.success(request, f"Pedido #{pedido.id} → {pedido.get_estado_pedido_display()}.")

    return redirect("cocina:lista")
