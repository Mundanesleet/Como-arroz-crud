from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from config.mixins import PanelStaffRequiredMixin, usuario_es_administrador

from .forms import PuntoRecogidaForm
from .models import Pedido, PuntoRecogida


class PuntoRecogidaListView(PanelStaffRequiredMixin, ListView):
    model = PuntoRecogida
    template_name = "panel/punto_list.html"
    context_object_name = "puntos"
    queryset = PuntoRecogida.objects.all().order_by("orden", "nombre")


class PuntoRecogidaCreateView(PanelStaffRequiredMixin, CreateView):
    model = PuntoRecogida
    form_class = PuntoRecogidaForm
    template_name = "panel/punto_form.html"
    success_url = reverse_lazy("pedidos_panel:punto_list")

    def form_valid(self, form):
        messages.success(self.request, f'Punto de recogida "{form.instance.nombre}" creado.')
        return super().form_valid(form)


class PuntoRecogidaUpdateView(PanelStaffRequiredMixin, UpdateView):
    model = PuntoRecogida
    form_class = PuntoRecogidaForm
    template_name = "panel/punto_form.html"
    success_url = reverse_lazy("pedidos_panel:punto_list")

    def form_valid(self, form):
        messages.success(self.request, f'Punto de recogida "{form.instance.nombre}" actualizado.')
        return super().form_valid(form)


class PuntoRecogidaDeleteView(PanelStaffRequiredMixin, DeleteView):
    model = PuntoRecogida
    template_name = "panel/confirm_delete.html"
    success_url = reverse_lazy("pedidos_panel:punto_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["titulo"] = f'¿Eliminar el punto de recogida "{self.object.nombre}"?'
        context["cancel_url"] = self.success_url
        return context

    def form_valid(self, form):
        messages.success(self.request, "Punto de recogida eliminado.")
        return super().form_valid(form)


# ---------------------------------------------------------------------------
# PEDIDOS Y PAGOS
# ---------------------------------------------------------------------------

class PedidoListView(PanelStaffRequiredMixin, ListView):
    model = Pedido
    template_name = "panel/pedido_list.html"
    context_object_name = "pedidos"
    paginate_by = 30

    def get_queryset(self):
        qs = Pedido.objects.all().order_by("-fecha")
        estado_pago = self.request.GET.get("estado_pago")
        estado_pedido = self.request.GET.get("estado_pedido")
        if estado_pago:
            qs = qs.filter(estado_pago=estado_pago)
        if estado_pedido:
            qs = qs.filter(estado_pedido=estado_pedido)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["estados_pago"] = Pedido.EstadoPago.choices
        context["estados_pedido"] = Pedido.EstadoPedido.choices
        context["estado_pago_seleccionado"] = self.request.GET.get("estado_pago", "")
        context["estado_pedido_seleccionado"] = self.request.GET.get("estado_pedido", "")
        return context


@user_passes_test(usuario_es_administrador, login_url="panel_login")
def pedido_detail(request, pk):
    pedido = get_object_or_404(Pedido, pk=pk)

    if request.method == "POST":
        accion = request.POST.get("accion")

        if accion == "confirmar_pago":
            pedido.estado_pago = Pedido.EstadoPago.CONFIRMADO
            pedido.verificado_por = request.user
            pedido.verificado_en = timezone.now()
            pedido.save(update_fields=["estado_pago", "verificado_por", "verificado_en"])
            messages.success(request, f"Pago del pedido #{pedido.id} confirmado.")

        elif accion == "rechazar_pago":
            pedido.estado_pago = Pedido.EstadoPago.RECHAZADO
            pedido.verificado_por = request.user
            pedido.verificado_en = timezone.now()
            pedido.save(update_fields=["estado_pago", "verificado_por", "verificado_en"])
            messages.warning(request, f"Pago del pedido #{pedido.id} rechazado.")

        elif accion == "marcar_pagado":
            pedido.estado_pago = Pedido.EstadoPago.PAGADO
            pedido.verificado_por = request.user
            pedido.verificado_en = timezone.now()
            pedido.save(update_fields=["estado_pago", "verificado_por", "verificado_en"])
            messages.success(request, f"Pedido #{pedido.id} marcado como pagado.")

        return redirect(reverse("pedidos_panel:pedido_detail", args=[pedido.pk]))

    return render(request, "panel/pedido_detail.html", {"pedido": pedido})
