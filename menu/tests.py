import json

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Categoria, Producto, Variante


class ApiProductosTests(TestCase):
    """La BD es la única fuente de verdad: el frontend debe reflejar
    exactamente lo que hay en la base de datos, ni más ni menos."""

    def test_sin_productos_devuelve_lista_vacia(self):
        respuesta = self.client.get(reverse("api_productos"))
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(json.loads(respuesta.content), [])

    def test_un_producto_aparece_exactamente_una_vez(self):
        categoria = Categoria.objects.create(nombre="Arroces", orden=0)
        producto = Producto.objects.create(categoria=categoria, nombre="Arroz Especial", descripcion="Con pollo")
        Variante.objects.create(producto=producto, nombre="Única", precio=25000)

        respuesta = self.client.get(reverse("api_productos"))
        datos = json.loads(respuesta.content)

        self.assertEqual(len(datos), 1)
        self.assertEqual(datos[0]["nombre"], "Arroz Especial")
        self.assertEqual(datos[0]["variantes"][0]["precio"], 25000.0)

    def test_varios_productos_coinciden_exactamente_con_la_bd(self):
        categoria = Categoria.objects.create(nombre="Bebidas", orden=0)
        for i in range(5):
            producto = Producto.objects.create(categoria=categoria, nombre=f"Bebida {i}")
            Variante.objects.create(producto=producto, nombre="Única", precio=1000 * i)

        respuesta = self.client.get(reverse("api_productos"))
        datos = json.loads(respuesta.content)
        self.assertEqual(len(datos), Producto.objects.count())
        self.assertEqual(len(datos), 5)

    def test_producto_inactivo_no_aparece(self):
        categoria = Categoria.objects.create(nombre="Arroces", orden=0)
        producto = Producto.objects.create(categoria=categoria, nombre="Oculto", activo=False)
        Variante.objects.create(producto=producto, nombre="Única", precio=1000)

        respuesta = self.client.get(reverse("api_productos"))
        self.assertEqual(json.loads(respuesta.content), [])

    def test_producto_agotado_no_aparece(self):
        categoria = Categoria.objects.create(nombre="Arroces", orden=0)
        producto = Producto.objects.create(categoria=categoria, nombre="Agotado", agotado=True)
        Variante.objects.create(producto=producto, nombre="Única", precio=1000)

        respuesta = self.client.get(reverse("api_productos"))
        self.assertEqual(json.loads(respuesta.content), [])

    def test_producto_sin_variantes_activas_no_aparece(self):
        categoria = Categoria.objects.create(nombre="Arroces", orden=0)
        Producto.objects.create(categoria=categoria, nombre="Sin precio")
        # No se crea ninguna Variante: no hay forma de venderlo, se omite.

        respuesta = self.client.get(reverse("api_productos"))
        self.assertEqual(json.loads(respuesta.content), [])

    def test_categoria_inactiva_oculta_sus_productos(self):
        categoria = Categoria.objects.create(nombre="Oculta", orden=0, activa=False)
        producto = Producto.objects.create(categoria=categoria, nombre="Producto")
        Variante.objects.create(producto=producto, nombre="Única", precio=1000)

        respuesta = self.client.get(reverse("api_productos"))
        self.assertEqual(json.loads(respuesta.content), [])

    def test_no_hay_datos_hardcodeados_de_ejemplo(self):
        """Nombres del catálogo estático original no deben aparecer si no
        están realmente en la base de datos."""
        respuesta = self.client.get(reverse("api_productos"))
        contenido = respuesta.content.decode("utf-8")
        self.assertNotIn("Arroz Tailandés", contenido)
        self.assertNotIn("Hamburguesa Sencilla", contenido)


class HomePageTests(TestCase):
    def test_sin_categorias_no_rompe_la_pagina(self):
        respuesta = self.client.get(reverse("home"))
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(list(respuesta.context["categorias"]), [])

    def test_con_categorias_aparecen_en_la_pagina(self):
        Categoria.objects.create(nombre="Arroces", orden=0)
        Categoria.objects.create(nombre="Bebidas", orden=1)
        respuesta = self.client.get(reverse("home"))
        html = respuesta.content.decode("utf-8")
        self.assertIn("Arroces", html)
        self.assertIn("Bebidas", html)

    def test_categoria_inactiva_no_aparece_en_nav(self):
        Categoria.objects.create(nombre="Visible", orden=0, activa=True)
        Categoria.objects.create(nombre="Invisible", orden=1, activa=False)
        respuesta = self.client.get(reverse("home"))
        html = respuesta.content.decode("utf-8")
        self.assertIn("Visible", html)
        self.assertNotIn("Invisible", html)


