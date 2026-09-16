import json

from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils.http import urlencode
from django.views.decorators.http import require_POST

from menu.models import Combo, Variante

from .models import LineaPedido, Pedido, PuntoRecogida

# Mismo número de contacto del negocio, reutilizado solo para que el cliente
# envíe el comprobante de transferencia — el pedido en sí NUNCA se hace por WhatsApp.
NUMERO_WHATSAPP_PAGOS = "573224047068"

PASOS_RECOGER = [
    ("recibido", "Recibido", "bi-receipt",
     {Pedido.EstadoPedido.PENDIENTE, Pedido.EstadoPedido.CONFIRMADO}),
    ("preparando", "Preparando", "bi-egg-fried",
     {Pedido.EstadoPedido.EN_PREPARACION}),
    ("listo", "Listo para recoger", "bi-bag-check",
     {Pedido.EstadoPedido.LISTO}),
    ("entregado", "Entregado", "bi-check-circle",
     {Pedido.EstadoPedido.ENTREGADO}),
]

PASOS_DOMICILIO = [
    ("recibido", "Recibido", "bi-receipt",
     {Pedido.EstadoPedido.PENDIENTE, Pedido.EstadoPedido.CONFIRMADO}),
    ("preparando", "Preparando", "bi-egg-fried",
     {Pedido.EstadoPedido.EN_PREPARACION, Pedido.EstadoPedido.LISTO}),
    ("camino", "En camino", "bi-scooter",
     {Pedido.EstadoPedido.EN_CAMINO}),
    ("entregado", "Entregado", "bi-check-circle",
     {Pedido.EstadoPedido.ENTREGADO}),
]


def _pasos_seguimiento(pedido):
    definicion = PASOS_RECOGER if pedido.tipo_pedido == Pedido.TipoPedido.RECOGER else PASOS_DOMICILIO

    indice_actual = None
    for indice, (_clave, _etiqueta, _icono, estados) in enumerate(definicion):
        if pedido.estado_pedido in estados:
            indice_actual = indice
            break

    pasos = []
    for indice, (clave, etiqueta, icono, _estados) in enumerate(definicion):
        if indice_actual is None:
            estado_visual = "pendiente"
        elif indice < indice_actual:
            estado_visual = "completado"
        elif indice == indice_actual:
            estado_visual = "activo"
        else:
            estado_visual = "pendiente"
        pasos.append({"clave": clave, "etiqueta": etiqueta, "icono": icono, "estado": estado_visual})
    return pasos


def _armar_lineas(carrito_raw):
    """Reconstruye cada línea desde la BD (nunca desde el precio que mande el navegador)."""
    lineas = []
    for item in carrito_raw:
        tipo = item.get("tipo")

        try:
            cantidad = int(item.get("cantidad"))
        except (TypeError, ValueError):
            cantidad = 0
        if cantidad <= 0:
            return None, "Hay una cantidad inválida en el carrito."

        if tipo == "producto":
            variante = (
                Variante.objects.filter(
                    pk=item.get("variante_id"),
                    activo=True,
                    producto_id=item.get("id"),
                    producto__activo=True,
                    producto__agotado=False,
                )
                .select_related("producto")
                .first()
            )
            if not variante:
                return None, "Uno de los productos del carrito ya no está disponible."

            variantes_activas = variante.producto.variantes.filter(activo=True).count()
            lineas.append({
                "producto": variante.producto,
                "variante": variante,
                "nombre_producto": variante.producto.nombre,
                "nombre_variante": variante.nombre if variantes_activas > 1 else "",
                "cantidad": cantidad,
                "precio_unitario": variante.precio,
            })

        elif tipo == "combo":
            combo = Combo.objects.filter(pk=item.get("id"), activo=True).first()
            if not combo:
                return None, "El combo del carrito ya no está disponible."

            lineas.append({
                "producto": None,
                "variante": None,
                "nombre_producto": combo.nombre,
                "nombre_variante": "",
                "cantidad": cantidad,
                "precio_unitario": combo.precio,
            })
        else:
            return None, "Hay una línea de pedido inválida en el carrito."

    return lineas, None


