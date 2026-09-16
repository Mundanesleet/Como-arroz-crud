from django import forms
from django.core.exceptions import ValidationError
from django.forms import BaseInlineFormSet, inlineformset_factory

from .models import Categoria, Combo, Producto, Variante


class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ["nombre", "icono", "orden", "activa"]
        widgets = {
            "nombre": forms.TextInput(attrs={"class": "form-control"}),
            "icono": forms.TextInput(attrs={"class": "form-control", "placeholder": "bi-egg-fried"}),
            "orden": forms.NumberInput(attrs={"class": "form-control"}),
            "activa": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ["categoria", "nombre", "descripcion", "imagen", "etiqueta", "orden", "activo", "agotado"]
        widgets = {
            "categoria": forms.Select(attrs={"class": "form-select"}),
            "nombre": forms.TextInput(attrs={"class": "form-control"}),
            "descripcion": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "imagen": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "etiqueta": forms.TextInput(attrs={"class": "form-control", "placeholder": "RECOMENDADO"}),
            "orden": forms.NumberInput(attrs={"class": "form-control"}),
            "activo": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "agotado": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class VarianteBaseFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        if any(self.errors):
            return

        con_precio = 0
        for form in self.forms:
            if not form.cleaned_data or form.cleaned_data.get("DELETE"):
                continue
            if form.cleaned_data.get("precio") is not None:
                con_precio += 1

        if con_precio == 0:
            raise ValidationError("El producto necesita al menos una variante con precio (ej. \"Única\").")


VarianteFormSet = inlineformset_factory(
    Producto,
    Variante,
    formset=VarianteBaseFormSet,
    fields=["nombre", "precio", "orden", "activo"],
    extra=1,
    can_delete=True,
    widgets={
        "nombre": forms.TextInput(attrs={"class": "form-control form-control-sm"}),
        "precio": forms.NumberInput(attrs={"class": "form-control form-control-sm"}),
        "orden": forms.NumberInput(attrs={"class": "form-control form-control-sm"}),
        "activo": forms.CheckboxInput(attrs={"class": "form-check-input"}),
    },
)


class ComboForm(forms.ModelForm):
    class Meta:
        model = Combo
        fields = ["nombre", "descripcion", "imagen", "precio", "etiqueta", "orden", "activo"]
        widgets = {
            "nombre": forms.TextInput(attrs={"class": "form-control"}),
            "descripcion": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "imagen": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "precio": forms.NumberInput(attrs={"class": "form-control"}),
            "etiqueta": forms.TextInput(attrs={"class": "form-control", "placeholder": "🔥 DE LUNES A VIERNES"}),
            "orden": forms.NumberInput(attrs={"class": "form-control"}),
            "activo": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }
