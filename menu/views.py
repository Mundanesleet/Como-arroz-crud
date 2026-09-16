from django.db.models import Prefetch
from django.http import JsonResponse
from django.shortcuts import render

from pedidos.models import PuntoRecogida

from .models import Categoria, Combo, Producto, Variante


def home(request):
    categorias = Categoria.objects.filter(activa=True).order_by("orden", "nombre")
    combo = Combo.objects.filter(activo=True).order_by("orden").first()
    puntos_recogida = PuntoRecogida.objects.filter(activo=True).order_by("orden", "nombre")
    return render(request, "public/index.html", {
        "categorias": categorias,
        "combo": combo,
        "puntos_recogida": puntos_recogida,
    })


def api_productos(request):
    """Catálogo activo para el menú público, consumido por static/js/productos.js."""
    productos = (
        Producto.objects.filter(activo=True, agotado=False, categoria__activa=True)
        .select_related("categoria")
        .prefetch_related(
            Prefetch("variantes", queryset=Variante.objects.filter(activo=True).order_by("orden", "precio"))
        )
        .order_by("categoria__orden", "orden", "nombre")
    )

    data = []
    for producto in productos:
        variantes = [{"id": v.id, "nombre": v.nombre, "precio": float(v.precio)} for v in producto.variantes.all()]
        if not variantes:
            # Sin variantes activas no hay precio: no se puede vender, se omite del menú.
            continue
        data.append({
            "id": producto.id,
            "nombre": producto.nombre,
            "categoria": producto.categoria.slug,
            "descripcion": producto.descripcion,
            "etiqueta": producto.etiqueta,
            "imagen": producto.imagen.url if producto.imagen else None,
            "variantes": variantes,
        })

    return JsonResponse(data, safe=False)
