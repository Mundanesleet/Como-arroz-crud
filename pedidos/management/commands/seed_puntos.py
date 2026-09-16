"""
Carga los puntos de recogida iniciales (los mismos que hoy están
hardcodeados en el <select> de index.html). Idempotente.

Uso:
    python manage.py seed_puntos
"""
from django.core.management.base import BaseCommand

from pedidos.models import PuntoRecogida

PUNTOS = [
    ("Central", 1),
    ("Nogales", 2),
    ("Solarte", 3),
]


class Command(BaseCommand):
    help = "Carga los puntos de recogida iniciales de Como Arroz."

    def handle(self, *args, **options):
        for nombre, orden in PUNTOS:
            PuntoRecogida.objects.update_or_create(
                nombre=nombre, defaults={"orden": orden, "activo": True},
            )
        self.stdout.write(self.style.SUCCESS(f"{len(PUNTOS)} puntos de recogida listos."))
