/* =========================================================
   COMO ARROZ - APP.JS
   Menú digital + carrito + pedido registrado en Django.

   IMPORTANTE: este archivo depende de la variable global
   `productos`, poblada de forma asíncrona por productos.js
   (fetch a /api/menu/productos/). Debe cargarse así en el HTML:
     <script src="js/productos.js"></script>
     <script src="js/app.js"></script>
   ========================================================= */

const CLAVE_STORAGE_CARRITO = "comoarroz_carrito";

/* =========================================================
   DOM + ESTADO
   ========================================================= */

const contenedorProductos = document.getElementById("contenedorProductos");
const tituloCategoria = document.getElementById("tituloCategoria");
const cantidadProductos = document.getElementById("cantidadProductos");
const botonesCategoria = document.querySelectorAll(".categoria-btn");

const carritoContador = document.getElementById("carritoContador");
const carritoProductos = document.getElementById("carritoProductos");
const carritoVacio = document.getElementById("carritoVacio");
const carritoResumen = document.getElementById("carritoResumen");
const carritoSubtotal = document.getElementById("carritoSubtotal");
const carritoTotal = document.getElementById("carritoTotal");
const btnContinuarPedido = document.getElementById("btnContinuarPedido");
const btnCombo = document.getElementById("btnCombo");

const modalPedidoElement = document.getElementById("modalPedido");
const modalPedido = modalPedidoElement ? new bootstrap.Modal(modalPedidoElement) : null;

let carrito = cargarCarritoGuardado();
let modalVariantes = null;
let productoPendiente = null;

/* =========================================================
   PERSISTENCIA DEL CARRITO (localStorage)
   ========================================================= */

function cargarCarritoGuardado() {
    try {
        const guardado = localStorage.getItem(CLAVE_STORAGE_CARRITO);
        const datos = guardado ? JSON.parse(guardado) : [];
        return Array.isArray(datos) ? datos : [];
    } catch {
        return [];
    }
}

function guardarCarrito() {
    try {
        localStorage.setItem(CLAVE_STORAGE_CARRITO, JSON.stringify(carrito));
    } catch {
        // localStorage puede fallar en modo incógnito o si está lleno.
        // El carrito sigue funcionando en memoria aunque no se guarde.
    }
}

/* =========================================================
   UTILIDADES
   ========================================================= */

function formatoPrecio(valor) {
    return new Intl.NumberFormat("es-CO", {
        style: "currency",
        currency: "COP",
        maximumFractionDigits: 0
    }).format(valor);
}

