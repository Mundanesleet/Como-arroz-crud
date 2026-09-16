"""
Crea los grupos de roles iniciales: Administrador y Cocina.
Sin esto, ningún usuario nuevo (no superuser) puede entrar al panel
ni al portal de cocina. Idempotente.

Uso:
    python manage.py seed_grupos
"""
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand

GRUPOS = ["Administrador", "Cocina"]


class Command(BaseCommand):
    help = "Crea los grupos de roles Administrador y Cocina."

    def handle(self, *args, **options):
        for nombre in GRUPOS:
            _, creado = Group.objects.get_or_create(name=nombre)
            if creado:
                self.stdout.write(self.style.SUCCESS(f'Grupo "{nombre}" creado.'))
            else:
                self.stdout.write(f'Grupo "{nombre}" ya existía.')
