from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from config.mixins import PanelStaffRequiredMixin

from .forms import CategoriaForm, ComboForm, ProductoForm, VarianteFormSet
from .models import Categoria, Combo, Producto

# ---------------------------------------------------------------------------
# CATEGORÍAS
# ---------------------------------------------------------------------------

class CategoriaListView(PanelStaffRequiredMixin, ListView):
    model = Categoria
    template_name = "panel/categoria_list.html"
    context_object_name = "categorias"
    queryset = Categoria.objects.all().order_by("orden", "nombre")


class CategoriaCreateView(PanelStaffRequiredMixin, CreateView):
    model = Categoria
    form_class = CategoriaForm
    template_name = "panel/categoria_form.html"
    success_url = reverse_lazy("menu_panel:categoria_list")

    def form_valid(self, form):
        messages.success(self.request, f'Categoría "{form.instance.nombre}" creada.')
        return super().form_valid(form)


class CategoriaUpdateView(PanelStaffRequiredMixin, UpdateView):
    model = Categoria
    form_class = CategoriaForm
    template_name = "panel/categoria_form.html"
    success_url = reverse_lazy("menu_panel:categoria_list")

    def form_valid(self, form):
        messages.success(self.request, f'Categoría "{form.instance.nombre}" actualizada.')
        return super().form_valid(form)


class CategoriaDeleteView(PanelStaffRequiredMixin, DeleteView):
    model = Categoria
    template_name = "panel/confirm_delete.html"
    success_url = reverse_lazy("menu_panel:categoria_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["titulo"] = f'¿Eliminar la categoría "{self.object.nombre}"?'
        context["advertencia"] = "Esto también eliminará todos sus productos y variantes."
        context["cancel_url"] = self.success_url
        return context

    def form_valid(self, form):
        messages.success(self.request, "Categoría eliminada.")
        return super().form_valid(form)


# ---------------------------------------------------------------------------
# PRODUCTOS (con variantes en el mismo formulario)
# ---------------------------------------------------------------------------

class ProductoListView(PanelStaffRequiredMixin, ListView):
    model = Producto
    template_name = "panel/producto_list.html"
    context_object_name = "productos"
    paginate_by = 25

    def get_queryset(self):
        qs = Producto.objects.select_related("categoria").order_by("categoria__orden", "orden", "nombre")
        categoria_id = self.request.GET.get("categoria")
        if categoria_id:
            qs = qs.filter(categoria_id=categoria_id)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categorias"] = Categoria.objects.all().order_by("orden")
        context["categoria_seleccionada"] = self.request.GET.get("categoria", "")
        return context


class ProductoDeleteView(PanelStaffRequiredMixin, DeleteView):
    model = Producto
    template_name = "panel/confirm_delete.html"
    success_url = reverse_lazy("menu_panel:producto_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["titulo"] = f'¿Eliminar el producto "{self.object.nombre}"?'
        context["advertencia"] = "Esto también eliminará todas sus variantes."
        context["cancel_url"] = self.success_url
        return context

    def form_valid(self, form):
        messages.success(self.request, "Producto eliminado.")
        return super().form_valid(form)


def _panel_check(request):
    """Autorización manual para las vistas basadas en función (formset)."""
    return request.user.is_authenticated and request.user.is_staff


def producto_form(request, pk=None):
    if not _panel_check(request):
        return redirect(f"{reverse_lazy('panel_login')}?next={request.path}")

    producto = get_object_or_404(Producto, pk=pk) if pk else None

    if request.method == "POST":
        form = ProductoForm(request.POST, request.FILES, instance=producto)
        formset = VarianteFormSet(request.POST, instance=producto if producto else Producto())

        if form.is_valid() and formset.is_valid():
            producto_guardado = form.save()
            formset.instance = producto_guardado
            formset.save()
            messages.success(request, f'Producto "{producto_guardado.nombre}" guardado con sus variantes.')
            return redirect("menu_panel:producto_list")
    else:
        form = ProductoForm(instance=producto)
        formset = VarianteFormSet(instance=producto)

    return render(request, "panel/producto_form.html", {
        "form": form,
        "formset": formset,
        "producto": producto,
    })


# ---------------------------------------------------------------------------
# COMBOS
# ---------------------------------------------------------------------------

class ComboListView(PanelStaffRequiredMixin, ListView):
    model = Combo
    template_name = "panel/combo_list.html"
    context_object_name = "combos"
    queryset = Combo.objects.all().order_by("orden", "nombre")


class ComboCreateView(PanelStaffRequiredMixin, CreateView):
    model = Combo
    form_class = ComboForm
    template_name = "panel/combo_form.html"
    success_url = reverse_lazy("menu_panel:combo_list")

    def form_valid(self, form):
        messages.success(self.request, f'Combo "{form.instance.nombre}" creado.')
        return super().form_valid(form)


class ComboUpdateView(PanelStaffRequiredMixin, UpdateView):
    model = Combo
    form_class = ComboForm
    template_name = "panel/combo_form.html"
    success_url = reverse_lazy("menu_panel:combo_list")

    def form_valid(self, form):
        messages.success(self.request, f'Combo "{form.instance.nombre}" actualizado.')
        return super().form_valid(form)


class ComboDeleteView(PanelStaffRequiredMixin, DeleteView):
    model = Combo
    template_name = "panel/confirm_delete.html"
    success_url = reverse_lazy("menu_panel:combo_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["titulo"] = f'¿Eliminar el combo "{self.object.nombre}"?'
        context["cancel_url"] = self.success_url
        return context

    def form_valid(self, form):
        messages.success(self.request, "Combo eliminado.")
        return super().form_valid(form)