function escaparHTML(valor) {
    return String(valor ?? "")
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

function nombreCategoria(categoria) {
    const boton = document.querySelector(`.categoria-btn[data-categoria="${categoria}"] span`);
    return boton ? boton.textContent : (categoria || "Menú");
}

function iconoCategoria(categoria) {
    const icono = document.querySelector(`.categoria-btn[data-categoria="${categoria}"] i`);
    return icono ? icono.className.replace("bi ", "") : "bi-egg-fried";
}

// Con más de una variante mostramos el selector; con una sola (ej. "Única")
// se agrega directo, igual que antes con los productos de precio fijo.
function tieneVariantes(producto) {
    return Array.isArray(producto.variantes) && producto.variantes.length > 1;
}

function precioDesde(producto) {
    return Math.min(...producto.variantes.map(variante => variante.precio));
}

function obtenerCSRFToken() {
    return document.querySelector('input[name="csrfmiddlewaretoken"]')?.value || "";
}

function obtenerProductoPorId(id) {
    return productos.find(producto => producto.id === id);
}

/* =========================================================
   MOSTRAR PRODUCTOS
   ========================================================= */

function mostrarProductos(categoria) {
    if (!contenedorProductos) return;

    const lista = categoria ? productos.filter(producto => producto.categoria === categoria) : [];

    if (tituloCategoria) tituloCategoria.textContent = nombreCategoria(categoria);
    if (cantidadProductos) cantidadProductos.textContent = lista.length;

    contenedorProductos.innerHTML = "";

    if (lista.length === 0) {
        mostrarEstadoVacioProductos();
        return;
    }

    lista.forEach((producto, indice) => {
        const tarjeta = crearTarjetaProducto(producto);
        tarjeta.style.opacity = "0";
        tarjeta.style.transform = "translateY(16px)";

        contenedorProductos.appendChild(tarjeta);

        setTimeout(() => {
            tarjeta.style.transition = "opacity .35s ease, transform .35s ease";
            tarjeta.style.opacity = "1";
            tarjeta.style.transform = "translateY(0)";
        }, indice * 45);
    });
}

// La BD es la única fuente de verdad: si no hay productos (categoría
// vacía o catálogo completo vacío), se muestra un estado vacío real,
// nunca datos de ejemplo ni tarjetas ficticias.
function mostrarEstadoVacioProductos() {
    if (!contenedorProductos) return;
    contenedorProductos.innerHTML = `
        <div class="col-12 productos-vacio">
            <i class="bi bi-emoji-neutral"></i>
            <p>No hay productos disponibles en esta categoría por ahora.</p>
        </div>
    `;
}

function crearTarjetaProducto(producto) {
    const nombre = escaparHTML(producto.nombre);
    const descripcion = escaparHTML(producto.descripcion);
    const etiqueta = escaparHTML(producto.etiqueta || "");

    const precioHTML = tieneVariantes(producto)
        ? `Desde ${formatoPrecio(precioDesde(producto))}`
        : formatoPrecio(precioDesde(producto));

    const tieneImagen = Boolean(producto.imagen);

    const tarjeta = document.createElement("div");
    tarjeta.className = "col-12 col-sm-6 col-lg-4";

    tarjeta.innerHTML = `
        <div class="producto-card">
            <div class="producto-imagen" role="button" tabindex="0" aria-label="Agregar ${nombre} al carrito">
                ${tieneImagen ? `
                <img
                    src="${producto.imagen}"
                    alt="${nombre}"
                    class="producto-foto"
                    loading="lazy"
                    decoding="async"
                    width="1200"
                    height="800"
                >` : ""}
                <div class="producto-imagen-placeholder" style="${tieneImagen ? "display:none;" : "display:flex;"}">
                    <i class="bi ${iconoCategoria(producto.categoria)}"></i>
                    <span>Foto del plato</span>
                </div>
                ${etiqueta ? `<span class="producto-etiqueta">${etiqueta}</span>` : ""}
            </div>
            <div class="producto-contenido">
                <h3 class="producto-nombre">${nombre}</h3>
                <p class="producto-descripcion">${descripcion}</p>
                <div class="producto-footer">
                    <span class="producto-precio">${precioHTML}</span>
                    <button class="btn-agregar" type="button" aria-label="Agregar ${nombre}">
                        <i class="bi bi-plus-lg"></i>
                    </button>
                </div>
            </div>
        </div>
    `;

    // Si la imagen real falla en tiempo de carga, caemos al placeholder.
    if (tieneImagen) {
        const img = tarjeta.querySelector(".producto-foto");
        img.addEventListener("error", function manejarErrorImagen() {
            img.removeEventListener("error", manejarErrorImagen);
            img.style.display = "none";
            img.nextElementSibling.style.display = "flex";
        });
    }

    // Agregar al carrito: botón "+" e imagen hacen exactamente lo mismo
    // (misma función, sin lógica duplicada). Un solo listener por zona,
    // así que un clic nunca agrega el producto dos veces.
    tarjeta.querySelector(".btn-agregar").addEventListener("click", (evento) => {
        evento.stopPropagation();
        agregarAlCarrito(producto.id);
    });

    const zonaImagen = tarjeta.querySelector(".producto-imagen");
    zonaImagen.addEventListener("click", () => {
        agregarAlCarrito(producto.id);
    });
    zonaImagen.addEventListener("keydown", (evento) => {
        if (evento.key === "Enter" || evento.key === " ") {
            evento.preventDefault();
            agregarAlCarrito(producto.id);
        }
    });

    return tarjeta;
}

/* =========================================================
   MODAL DE VARIANTES
   ========================================================= */

function crearModalVariantes() {
    if (document.getElementById("modalVariantes")) return;

    const modal = document.createElement("div");
    modal.className = "modal fade";
    modal.id = "modalVariantes";
    modal.tabIndex = -1;

    modal.innerHTML = `
        <div class="modal-dialog modal-dialog-centered">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title" id="tituloModalVariantes">Personaliza tu pedido</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Cerrar"></button>
                </div>
                <div class="modal-body" id="listaVariantes"></div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
                    <button type="button" class="btn btn-danger" id="btnConfirmarVariante">
                        <i class="bi bi-cart-plus me-1"></i> Agregar al pedido
                    </button>
                </div>
            </div>
        </div>
    `;

    document.body.appendChild(modal);
    modalVariantes = new bootstrap.Modal(modal);
    document.getElementById("btnConfirmarVariante").addEventListener("click", confirmarVariante);
}

function abrirSelectorVariantes(producto) {
    crearModalVariantes();
    productoPendiente = producto;

    document.getElementById("tituloModalVariantes").textContent = `Personaliza: ${producto.nombre}`;

    const lista = document.getElementById("listaVariantes");
    lista.innerHTML = producto.variantes
        .map((variante, indice) => `
            <label class="variante-opcion">
                <input type="radio" name="varianteSeleccionada" value="${indice}" ${indice === 0 ? "checked" : ""}>
                <span class="variante-info">
                    <span class="variante-nombre">${escaparHTML(variante.nombre)}</span>
                    <span class="variante-precio">${formatoPrecio(variante.precio)}</span>
                </span>
            </label>
        `)
        .join("");

    modalVariantes.show();
}

function confirmarVariante() {
    if (!productoPendiente) return;

    const seleccionado = document.querySelector('input[name="varianteSeleccionada"]:checked');
    if (!seleccionado) return;

    const variante = productoPendiente.variantes[Number(seleccionado.value)];
    agregarLineaAlCarrito({
        tipo: "producto", id: productoPendiente.id, varianteId: variante.id, varianteNombre: variante.nombre,
        nombre: productoPendiente.nombre, precio: variante.precio,
    });

    if (modalVariantes) modalVariantes.hide();
    productoPendiente = null;
}

/* =========================================================
   CARRITO
   ========================================================= */

function agregarAlCarrito(id) {
    const producto = obtenerProductoPorId(id);
    if (!producto) return;

    if (tieneVariantes(producto)) {
        abrirSelectorVariantes(producto);
        return;
    }

    // Una sola variante (ej. "Única"): se agrega directo, sin mostrar selector.
    const unica = producto.variantes[0];
    agregarLineaAlCarrito({
        tipo: "producto", id: producto.id, varianteId: unica.id, varianteNombre: null,
        nombre: producto.nombre, precio: unica.precio,
    });
    mostrarCarrito();
}

// El backend recalcula el precio real a partir de varianteId (o del combo);
// lo que viaja aquí es solo para mostrar el carrito al cliente.
function agregarLineaAlCarrito({ tipo, id, varianteId, varianteNombre, nombre, precio }) {
    const lineaId = `${tipo}-${id}-${varianteId ?? "normal"}`;
    const existente = carrito.find(item => item.lineaId === lineaId);

    if (existente) {
        existente.cantidad++;
    } else {
        carrito.push({ lineaId, tipo, id, varianteId, varianteNombre, nombre, precio, cantidad: 1 });
    }

    actualizarCarrito();
    animarCarrito();
}

function aumentarCantidad(lineaId) {
    const item = carrito.find(producto => producto.lineaId === lineaId);
    if (!item) return;
    item.cantidad++;
    actualizarCarrito();
}

function disminuirCantidad(lineaId) {
    const item = carrito.find(producto => producto.lineaId === lineaId);
    if (!item) return;

    item.cantidad--;
    if (item.cantidad <= 0) {
        carrito = carrito.filter(producto => producto.lineaId !== lineaId);
    }

    actualizarCarrito();
}

function eliminarDelCarrito(lineaId) {
    carrito = carrito.filter(producto => producto.lineaId !== lineaId);
    actualizarCarrito();
}

function calcularCantidadTotal() {
    return carrito.reduce((total, producto) => total + producto.cantidad, 0);
}

function calcularTotal() {
    return carrito.reduce((total, producto) => total + producto.precio * producto.cantidad, 0);
}

/* =========================================================
   ACTUALIZAR CARRITO
   ========================================================= */

function actualizarCarrito() {
    guardarCarrito();

    const total = calcularTotal();

    if (carritoContador) carritoContador.textContent = calcularCantidadTotal();

    if (!carritoProductos || !carritoVacio || !carritoResumen) return;

    if (carrito.length === 0) {
        carritoVacio.style.display = "flex";
        carritoResumen.style.display = "none";
        carritoProductos.innerHTML = "";
        return;
    }

    carritoVacio.style.display = "none";
    carritoResumen.style.display = "block";
    carritoProductos.innerHTML = "";

    carrito.forEach(producto => {
        const item = document.createElement("div");
        item.className = "carrito-item";

        item.innerHTML = `
            <div class="carrito-item-info">
                <div class="carrito-item-nombre">${escaparHTML(producto.nombre)}</div>
                ${producto.varianteNombre ? `<div class="carrito-item-variante">${escaparHTML(producto.varianteNombre)}</div>` : ""}
                <div class="carrito-item-precio">${formatoPrecio(producto.precio)} c/u</div>
                <div class="cantidad-control">
                    <button class="cantidad-btn" type="button" data-accion="disminuir" aria-label="Disminuir cantidad">
                        <i class="bi bi-dash"></i>
                    </button>
                    <span class="cantidad-numero">${producto.cantidad}</span>
                    <button class="cantidad-btn" type="button" data-accion="aumentar" aria-label="Aumentar cantidad">
                        <i class="bi bi-plus"></i>
                    </button>
                    <button class="btn-eliminar ms-2" type="button" data-accion="eliminar" aria-label="Eliminar producto">
                        <i class="bi bi-trash"></i>
                    </button>
                </div>
            </div>
            <div class="carrito-item-total">${formatoPrecio(producto.precio * producto.cantidad)}</div>
        `;

        item.querySelector('[data-accion="disminuir"]').addEventListener("click", () => disminuirCantidad(producto.lineaId));
        item.querySelector('[data-accion="aumentar"]').addEventListener("click", () => aumentarCantidad(producto.lineaId));
        item.querySelector('[data-accion="eliminar"]').addEventListener("click", () => eliminarDelCarrito(producto.lineaId));

        carritoProductos.appendChild(item);
    });

    if (carritoSubtotal) carritoSubtotal.textContent = formatoPrecio(total);
    if (carritoTotal) carritoTotal.textContent = formatoPrecio(total);
}

/* =========================================================
   MOSTRAR / ANIMAR CARRITO
   ========================================================= */

function mostrarCarrito() {
    const elemento = document.getElementById("carrito");
    if (!elemento) return;
    bootstrap.Offcanvas.getOrCreateInstance(elemento).show();
}

function animarCarrito() {
    if (!carritoContador) return;
    carritoContador.animate(
        [{ transform: "scale(1)" }, { transform: "scale(1.45)" }, { transform: "scale(1)" }],
        { duration: 350 }
    );
}

/* =========================================================
   CATEGORÍAS
   ========================================================= */

botonesCategoria.forEach(boton => {
    boton.addEventListener("click", () => {
        const categoria = boton.dataset.categoria;

        botonesCategoria.forEach(btn => btn.classList.remove("activo"));
        boton.classList.add("activo");

        mostrarProductos(categoria);

        if (window.innerWidth < 768) {
            document.querySelector(".productos")?.scrollIntoView({ behavior: "smooth", block: "start" });
        }
    });
});

/* =========================================================
   COMBO
   (El precio/nombre viajan en data-* del botón, tomados del
   Combo activo que Django renderizó en el HTML.)
   ========================================================= */

if (btnCombo) {
    btnCombo.addEventListener("click", () => {
        const id = btnCombo.dataset.comboId;
        const nombre = btnCombo.dataset.nombre;
        const precio = Number(btnCombo.dataset.precio);
        if (!id || !nombre || Number.isNaN(precio)) return;

        agregarLineaAlCarrito({ tipo: "combo", id, varianteId: null, varianteNombre: null, nombre, precio });
        mostrarCarrito();
    });
}

/* =========================================================
   CONTINUAR PEDIDO
   ========================================================= */

if (btnContinuarPedido) {
    btnContinuarPedido.addEventListener("click", () => {
        if (carrito.length === 0) return;

        const carritoElemento = document.getElementById("carrito");
        if (carritoElemento) {
            bootstrap.Offcanvas.getOrCreateInstance(carritoElemento).hide();
        }

        setTimeout(() => {
            if (modalPedido) modalPedido.show();
        }, 300);
    });
}

/* =========================================================
   TIPO DE PEDIDO
   ========================================================= */

document.querySelectorAll('input[name="tipoPedido"]').forEach(opcion => {
    opcion.addEventListener("change", () => {
        const domicilio = document.getElementById("datosDomicilio");
        const recoger = document.getElementById("datosRecogida");
        const esDomicilio = opcion.value === "domicilio";

        if (domicilio) domicilio.style.display = esDomicilio ? "block" : "none";
        if (recoger) recoger.style.display = esDomicilio ? "none" : "block";
    });
});

/* =========================================================
   MÉTODO DE PAGO
   ========================================================= */

document.querySelectorAll('input[name="metodoPago"]').forEach(opcion => {
    opcion.addEventListener("change", () => {
        const alerta = document.getElementById("alertaTarjeta");
        if (alerta) alerta.style.display = opcion.value === "tarjeta" ? "flex" : "none";

        const transferencia = document.getElementById("datosTransferencia");
        if (transferencia) transferencia.style.display = opcion.value === "transferencia" ? "block" : "none";
    });
});

/* =========================================================
   VALIDACIÓN
   ========================================================= */

function mostrarError(mensaje) {
    const error = document.getElementById("mensajeError");
    if (!error) return;

    error.textContent = mensaje;
    error.style.display = "block";
    error.scrollIntoView({ behavior: "smooth", block: "nearest" });
}

function ocultarError() {
    const error = document.getElementById("mensajeError");
    if (!error) return;
    error.style.display = "none";
    error.textContent = "";
}

function valorCampo(id) {
    return document.getElementById(id)?.value.trim() || "";
}

// Acepta números colombianos con o sin +57, espacios o guiones (7 a 13 dígitos "crudos").
function telefonoValido(telefono) {
    const soloDigitos = telefono.replace(/\D/g, "");
    return soloDigitos.length >= 7 && soloDigitos.length <= 13;
}

function validarPedido() {
    ocultarError();

    const tipoPedido = document.querySelector('input[name="tipoPedido"]:checked');
    if (!tipoPedido) {
        mostrarError("Selecciona si deseas domicilio o recoger el pedido.");
        return false;
    }

    const nombre = valorCampo("clienteNombre");
    if (!nombre) {
        mostrarError("Por favor escribe tu nombre.");
        return false;
    }

    const telefono = valorCampo("clienteTelefono");
    if (!telefono) {
        mostrarError("Por favor escribe tu número de teléfono.");
        return false;
    }
    if (!telefonoValido(telefono)) {
        mostrarError("El número de teléfono no parece válido. Revísalo, por favor.");
        return false;
    }

    if (tipoPedido.value === "domicilio") {
        const direccion = valorCampo("clienteDireccion");
        const barrio = valorCampo("clienteBarrio");

        if (!direccion || !barrio) {
            mostrarError("Para el domicilio necesitamos la dirección y el barrio.");
            return false;
        }
    } else {
        const punto = document.getElementById("puntoRecogida")?.value || "";
        if (!punto) {
            mostrarError("Selecciona el punto donde recogerás tu pedido.");
            return false;
        }
    }

    const metodoPago = document.querySelector('input[name="metodoPago"]:checked');
    if (!metodoPago) {
        mostrarError("Selecciona una forma de pago.");
        return false;
    }

    if (metodoPago.value === "tarjeta" && tipoPedido.value === "domicilio") {
        mostrarError("El pago con tarjeta está disponible únicamente en el punto físico.");
        return false;
    }

    return true;
}

/* =========================================================
   ENVIAR PEDIDO
   Crea el pedido en Django vía fetch (multipart, por el
   comprobante opcional). El backend recalcula precios desde
   la BD. El pedido NUNCA se envía por WhatsApp; WhatsApp solo
   aparece después, en la pantalla de confirmación, y solo
   para transferencias, únicamente para enviar el comprobante.
   ========================================================= */

function construirFormDataPedido() {
    const tipoPedido = document.querySelector('input[name="tipoPedido"]:checked').value;
    const metodoPago = document.querySelector('input[name="metodoPago"]:checked').value;

    const formData = new FormData();
    formData.append("cliente_nombre", valorCampo("clienteNombre"));
    formData.append("cliente_telefono", valorCampo("clienteTelefono"));
    formData.append("tipo_pedido", tipoPedido);
    formData.append("metodo_pago", metodoPago);
    formData.append("observaciones", valorCampo("clienteObservaciones"));

    if (tipoPedido === "domicilio") {
        formData.append("direccion", valorCampo("clienteDireccion"));
        formData.append("barrio", valorCampo("clienteBarrio"));
        formData.append("referencia", valorCampo("clienteReferencia"));
    } else {
        formData.append("punto_recogida", document.getElementById("puntoRecogida")?.value || "");
    }

    const archivoComprobante = document.getElementById("comprobantePago")?.files[0];
    if (archivoComprobante) formData.append("comprobante", archivoComprobante);

    const lineas = carrito.map(item => ({
        tipo: item.tipo,
        id: item.id,
        variante_id: item.varianteId,
        cantidad: item.cantidad,
    }));
    formData.append("carrito", JSON.stringify(lineas));

    return formData;
}

const btnEnviarPedido = document.getElementById("btnEnviarPedido");

if (btnEnviarPedido) {
    btnEnviarPedido.addEventListener("click", async () => {
        if (!validarPedido()) return;

        if (carrito.length === 0) {
            mostrarError("Tu carrito está vacío.");
            return;
        }

        btnEnviarPedido.disabled = true;

        try {
            const respuesta = await fetch("/pedidos/crear/", {
                method: "POST",
                headers: { "X-CSRFToken": obtenerCSRFToken() },
                body: construirFormDataPedido(),
            });

            const datos = await respuesta.json();

            if (!respuesta.ok || !datos.ok) {
                mostrarError(datos.error || "No pudimos registrar tu pedido. Intenta de nuevo.");
                btnEnviarPedido.disabled = false;
                return;
            }

            carrito = [];
            actualizarCarrito();
            modalPedido?.hide();
            window.location.href = datos.redirect_url;
        } catch (error) {
            console.error(error);
            mostrarError("No pudimos conectar con el servidor. Revisa tu conexión e intenta de nuevo.");
            btnEnviarPedido.disabled = false;
        }
    });
}

/* =========================================================
   LIMPIAR ERROR AL CERRAR MODAL
   ========================================================= */

if (modalPedidoElement) {
    modalPedidoElement.addEventListener("hidden.bs.modal", ocultarError);
}

/* =========================================================
   INICIAR
   ========================================================= */

async function iniciarApp() {
    try {
        await cargarProductos();
    } catch (error) {
        console.error(error);
        if (contenedorProductos) {
            contenedorProductos.innerHTML =
                '<p class="text-center text-white-50 py-5">No se pudo cargar el menú. Intenta recargar la página.</p>';
        }
        actualizarCarrito();
        return;
    }

    const primerBoton = botonesCategoria[0];
    if (primerBoton) {
        primerBoton.classList.add("activo");
        mostrarProductos(primerBoton.dataset.categoria);
    } else {
        // No hay categorías activas en la BD: no inventamos ninguna.
        mostrarProductos(null);
    }

    actualizarCarrito();
}

iniciarApp();
