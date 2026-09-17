from django.db import models
from django.utils.text import slugify

# Lista curada para el selector visual de íconos del panel (no bloquea
# valores ya guardados: una categoría con un ícono fuera de esta lista
# se sigue mostrando bien, solo no aparece marcada como "seleccionada").
ICONOS_CATEGORIA = [
    ("bi-egg-fried", "Arroces / frituras"),
    ("bi-egg", "Huevo"),
    ("bi-noodles", "Espaguetis / pastas"),
    ("bi-fire", "Carnes a la parrilla"),
    ("bi-list", "Hamburguesas"),
    ("bi-circle", "Mazorcadas"),
    ("bi-bowl-hot", "Sopas / Chop Suey"),
    ("bi-cup-straw", "Bebidas frías"),
    ("bi-cup-hot", "Bebidas calientes / café"),
    ("bi-plus-circle", "Adicionales"),
    ("bi-box2-heart", "Entradas"),
    ("bi-basket2", "Ensaladas / acompañamientos"),
    ("bi-cake2", "Postres"),
    ("bi-cup", "Vasos / jugos"),
    ("bi-bag-check", "Combos / promos"),
    ("bi-shop", "Punto de venta"),
]


class Categoria(models.Model):
    nombre = models.CharField(max_length=60)
    slug = models.SlugField(max_length=60, unique=True, blank=True)
    icono = models.CharField(
        max_length=40, blank=True,
        help_text="Clase de Bootstrap Icons, ej: bi-egg-fried",
    )
    orden = models.PositiveIntegerField(default=0)
    activa = models.BooleanField(default=True)

    class Meta:
        ordering = ["orden", "nombre"]
        verbose_name = "categoría"
        verbose_name_plural = "categorías"

    def __str__(self):
        return self.nombre

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)


class Producto(models.Model):
    categoria = models.ForeignKey(
        Categoria, on_delete=models.PROTECT, related_name="productos",
    )
    nombre = models.CharField(max_length=120)
    descripcion = models.TextField(blank=True)
    imagen = models.ImageField(upload_to="productos/", blank=True, null=True)
    etiqueta = models.CharField(
        max_length=40, blank=True,
        help_text="Insignia opcional sobre la foto, ej: RECOMENDADO",
    )
    activo = models.BooleanField(default=True)
    agotado = models.BooleanField(
        default=False,
        help_text="Se acabó por hoy: se oculta del menú sin desactivar el producto.",
    )
    orden = models.PositiveIntegerField(default=0)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["orden", "nombre"]

    def __str__(self):
        return self.nombre

    @property
    def precio_desde(self):
        variante = self.variantes.filter(activo=True).order_by("precio").first()
        return variante.precio if variante else None


class Combo(models.Model):
    nombre = models.CharField(max_length=120)
    descripcion = models.TextField(blank=True)
    imagen = models.ImageField(upload_to="combos/", blank=True, null=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    etiqueta = models.CharField(
        max_length=60, blank=True,
        help_text='Insignia de vigencia, ej: "🔥 DE LUNES A VIERNES"',
    )
    activo = models.BooleanField(default=True)
    orden = models.PositiveIntegerField(default=0)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["orden", "nombre"]

    def __str__(self):
        return self.nombre


class Variante(models.Model):
    producto = models.ForeignKey(
        Producto, on_delete=models.CASCADE, related_name="variantes",
    )
    nombre = models.CharField(
        max_length=60, default="Única",
        help_text='Ej: "¼ porción", "Pan", "Normal". Usa "Única" si el producto no tiene variantes.',
    )
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    activo = models.BooleanField(default=True)
    orden = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["orden", "precio"]

    def __str__(self):
        return f"{self.producto.nombre} - {self.nombre}"
