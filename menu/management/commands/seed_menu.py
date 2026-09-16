"""
Carga inicial del catálogo (categorías, productos y variantes) tomando
como referencia los datos que hoy viven en js/productos.js del sitio
estático. Es idempotente: se puede ejecutar varias veces sin duplicar
registros (usa get_or_create / update_or_create).

Uso:
    python manage.py seed_menu
"""
from pathlib import Path

from django.core.files import File
from django.core.management.base import BaseCommand
from django.db import transaction

from menu.models import Categoria, Combo, Producto, Variante

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
IMG_WEB_DIR = BASE_DIR / "img" / "web"

CATEGORIAS = [
    # slug, nombre, icono, orden
    ("arroces", "Arroces", "bi-egg-fried", 1),
    ("espaguetis", "Espaguetis", "bi-noodles", 2),
    ("carnes", "Carnes", "bi-fire", 3),
    ("hamburguesas", "Hamburguesas", "bi-list", 4),
    ("mazorcadas", "Mazorcadas", "bi-circle", 5),
    ("chop-suey", "Chop Suey", "bi-bowl-hot", 6),
    ("bebidas", "Bebidas", "bi-cup-straw", 7),
    ("adicionales", "Adicionales", "bi-plus-circle", 8),
    ("entradas", "Entradas", "bi-box2-heart", 9),
]

