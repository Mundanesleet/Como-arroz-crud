# Como Arroz — CRUD

Backend en Django del menú digital de **Como Arroz** (Pitalito, Huila). Este proyecto administra el catálogo de productos y los pedidos que antes vivían solo en el frontend estático, permitiendo crear, editar y eliminar información desde una base de datos real en lugar de tenerla hardcodeada en el código.

> Es la versión "con backend" del sitio estático de Como Arroz: aquí el menú y los pedidos se guardan y gestionan en base de datos, no en un arreglo de JavaScript.

## Tecnologías

- **Python 3** + **Django 5.1.2**
- **Pillow 12.3.0** (manejo de imágenes subidas, por ejemplo fotos de productos)
- Plantillas HTML de Django (`templates/`) + CSS/JS propios (`css/`, `js/`, `static/`)

## Estructura del proyecto

```
Como-arroz-crud/
├── config/          # Configuración del proyecto Django (settings, urls, wsgi)
├── cuentas/         # App de autenticación (registro / inicio de sesión)
├── menu/            # App CRUD del menú: productos, categorías, precios
├── pedidos/         # App CRUD de pedidos realizados por los clientes
├── templates/       # Plantillas HTML que usa Django para renderizar las vistas
├── static/          # Archivos estáticos servidos por Django
├── css/             # Estilos del sitio
├── js/              # Scripts del sitio
├── img/             # Imágenes (logo, productos, etc.)
├── index.html        # Página de entrada
├── manage.py        # Utilidad de línea de comandos de Django
└── requirements.txt # Dependencias del proyecto
```

> Nota: esta descripción de cada carpeta está basada en la convención estándar de Django y en los nombres de las carpetas del repo. Si alguna app hace algo distinto a lo aquí descrito, avísame para corregirlo.

## Requisitos previos

- Python 3.10 o superior
- pip

## Instalación

1. **Clona el repositorio**
   ```bash
   git clone https://github.com/Mundanesleet/Como-arroz-crud.git
   cd Como-arroz-crud
   ```

2. **Crea y activa un entorno virtual**
   ```bash
   python -m venv venv

   # Windows
   venv\Scripts\activate

   # macOS / Linux
   source venv/bin/activate
   ```

3. **Instala las dependencias**
   ```bash
   pip install -r requirements.txt
   ```

4. **Aplica las migraciones** (crea la base de datos y sus tablas)
   ```bash
   python manage.py migrate
   ```

5. **Levanta el servidor de desarrollo**
   ```bash
   python manage.py runserver
   ```

6. Abre tu navegador en:
   ```
   http://127.0.0.1:8000/
   ```

## Uso

- **Menú**: la app `menu` permite crear, ver, editar y eliminar los productos que se muestran en el sitio (nombre, categoría, precio, imagen, descripción).
- **Pedidos**: la app `pedidos` guarda y gestiona los pedidos realizados por los clientes.
- **Cuentas**: la app `cuentas` gestiona el registro e inicio de sesión de usuarios.

Si necesitas entrar a la administración de Django para gestionar los datos directamente, primero crea un usuario administrador:

```bash
python manage.py createsuperuser
```

Y accede al panel en:
```
http://127.0.0.1:8000/admin/
```

## Estado del proyecto

Proyecto en desarrollo / práctica. Pendiente por documentar (avísame si quieres que lo agregue):
- Variables de entorno o configuración sensible (si aplica)
- Despliegue en producción
- Capturas de pantalla del sitio funcionando

## Proyecto relacionado

Este backend complementa la versión estática del sitio (HTML/CSS/JS + carrito por WhatsApp), disponible en [Como-arroz](https://github.com/Mundanesleet/Como-arroz).
