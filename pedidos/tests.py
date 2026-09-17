import json
import re
from pathlib import Path

from django.conf import settings
from django.test import TestCase
from django.urls import reverse

from menu.models import Categoria, Producto, Variante

from .models import Pedido, PuntoRecogida


class SinWhatsAppEnElPedidoTests(TestCase):
    """Red de seguridad contra la regresión que ya ocurrió una vez: alguien
    (o alguna herramienta) sobreescribió static/js/app.js con la versión
    vieja que envía el pedido completo por WhatsApp. Esto falla fuerte y
    explícito si se vuelve a colar."""

    def test_app_js_no_envia_el_pedido_por_whatsapp(self):
        ruta = Path(settings.BASE_DIR) / "static" / "js" / "app.js"
        contenido = ruta.read_text(encoding="utf-8")

        prohibidos = [
            "generarMensajeWhatsApp",
            "btnEnviarWhatsApp",
            "NUMERO_WHATSAPP =",
            "wa.me",
        ]
        for patron in prohibidos:
            self.assertNotIn(
                patron, contenido,
                f'"{patron}" apareció en static/js/app.js: el pedido no debe enviarse por WhatsApp.',
            )

    def test_app_js_crea_el_pedido_via_fetch(self):
        ruta = Path(settings.BASE_DIR) / "static" / "js" / "app.js"
        contenido = ruta.read_text(encoding="utf-8")
        self.assertIn("/pedidos/crear/", contenido)

    def test_productos_js_no_tiene_catalogo_hardcodeado(self):
        ruta = Path(settings.BASE_DIR) / "static" / "js" / "productos.js"
        contenido = ruta.read_text(encoding="utf-8")
        self.assertNotIn("crearProducto(", contenido)
        self.assertIn("/api/menu/productos/", contenido)


class CrearPedidoTests(TestCase):
    def setUp(self):
        categoria = Categoria.objects.create(nombre="Bebidas", orden=0)
        self.producto = Producto.objects.create(categoria=categoria, nombre="Agua")
        self.variante = Variante.objects.create(producto=self.producto, nombre="Única", precio=3000)
        self.punto = PuntoRecogida.objects.create(nombre="Central", orden=0)

    def _carrito(self):
        return json.dumps([{"tipo": "producto", "id": self.producto.id, "variante_id": self.variante.id, "cantidad": 1}])

    def test_efectivo_crea_pedido_sin_whatsapp_en_confirmacion(self):
        respuesta = self.client.post(reverse("pedidos:crear_pedido"), {
            "cliente_nombre": "Cliente Test", "cliente_telefono": "3000000000",
            "tipo_pedido": "recoger", "punto_recogida": self.punto.id,
            "metodo_pago": "efectivo", "observaciones": "", "carrito": self._carrito(),
        })
        datos = json.loads(respuesta.content)
        self.assertTrue(datos["ok"])

        confirmacion = self.client.get(datos["redirect_url"])
        html = confirmacion.content.decode("utf-8")
        self.assertNotIn("wa.me", html)
        self.assertIn("PEDIDO RECIBIDO", html)

    def test_domicilio_mas_tarjeta_se_rechaza(self):
        respuesta = self.client.post(reverse("pedidos:crear_pedido"), {
            "cliente_nombre": "Cliente Test", "cliente_telefono": "3000000000",
            "tipo_pedido": "domicilio", "direccion": "Calle 1", "barrio": "Centro",
            "metodo_pago": "tarjeta", "observaciones": "", "carrito": self._carrito(),
        })
        self.assertEqual(respuesta.status_code, 400)
        datos = json.loads(respuesta.content)
        self.assertFalse(datos["ok"])

    def test_transferencia_sin_comprobante_crea_pedido_por_verificar(self):
        respuesta = self.client.post(reverse("pedidos:crear_pedido"), {
            "cliente_nombre": "Cliente Test", "cliente_telefono": "3000000000",
            "tipo_pedido": "recoger", "punto_recogida": self.punto.id,
            "metodo_pago": "transferencia", "observaciones": "", "carrito": self._carrito(),
        })
        datos = json.loads(respuesta.content)
        self.assertTrue(datos["ok"])

        pedido = Pedido.objects.get(pk=datos["pedido_id"])
        self.assertEqual(pedido.estado_pago, Pedido.EstadoPago.POR_VERIFICAR)

    def test_confirmacion_transferencia_muestra_whatsapp_solo_para_comprobante(self):
        respuesta = self.client.post(reverse("pedidos:crear_pedido"), {
            "cliente_nombre": "Cliente Test", "cliente_telefono": "3000000000",
            "tipo_pedido": "recoger", "punto_recogida": self.punto.id,
            "metodo_pago": "transferencia", "observaciones": "", "carrito": self._carrito(),
        })
        datos = json.loads(respuesta.content)

        confirmacion = self.client.get(datos["redirect_url"])
        html = confirmacion.content.decode("utf-8")

        self.assertIn("wa.me", html)
        self.assertIn("Enviar comprobante por WhatsApp", html)

        # El pedido ya existe ANTES de llegar aquí: el mensaje del enlace
        # solo debe referenciar el número de pedido y el total, nunca la
        # lista de productos (WhatsApp no es el mecanismo del pedido).
        href = re.search(r'href="(https://wa\.me/[^"]+)"', html).group(1)
        mensaje = href.split("text=", 1)[1]
        self.assertIn(f"pedido+%23{datos['pedido_id']}", mensaje)
        self.assertNotIn("Agua", mensaje)

    def test_carrito_vacio_se_rechaza(self):
        respuesta = self.client.post(reverse("pedidos:crear_pedido"), {
            "cliente_nombre": "Cliente Test", "cliente_telefono": "3000000000",
            "tipo_pedido": "recoger", "punto_recogida": self.punto.id,
            "metodo_pago": "efectivo", "observaciones": "", "carrito": "[]",
        })
        self.assertEqual(respuesta.status_code, 400)
