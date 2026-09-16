from datetime import date
from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import redirect
from django.views.generic import TemplateView

from menu.models import Producto
from pedidos.models import Pedido

from .mixins import PanelStaffRequiredMixin, usuario_es_administrador, usuario_es_cocina


class PanelDashboardView(PanelStaffRequiredMixin, TemplateView):
    template_name = "panel/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        pedidos_hoy = Pedido.objects.filter(fecha__date=date.today())
        ventas_hoy = pedidos_hoy.exclude(
            estado_pedido=Pedido.EstadoPedido.CANCELADO,
        ).aggregate(total=Sum("total"))["total"] or Decimal("0")

        context["metricas"] = {
            "pendientes": Pedido.objects.filter(estado_pedido=Pedido.EstadoPedido.PENDIENTE).count(),
            "en_preparacion": Pedido.objects.filter(estado_pedido=Pedido.EstadoPedido.EN_PREPARACION).count(),
            "listos": Pedido.objects.filter(estado_pedido=Pedido.EstadoPedido.LISTO).count(),
            "pedidos_hoy": pedidos_hoy.count(),
            "ventas_hoy": ventas_hoy,
            "productos_activos": Producto.objects.filter(activo=True).count(),
            "productos_agotados": Producto.objects.filter(activo=True, agotado=True).count(),
            "pagos_por_verificar": Pedido.objects.filter(estado_pago=Pedido.EstadoPago.POR_VERIFICAR).count(),
        }
        return context


@login_required(login_url="panel_login")
def post_login_redirect(request):
    """El mismo login sirve para panel y cocina; aquí se decide a dónde va cada rol."""
    if usuario_es_administrador(request.user):
        return redirect("panel_dashboard")
    if usuario_es_cocina(request.user):
        return redirect("cocina:lista")
    return redirect("panel_login")
