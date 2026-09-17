/* =========================================================
   COMO ARROZ - PRODUCTOS.JS
   El catálogo NO vive aquí hardcodeado. Se carga desde la API
   de Django (/api/menu/productos/), que lee categorías,
   productos y variantes directamente de la base de datos.

   Debe cargarse en el HTML ANTES de app.js:
   <script src="js/productos.js"></script>
   <script src="js/app.js"></script>
   ========================================================= */

let productos = [];

async function cargarProductos() {
    const respuesta = await fetch("/api/menu/productos/");
    if (!respuesta.ok) {
        throw new Error(`No se pudo cargar el menú (HTTP ${respuesta.status}).`);
    }
    productos = await respuesta.json();
    return productos;
}