# Cada entrada: (categoria_slug, nombre, archivo_imagen_o_None, descripcion,
#                 precio_unico_o_lista_de_variantes, etiqueta)
PRODUCTOS = [
    # ---- ARROCES ----
    ("arroces", "Arroz Tailandés", "arroz-thai",
     "Arroz frito al wok con lomo de cerdo, carne desmechada, camarones, raíces, salsa teriyaki y vegetales frescos.",
     [("¼ porción", 27000), ("½ porción", 40000), ("Caja", 60000)], "RECOMENDADO"),
    ("arroces", "Arroz Chino", "arroz-chino",
     "Arroz frito al wok con vegetales frescos, raíces, lomo de cerdo, pechuga en trozos, camarones salteados y salsa de soya china.",
     [("¼ porción", 27000), ("½ porción", 40000), ("Caja", 60000)], ""),
    ("arroces", "Arroz Ranchero", "arroz-ranchero",
     "Arroz frito al wok con jamón, salchicha llanera, lomo de cerdo, maíz tierno y vegetales frescos salteados.",
     [("¼ porción", 27000), ("½ porción", 40000), ("Caja", 60000)], "MÁS PEDIDO"),
    ("arroces", "Arroz Italiano", "arroz-italiano",
     "Arroz preparado con carne desmechada, pechuga en trozos, salchicha llanera, queso, salsa italiana y salsa de soya.",
     [("¼ porción", 27000), ("½ porción", 40000), ("Caja", 60000)], ""),
    ("arroces", "Arroz Mexicano", "arroz-mexicano",
     "Arroz frito al wok preparado con vegetales, salchicha llanera, jamón ahumado, jalapeños, lomo de cerdo y doritos.",
     [("¼ porción", 27000), ("½ porción", 40000), ("Caja", 60000)], ""),
    ("arroces", "Arroz Queso y Jamón", "arroz-queso-jamon",
     "Arroz preparado con queso y jamón, con carne y pollo en trozos y salsa de la casa.",
     [("¼ porción", 27000), ("½ porción", 40000), ("Caja", 60000)], ""),
    ("arroces", "Arroz Vegetariano", "arroz-vegetariano",
     "Arroz preparado con maíz tierno, zanahoria, pimentón, calabacín, cebolla en julianas, brócoli, coliflor y queso.",
     [("¼ porción", 27000), ("½ porción", 40000), ("Caja", 60000)], "VEGETARIANO"),
    ("arroces", "Arroz Demasiadas Carnes", "arroz-demasiadas-carnes",
     "Arroz frito al wok con una preparación de todas las carnes: lomo de cerdo, pechuga, jamón, salchicha y carne de res desmechada con salsa de soya y BBQ.",
     [("¼ porción", 38000), ("½ porción", 51000), ("Caja", 75000)], "🔥 ESPECIAL"),
    ("arroces", "Arroz con Camarones", "arroz-camarones",
     "Arroz preparado con vegetales frescos, pollo en trozos, lomo de cerdo y camarón tigre.",
     [("¼ porción", 38000), ("½ porción", 51000), ("Caja", 75000)], "🦐 ESPECIAL"),
    ("arroces", "Arroz Mixto", "arroz-mixto",
     "Arroz preparado con vegetales frescos, raíces, plátano maduro, maíz, tocineta, chicharrón, pollo y chorizo.",
     [("¼ porción", 38000), ("½ porción", 51000), ("Caja", 75000)], "ESPECIAL"),

    # ---- ESPAGUETIS ----
    ("espaguetis", "Espagueti Vegetariano", "espagueti-vegetariano",
     "Delicioso espagueti con maíz tierno, raíces, zanahoria, pimentón, calabacín, brócoli, champiñones, coliflor y queso.",
     28000, "VEGETARIANO"),
    ("espaguetis", "Espagueti Tailandés", "espagueti-thai",
     "Delicioso espagueti preparado con carne desmechada, camarones, vegetales frescos, queso y salsa de la casa.",
     28000, "RECOMENDADO"),
    ("espaguetis", "Espagueti Ranchero", "espagueti-ranchero",
     "Espagueti en salsa de la casa con salchicha llanera, jamón ahumado, maíz tierno, queso y vegetales frescos.",
     28000, ""),
    ("espaguetis", "Espagueti Mexicano", "espagueti-mexicano",
     "Espagueti en salsa de la casa con salchicha llanera, jamón, jalapeños, queso y vegetales frescos.",
     28000, ""),
    ("espaguetis", "Espagueti Italiano", "espagueti-italiano",
     "Espagueti con queso, vegetales, carne desmechada, pechuga en trozos y salsa de la casa.",
     28000, ""),
    ("espaguetis", "Espagueti Demasiadas Carnes", "espagueti-demasiadas-carnes",
     "Espagueti con salsa de la casa, vegetales frescos y una cama de carnes picadas, salchicha, cerdo, jamón, carne desmechada, pechuga en trozos y queso.",
     43000, "🔥 ESPECIAL"),
    ("espaguetis", "Espagueti Camarones", "espagueti-camarones",
     "Espagueti con pechuga en trozos, vegetales frescos y una cama de camarones de primera.",
     43000, "🦐 ESPECIAL"),

    # ---- CARNES ----
    ("carnes", "Churrasco", "churrasco",
     "Lomo de res de 270 gramos con ensalada fría y papas a la francesa.", 33000, ""),
    ("carnes", "Pechuga a la Plancha", "pechuga-plancha",
     "Filete de pechuga de 270 gramos con ensalada fría y papas a la francesa.", 27500, ""),
    ("carnes", "Lomo de Cerdo", "lomo-cerdo",
     "Lomo de cerdo de 270 gramos con ensalada fría y papas a la francesa.", 33000, ""),
    ("carnes", "Picada de Carnes", "picada-carnes",
     "Lomo de cerdo, lomo de res, pechuga, chorizo, salchicha llanera, papas a la francesa, plátanos y huevos de codorniz.",
     38000, "PARA COMPARTIR"),
    ("carnes", "Costillas BBQ", "costillas-bbq",
     "400 gramos de costillas acompañadas de papa a la francesa.", 38000, ""),
    ("carnes", "Ceviche de Camarones", "ceviche-camarones",
     "250 gramos de camarón tigre con salsa de tomate, mayonesa, ajo, ají, pimentón, cebolla y cilantro, acompañado con galletas saltín y jugo de naranja.",
     25000, "🦐"),
    ("carnes", "Ceviche Especial", "ceviche-especial",
     "Ceviche con ingredientes frescos, camarón tigre, pimentón, cilantro, salsa de ajo y sal, acompañado con galletas saltín y jugo de naranja.",
     29000, "🦐 ESPECIAL"),

    # ---- MAZORCADAS ----
    ("mazorcadas", "Mazorcada de Pollo", "mazorcada-pollo",
     "Pechuga en trozos, maíz tierno, queso, ripio de papa y salsas.", 28500, ""),
    ("mazorcadas", "Mazorcada de Carnes", "mazorcada-carnes",
     "Carne desmechada, maíz tierno, queso, ripio de papa y salsas.", 28500, ""),
    ("mazorcadas", "Mazorcada Mixta", "mazorcada-mixta",
     "Carne desmechada, pechuga en trozos, tocineta, maíz tierno, queso, ripio de papa y salsas.",
     32000, "MÁS PEDIDO"),
    ("mazorcadas", "Mazorcada Media Mixta", "mazorcada-media-mixta",
     "Carne desmechada, pechuga en trozos, tocineta, maíz tierno, queso, ripio de papa y salsas.", 20000, ""),

    # ---- HAMBURGUESAS Y COMIDAS RÁPIDAS ----
    ("hamburguesas", "Hamburguesa Sencilla", "hamburguesa-sencilla",
     "Pan o patacón, carne de res o pollo apanado, lechuga, tomate, cebolla sofrita y salsas.",
     [("Pan", 19000), ("Patacón", 20000)], ""),
    ("hamburguesas", "Hamburguesa Especial", "hamburguesa-especial",
     "Doble carne de res, pollo apanado o mixta, doble queso, lechuga, tomate, cebolla sofrita y champiñones.",
     [("Pan", 27500), ("Patacón", 29000)], "MÁS PEDIDO"),
    ("hamburguesas", "Choripapa", "choripapa",
     "300 gramos de papa a la francesa, chorizo de Las Brisas, queso y huevos de codorniz.", 22000, ""),
    ("hamburguesas", "Chorizo", "chorizo",
     "Chorizo de Las Brisas acompañado con 150 gramos de papas a la francesa, lechuga y tomate.", 10000, ""),
    ("hamburguesas", "Nuggets de Pollo", "nuggets-pollo",
     "Nuggets de pollo acompañados con papas a la francesa.", 19000, ""),
    ("hamburguesas", "Salchipapa Especial", "salchipapa-especial",
     "300 gramos de papa a la francesa, salchicha llanera, queso y huevo de codorniz.", 21000, ""),
    ("hamburguesas", "Salchipapa Junior", "salchipapa-junior",
     "Papa a la francesa, salchicha llanera, queso y huevo de codorniz.", 13000, ""),

    # ---- CHOP SUEY ----
    ("chop-suey", "Chop Suey Vegetales", None,
     "Vegetales frescos: cebolla, brócoli, coliflor, pimentón, calabacín, raíces y zanahoria en delicioso caldo de pollo.", 22000, ""),
    ("chop-suey", "Chop Suey con Lomo de Cerdo", None,
     "Chop Suey de vegetales acompañado de lomo de cerdo.", 30000, ""),
    ("chop-suey", "Chop Suey con Pollo", None,
     "Chop Suey de vegetales acompañado de pollo.", 30000, ""),
    ("chop-suey", "Chop Suey Mixto", None,
     "Chop Suey mixto de pollo, cerdo y camarón.", 34000, "RECOMENDADO"),

    # ---- BEBIDAS ----
    ("bebidas", "Jugo Natural en Agua", None,
     "Sabores: fresa, mora, maracuyá, mango, lulo, guanábana y limonada.",
     [("Vaso 22 oz", 6500), ("Jarra 40 oz", 12000)], ""),
    ("bebidas", "Jugo Natural en Leche", None,
     "Sabores: fresa, mora, maracuyá, mango, lulo, guanábana y limonada.",
     [("Vaso 22 oz", 8500), ("Jarra 40 oz", 16000)], ""),
    ("bebidas", "Jugo Hit Personal", None, "Jugo Hit personal.", 4500, ""),
    ("bebidas", "Jugo Hit Litro", None, "Jugo Hit en presentación de litro.", 6500, ""),
    ("bebidas", "Gaseosa Tropikola 400 ml", None, "Gaseosa Tropikola de 400 ml.", 5500, ""),
    ("bebidas", "Gaseosa PET 400 ml", None, "Gaseosa PET de 400 ml.", 5000, ""),
    ("bebidas", "Gaseosa 1.5 L", None, "Gaseosa familiar de 1.5 litros.", 9500, ""),
    ("bebidas", "Gaseosa 3 L", None, "Gaseosa familiar de 3 litros.", 13000, ""),
    ("bebidas", "Power", None, "Bebida Power.", 5500, ""),
    ("bebidas", "Agua", None, "Botella de agua.", 3000, ""),
    ("bebidas", "Agua con Gas", None, "Botella de agua con gas.", 4000, ""),
    ("bebidas", "Cerveza Águila o Poker", None, "Presentación disponible según existencia.", 5000, ""),
    ("bebidas", "Cerveza Club Colombia", None, "Cerveza Club Colombia.", 6000, ""),
    ("bebidas", "Cerveza Corona / Heineken", None, "Presentación disponible según existencia.", 7000, ""),
    ("bebidas", "Limonada de Coco", None, "Limonada de coco.", 13000, "NUEVA"),
    ("bebidas", "Limonada de Cereza", None, "Limonada de cereza.", 13000, "NUEVA"),
    ("bebidas", "Malteada", None, "Malteada de la casa.", 13000, "NUEVA"),
    ("bebidas", "Limonada Mango Biche", None, "Limonada de mango biche.", 13000, "NUEVA"),
    ("bebidas", "Maltiricrunch", None, "Nueva bebida de la casa con topping especial.", 16500, "NUEVA"),

    # ---- ADICIONALES ----
    ("adicionales", "Papas a la Francesa 125 g", None, "Porción de papas a la francesa de 125 gramos.", 4500, ""),
    ("adicionales", "Papas a la Francesa 250 g", None, "Porción de papas a la francesa de 250 gramos.", 8000, ""),
    ("adicionales", "Yuca Frita", None, "Porción de yuca frita.", 4500, ""),
    ("adicionales", "Patacón", None, "Porción de patacón.", 5500, ""),
    ("adicionales", "Camarón Tigre 250 g", None, "Porción de camarón tigre de 250 gramos.", 19000, "🦐"),
    ("adicionales", "Queso", None, "Porción adicional de queso.", 3000, ""),
    ("adicionales", "Jalapeños", None, "Porción adicional de jalapeños.", 2200, ""),
    ("adicionales", "Maíz Tierno", None, "Porción adicional de maíz tierno.", 6000, ""),
    ("adicionales", "Ensalada Fría", None, "Porción de ensalada fría.", 7500, ""),
    ("adicionales", "Huevos de Codorniz", None, "Porción de huevos de codorniz.", 6000, ""),
    ("adicionales", "Tocineta", None, "Porción adicional de tocineta.", 4000, ""),
    ("adicionales", "Empaque", None, "Empaque para llevar.", 1500, ""),

    # ---- ENTRADAS ----
    ("entradas", "Rollos Primavera (Lumpias) x2", None, "2 rollos primavera (lumpias).", 7000, "ENTRADA"),
    ("entradas", "Rollos Primavera (Lumpias) x4", None, "4 rollos primavera (lumpias).", 13000, "ENTRADA"),
    ("entradas", "Plato de Arroz Demasiadas Carnes", None,
     "Arroz frito al wok con una preparación especial de todas las carnes, con salsa de soya y BBQ.", 21000, "ESPECIAL"),
]


