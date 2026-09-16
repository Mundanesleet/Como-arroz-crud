from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin


def usuario_es_administrador(user):
    return user.is_authenticated and (
        user.is_superuser or user.groups.filter(name="Administrador").exists()
    )


def usuario_es_cocina(user):
    """Cocina y Administrador pueden ver el portal de cocina; solo Administrador
    (o superuser) entra al panel de gestión completo."""
    return user.is_authenticated and (
        user.is_superuser or user.groups.filter(name__in=["Administrador", "Cocina"]).exists()
    )


class PanelStaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Acceso al panel administrativo: superuser o grupo "Administrador"."""
    login_url = "panel_login"

    def test_func(self):
        return usuario_es_administrador(self.request.user)
