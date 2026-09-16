from django import forms

from .models import PuntoRecogida


class PuntoRecogidaForm(forms.ModelForm):
    class Meta:
        model = PuntoRecogida
        fields = ["nombre", "direccion", "orden", "activo"]
        widgets = {
            "nombre": forms.TextInput(attrs={"class": "form-control"}),
            "direccion": forms.TextInput(attrs={"class": "form-control"}),
            "orden": forms.NumberInput(attrs={"class": "form-control"}),
            "activo": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }
