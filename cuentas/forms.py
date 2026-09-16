from django import forms
from django.contrib.auth.models import Group, User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

ROLES = [("Administrador", "Administrador"), ("Cocina", "Cocina")]

CAMPOS_BASE = ["username", "first_name", "last_name", "email", "is_active"]
WIDGETS_BASE = {
    "username": forms.TextInput(attrs={"class": "form-control"}),
    "first_name": forms.TextInput(attrs={"class": "form-control"}),
    "last_name": forms.TextInput(attrs={"class": "form-control"}),
    "email": forms.EmailInput(attrs={"class": "form-control"}),
    "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
}


class UsuarioBaseForm(forms.ModelForm):
    rol = forms.ChoiceField(choices=ROLES, widget=forms.Select(attrs={"class": "form-select"}))

    class Meta:
        model = User
        fields = CAMPOS_BASE
        widgets = WIDGETS_BASE

    def _guardar_rol(self, usuario):
        grupo = Group.objects.get(name=self.cleaned_data["rol"])
        usuario.groups.set([grupo])


class UsuarioCreateForm(UsuarioBaseForm):
    password = forms.CharField(
        label="Contraseña", widget=forms.PasswordInput(attrs={"class": "form-control"}),
    )

    def clean_password(self):
        password = self.cleaned_data["password"]
        validate_password(password)
        return password

    def save(self, commit=True):
        usuario = super().save(commit=False)
        usuario.set_password(self.cleaned_data["password"])
        if commit:
            usuario.save()
            self._guardar_rol(usuario)
        return usuario


class UsuarioEditForm(UsuarioBaseForm):
    def save(self, commit=True):
        usuario = super().save(commit=commit)
        if commit:
            self._guardar_rol(usuario)
        return usuario


class ResetPasswordForm(forms.Form):
    password1 = forms.CharField(
        label="Nueva contraseña", widget=forms.PasswordInput(attrs={"class": "form-control"}),
    )
    password2 = forms.CharField(
        label="Confirmar contraseña", widget=forms.PasswordInput(attrs={"class": "form-control"}),
    )

    def clean(self):
        cleaned = super().clean()
        p1, p2 = cleaned.get("password1"), cleaned.get("password2")
        if p1 and p2 and p1 != p2:
            raise ValidationError("Las contraseñas no coinciden.")
        if p1:
            validate_password(p1)
        return cleaned
