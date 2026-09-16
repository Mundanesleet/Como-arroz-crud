from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView

from config.mixins import PanelStaffRequiredMixin, usuario_es_administrador

from .forms import ResetPasswordForm, UsuarioCreateForm, UsuarioEditForm


def _es_el_ultimo_administrador(usuario):
    """Solo cuentan otros administradores ACTIVOS: uno desactivado no sirve
    de respaldo real si este usuario se quita el rol."""
    otros_admins = (
        User.objects.filter(is_superuser=True, is_active=True).exclude(pk=usuario.pk).exists()
        or User.objects.filter(groups__name="Administrador", is_active=True).exclude(pk=usuario.pk).exists()
    )
    return not otros_admins


class UsuarioListView(PanelStaffRequiredMixin, ListView):
    model = User
    template_name = "panel/usuario_list.html"
    context_object_name = "usuarios_raw"
    queryset = User.objects.all().order_by("username")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        filas = []
        for usuario in context["usuarios_raw"]:
            if usuario.is_superuser:
                rol = "Superusuario"
            else:
                grupos = list(usuario.groups.values_list("name", flat=True))
                rol = grupos[0] if grupos else "Sin rol asignado"
            filas.append({"usuario": usuario, "rol": rol})
        context["filas"] = filas
        return context


class UsuarioCreateView(PanelStaffRequiredMixin, CreateView):
    model = User
    form_class = UsuarioCreateForm
    template_name = "panel/usuario_form.html"
    success_url = reverse_lazy("cuentas_panel:usuario_list")

    def form_valid(self, form):
        messages.success(self.request, f'Usuario "{form.instance.username}" creado.')
        return super().form_valid(form)


class UsuarioUpdateView(PanelStaffRequiredMixin, UpdateView):
    model = User
    form_class = UsuarioEditForm
    template_name = "panel/usuario_form.html"
    success_url = reverse_lazy("cuentas_panel:usuario_list")

    def get_initial(self):
        initial = super().get_initial()
        grupos = set(self.object.groups.values_list("name", flat=True))
        if "Administrador" in grupos:
            initial["rol"] = "Administrador"
        elif "Cocina" in grupos:
            initial["rol"] = "Cocina"
        return initial

    def form_valid(self, form):
        usuario = form.instance
        es_uno_mismo = usuario.pk == self.request.user.pk

        if es_uno_mismo and not form.cleaned_data.get("is_active", True):
            form.add_error("is_active", "No puedes desactivar tu propia cuenta.")
            return self.form_invalid(form)

        if es_uno_mismo and form.cleaned_data.get("rol") != "Administrador" and _es_el_ultimo_administrador(usuario):
            form.add_error("rol", "No puedes quitarte el rol de Administrador: eres el único.")
            return self.form_invalid(form)

        messages.success(self.request, f'Usuario "{usuario.username}" actualizado.')
        return super().form_valid(form)


@user_passes_test(usuario_es_administrador, login_url="panel_login")
def usuario_password(request, pk):
    usuario = get_object_or_404(User, pk=pk)

    if request.method == "POST":
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            usuario.set_password(form.cleaned_data["password1"])
            usuario.save(update_fields=["password"])
            messages.success(request, f'Contraseña de "{usuario.username}" actualizada.')
            return redirect("cuentas_panel:usuario_list")
    else:
        form = ResetPasswordForm()

    return render(request, "panel/usuario_password.html", {"form": form, "usuario": usuario})


@user_passes_test(usuario_es_administrador, login_url="panel_login")
def usuario_toggle_activo(request, pk):
    if request.method != "POST":
        return redirect("cuentas_panel:usuario_list")

    usuario = get_object_or_404(User, pk=pk)

    if usuario.pk == request.user.pk:
        messages.error(request, "No puedes desactivar tu propia cuenta.")
        return redirect("cuentas_panel:usuario_list")

    usuario.is_active = not usuario.is_active
    usuario.save(update_fields=["is_active"])
    estado = "activado" if usuario.is_active else "desactivado"
    messages.success(request, f'Usuario "{usuario.username}" {estado}.')
    return redirect("cuentas_panel:usuario_list")