class Command(BaseCommand):
    help = "Carga las categorías y productos iniciales de Como Arroz."

    @transaction.atomic
    def handle(self, *args, **options):
        categorias_por_slug = {}
        for slug, nombre, icono, orden in CATEGORIAS:
            categoria, _ = Categoria.objects.update_or_create(
                slug=slug,
                defaults={"nombre": nombre, "icono": icono, "orden": orden, "activa": True},
            )
            categorias_por_slug[slug] = categoria
        self.stdout.write(self.style.SUCCESS(f"{len(categorias_por_slug)} categorías listas."))

        creados = 0
        for orden, (cat_slug, nombre, archivo_imagen, descripcion, precio_o_variantes, etiqueta) in enumerate(PRODUCTOS):
            categoria = categorias_por_slug[cat_slug]
            producto, _ = Producto.objects.update_or_create(
                categoria=categoria, nombre=nombre,
                defaults={
                    "descripcion": descripcion,
                    "etiqueta": etiqueta,
                    "orden": orden,
                    "activo": True,
                },
            )

            if archivo_imagen and not producto.imagen:
                ruta_imagen = IMG_WEB_DIR / cat_slug / f"{archivo_imagen}.webp"
                if ruta_imagen.exists():
                    with open(ruta_imagen, "rb") as f:
                        producto.imagen.save(ruta_imagen.name, File(f), save=True)

            producto.variantes.all().delete()
            if isinstance(precio_o_variantes, list):
                for v_orden, (v_nombre, v_precio) in enumerate(precio_o_variantes):
                    Variante.objects.create(
                        producto=producto, nombre=v_nombre, precio=v_precio, orden=v_orden,
                    )
            else:
                Variante.objects.create(
                    producto=producto, nombre="Única", precio=precio_o_variantes, orden=0,
                )

            creados += 1

        self.stdout.write(self.style.SUCCESS(f"{creados} productos cargados con sus variantes."))

        combo, _ = Combo.objects.update_or_create(
            nombre="Combo de la casa",
            defaults={
                "descripcion": (
                    "Arroz de la casa, papas a la francesa, ensalada, "
                    "gaseosa de 250 ml y filete de carne de 125 gr."
                ),
                "precio": 12300,
                "etiqueta": "🔥 DE LUNES A VIERNES",
                "activo": True,
                "orden": 0,
            },
        )
        ruta_imagen_combo = BASE_DIR / "img" / "combo" / "combo.png"
        if ruta_imagen_combo.exists() and not combo.imagen:
            with open(ruta_imagen_combo, "rb") as f:
                combo.imagen.save(ruta_imagen_combo.name, File(f), save=True)

        self.stdout.write(self.style.SUCCESS("Combo de la casa listo."))