@require_POST
def crear_pedido(request):
    errores = []

    cliente_nombre = request.POST.get("cliente_nombre", "").strip()
    cliente_telefono = request.POST.get("cliente_telefono", "").strip()
    tipo_pedido = request.POST.get("tipo_pedido", "")
    metodo_pago = request.POST.get("metodo_pago", "")
    observaciones = request.POST.get("observaciones", "").strip()

    if not cliente_nombre:
        errores.append("Falta el nombre del cliente.")
    if not cliente_telefono:
        errores.append("Falta el teléfono del cliente.")
    if tipo_pedido not in Pedido.TipoPedido.values:
        errores.append("El tipo de pedido no es válido.")
    if metodo_pago not in Pedido.MetodoPago.values:
        errores.append("El método de pago no es válido.")

    direccion = barrio = referencia = ""
    punto_recogida = None

    if tipo_pedido == Pedido.TipoPedido.DOMICILIO:
        direccion = request.POST.get("direccion", "").strip()
        barrio = request.POST.get("barrio", "").strip()
        referencia = request.POST.get("referencia", "").strip()
        if not direccion or not barrio:
            errores.append("Para domicilio necesitamos la dirección y el barrio.")
    elif tipo_pedido == Pedido.TipoPedido.RECOGER:
        punto_recogida = PuntoRecogida.objects.filter(
            pk=request.POST.get("punto_recogida"), activo=True,
        ).first()
        if not punto_recogida:
            errores.append("Selecciona un punto de recogida válido.")

    if metodo_pago == Pedido.MetodoPago.TARJETA and tipo_pedido == Pedido.TipoPedido.DOMICILIO:
        errores.append("El pago con tarjeta solo está disponible para pedidos que se recogen en el restaurante.")

    comprobante = request.FILES.get("comprobante")

    try:
        carrito_raw = json.loads(request.POST.get("carrito", "[]"))
        if not isinstance(carrito_raw, list):
            raise ValueError
    except (json.JSONDecodeError, TypeError, ValueError):
        carrito_raw = []
        errores.append("El carrito llegó en un formato inválido.")
    else:
        if not carrito_raw:
            errores.append("Tu carrito está vacío.")

    if errores:
        return JsonResponse({"ok": False, "error": " ".join(errores)}, status=400)

    lineas, error_lineas = _armar_lineas(carrito_raw)
    if error_lineas:
        return JsonResponse({"ok": False, "error": error_lineas}, status=400)

    pedido = Pedido(
        cliente_nombre=cliente_nombre,
        cliente_telefono=cliente_telefono,
        tipo_pedido=tipo_pedido,
        direccion=direccion,
        barrio=barrio,
        referencia=referencia,
        punto_recogida=punto_recogida,
        metodo_pago=metodo_pago,
        observaciones=observaciones,
    )
    if comprobante:
        pedido.comprobante_pago = comprobante
    if metodo_pago == Pedido.MetodoPago.TRANSFERENCIA:
        # El comprobante es opcional: el cliente puede confirmarla por WhatsApp
        # en vez de subirlo aquí. De cualquier forma queda "por verificar"
        # hasta que el staff la confirme manualmente en el panel.
        pedido.estado_pago = Pedido.EstadoPago.POR_VERIFICAR

    try:
        pedido.full_clean(exclude=["subtotal", "total", "comprobante_pago"])
    except ValidationError as error:
        return JsonResponse({"ok": False, "error": " ".join(error.messages)}, status=400)

    pedido.save()

    for datos_linea in lineas:
        LineaPedido.objects.create(pedido=pedido, **datos_linea)

    pedido.recalcular_totales(guardar=True)

    return JsonResponse({
        "ok": True,
        "pedido_id": pedido.id,
        "redirect_url": reverse("pedidos:confirmacion", args=[pedido.id]),
    })


def confirmacion(request, pedido_id):
    pedido = get_object_or_404(Pedido, pk=pedido_id)

    whatsapp_pago_url = None
    if pedido.metodo_pago == Pedido.MetodoPago.TRANSFERENCIA and pedido.estado_pago == Pedido.EstadoPago.POR_VERIFICAR:
        mensaje = (
            f"Hola, quiero confirmar la transferencia de mi pedido #{pedido.id} "
            f"por ${pedido.total:.0f}. Les envío el comprobante:"
        )
        whatsapp_pago_url = f"https://wa.me/{NUMERO_WHATSAPP_PAGOS}?{urlencode({'text': mensaje})}"

    return render(request, "public/confirmacion.html", {
        "pedido": pedido,
        "pasos": _pasos_seguimiento(pedido),
        "whatsapp_pago_url": whatsapp_pago_url,
    })
