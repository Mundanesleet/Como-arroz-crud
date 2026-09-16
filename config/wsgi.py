"""
WSGI config for config project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""

import logging
import os

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

# ------------------------------------------------------------------
# Red de seguridad para producción.
#
# Django exige que collectstatic haya corrido ANTES de arrancar cuando
# se usa almacenamiento con manifiesto (WhiteNoise en modo comprimido).
# Si el "Build Command" del hosting no lo ejecuta por cualquier motivo,
# cada página que use {% static %} revienta con 500 (manifest faltante).
#
# Para que la app nunca dependa por completo de que ese paso externo
# esté bien configurado, la generamos aquí también al arrancar el
# proceso, ANTES de construir el WSGI (para que WhiteNoise ya encuentre
# la carpeta lista). Es rápido si ya está hecha y evita el 500 por
# completo.
# ------------------------------------------------------------------
if os.environ.get('DJANGO_DEBUG', 'True').lower() != 'true':
    from django.core.management import call_command

    try:
        call_command('collectstatic', interactive=False, verbosity=0)
    except Exception:
        logging.getLogger('django').exception(
            'No se pudo generar collectstatic automáticamente al arrancar.'
        )

from django.core.wsgi import get_wsgi_application  # noqa: E402

application = get_wsgi_application()