class OrdenCategoriaTests(TestCase):
    """orden=0 debe ser la primera categoría, orden=1 la segunda, etc.,
    tanto en la consulta a la BD como en el HTML que recibe el cliente."""

    def test_orden_ascendente_en_consulta(self):
        Categoria.objects.create(nombre="Tercera", orden=2)
        Categoria.objects.create(nombre="Primera", orden=0)
        Categoria.objects.create(nombre="Segunda", orden=1)

        nombres = list(Categoria.objects.order_by("orden").values_list("nombre", flat=True))
        self.assertEqual(nombres, ["Primera", "Segunda", "Tercera"])

    def test_orden_respetado_en_el_html(self):
        Categoria.objects.create(nombre="Tercera", orden=2)
        Categoria.objects.create(nombre="Primera", orden=0)
        Categoria.objects.create(nombre="Segunda", orden=1)

        respuesta = self.client.get(reverse("home"))
        html = respuesta.content.decode("utf-8")
        pos_primera = html.index("Primera")
        pos_segunda = html.index("Segunda")
        pos_tercera = html.index("Tercera")
        self.assertTrue(pos_primera < pos_segunda < pos_tercera)

    def test_orden_empatado_se_desempata_por_nombre(self):
        Categoria.objects.create(nombre="Zeta", orden=0)
        Categoria.objects.create(nombre="Alfa", orden=0)

        nombres = list(Categoria.objects.order_by("orden", "nombre").values_list("nombre", flat=True))
        self.assertEqual(nombres, ["Alfa", "Zeta"])

    def test_orden_por_defecto_es_cero(self):
        categoria = Categoria.objects.create(nombre="Sin orden explícito")
        self.assertEqual(categoria.orden, 0)


class PanelCategoriaCRUDTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser("admin_test", password="x")
        self.client.login(username="admin_test", password="x")

    def test_crear_categoria_con_icono_del_selector(self):
        respuesta = self.client.post(reverse("menu_panel:categoria_create"), {
            "nombre": "Postres", "icono": "bi-cake2", "orden": 5, "activa": "on",
        })
        self.assertEqual(respuesta.status_code, 302)
        categoria = Categoria.objects.get(nombre="Postres")
        self.assertEqual(categoria.icono, "bi-cake2")
        self.assertEqual(categoria.orden, 5)

    def test_editar_categoria_mantiene_icono_no_listado(self):
        """Una categoría con un ícono que no está en la lista curada
        (dato antiguo) no debe romperse ni perderse al editar otro campo."""
        categoria = Categoria.objects.create(nombre="Vieja", icono="bi-icono-raro-antiguo", orden=0)
        respuesta = self.client.post(reverse("menu_panel:categoria_update", args=[categoria.pk]), {
            "nombre": "Vieja renombrada", "icono": "bi-icono-raro-antiguo", "orden": 0, "activa": "on",
        })
        self.assertEqual(respuesta.status_code, 302)
        categoria.refresh_from_db()
        self.assertEqual(categoria.icono, "bi-icono-raro-antiguo")
        self.assertEqual(categoria.nombre, "Vieja renombrada")

    def test_eliminar_categoria_la_quita_del_frontend(self):
        categoria = Categoria.objects.create(nombre="Temporal", orden=0)
        self.client.post(reverse("menu_panel:categoria_delete", args=[categoria.pk]))
        self.assertFalse(Categoria.objects.filter(pk=categoria.pk).exists())

        respuesta = self.client.get(reverse("home"))
        self.assertNotIn("Temporal", respuesta.content.decode("utf-8"))


class PanelProductoCRUDTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser("admin_test2", password="x")
        self.client.login(username="admin_test2", password="x")
        self.categoria = Categoria.objects.create(nombre="Arroces", orden=0)

    def test_crear_producto_aparece_en_api(self):
        respuesta = self.client.post(reverse("menu_panel:producto_create"), {
            "categoria": self.categoria.pk, "nombre": "Arroz Especial", "descripcion": "Con pollo",
            "etiqueta": "", "orden": 0, "activo": "on",
            "variantes-TOTAL_FORMS": "1", "variantes-INITIAL_FORMS": "0",
            "variantes-MIN_NUM_FORMS": "0", "variantes-MAX_NUM_FORMS": "1000",
            "variantes-0-nombre": "Única", "variantes-0-precio": "25000",
            "variantes-0-orden": "0", "variantes-0-id": "", "variantes-0-activo": "on",
        })
        self.assertEqual(respuesta.status_code, 302)

        api = self.client.get(reverse("api_productos"))
        datos = json.loads(api.content)
        self.assertEqual(len(datos), 1)
        self.assertEqual(datos[0]["nombre"], "Arroz Especial")
        self.assertEqual(datos[0]["descripcion"], "Con pollo")
        self.assertEqual(datos[0]["variantes"][0]["precio"], 25000.0)

    def test_modificar_producto_actualiza_api(self):
        producto = Producto.objects.create(categoria=self.categoria, nombre="Original")
        variante = Variante.objects.create(producto=producto, nombre="Única", precio=10000)

        self.client.post(reverse("menu_panel:producto_update", args=[producto.pk]), {
            "categoria": self.categoria.pk, "nombre": "Modificado", "descripcion": "",
            "etiqueta": "", "orden": 0, "activo": "on",
            "variantes-TOTAL_FORMS": "1", "variantes-INITIAL_FORMS": "1",
            "variantes-MIN_NUM_FORMS": "0", "variantes-MAX_NUM_FORMS": "1000",
            "variantes-0-nombre": "Única", "variantes-0-precio": "30000",
            "variantes-0-orden": "0", "variantes-0-id": variante.pk, "variantes-0-activo": "on",
        })

        api = self.client.get(reverse("api_productos"))
        datos = json.loads(api.content)
        self.assertEqual(datos[0]["nombre"], "Modificado")
        self.assertEqual(datos[0]["variantes"][0]["precio"], 30000.0)

    def test_eliminar_producto_desaparece_de_api(self):
        producto = Producto.objects.create(categoria=self.categoria, nombre="Borrar")
        Variante.objects.create(producto=producto, nombre="Única", precio=1000)

        self.client.post(reverse("menu_panel:producto_delete", args=[producto.pk]))

        api = self.client.get(reverse("api_productos"))
        self.assertEqual(json.loads(api.content), [])
