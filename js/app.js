/* =========================================================
   COMO ARROZ - APP.JS
   Menú digital + carrito + pedidos por WhatsApp

   IMPORTANTE: este archivo depende de la variable global
   `productos`, definida en productos.js. Debe cargarse así
   en el HTML:
     <script src="js/productos.js"></script>
     <script src="js/app.js"></script>
   ========================================================= */

const NUMERO_WHATSAPP = "573224047068";
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
    const nombres = {
        arroces: "Arroces",
        espaguetis: "Espaguetis",
        carnes: "Carnes a la Plancha",
        hamburguesas: "Hamburguesas y Comidas Rápidas",
        mazorcadas: "Mazorcadas",
        "chop-suey": "Chop Suey",
        bebidas: "Bebidas",
        adicionales: "Adicionales",
        entradas: "Entradas"
    };
    return nombres[categoria] || categoria;
}

function iconoCategoria(categoria) {
    const iconos = {
        arroces: "bi-egg-fried",
        espaguetis: "bi-egg",
        carnes: "bi-fire",
        hamburguesas: "bi-burger",
        mazorcadas: "bi-circle",
        "chop-suey": "bi-bowl-hot",
        bebidas: "bi-cup-straw",
        adicionales: "bi-plus-circle",
        entradas: "bi-box2-heart"
    };
    return iconos[categoria] || "bi-egg-fried";
}

function tieneVariantes(producto) {
    return Array.isArray(producto.variantes) && producto.variantes.length > 0;
}

function precioDesde(producto) {
    return tieneVariantes(producto)
        ? Math.min(...producto.variantes.map(variante => variante.precio))
        : producto.precio;
}

function obtenerLineaId(id, variante = null) {
    const texto = variante
        ? String(variante).toLowerCase().trim().replace(/\s+/g, "-")
        : "normal";
    return `${id}-${texto}`;
}

function obtenerProductoPorId(id) {
    return productos.find(producto => producto.id === id);
}

/* =========================================================
   MOSTRAR PRODUCTOS
   ========================================================= */

function mostrarProductos(categoria = "arroces") {
    if (!contenedorProductos) return;

    const lista = productos.filter(producto => producto.categoria === categoria);

    if (tituloCategoria) tituloCategoria.textContent = nombreCategoria(categoria);
    if (cantidadProductos) cantidadProductos.textContent = lista.length;

    contenedorProductos.innerHTML = "";

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

function crearTarjetaProducto(producto) {
    const nombre = escaparHTML(producto.nombre);
    const descripcion = escaparHTML(producto.descripcion);
    const etiqueta = escaparHTML(producto.etiqueta || "");

    const precioHTML = tieneVariantes(producto)
        ? `Desde ${formatoPrecio(precioDesde(producto))}`
        : formatoPrecio(producto.precio);

    const tarjeta = document.createElement("div");
    tarjeta.className = "col-12 col-sm-6 col-lg-4";

    tarjeta.innerHTML = `
        <div class="producto-card">
            <div class="producto-imagen">
                <img
                    src="${producto.imagen}"
                    alt="${nombre}"
                    class="producto-foto"
                    loading="lazy"
                    decoding="async"
                    width="1200"
                    height="800"
                >
                <div class="producto-imagen-placeholder" style="display:none;">
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

    // Fallback de imagen (WebP -> JPG -> placeholder) sin usar onerror inline en el HTML.
    const img = tarjeta.querySelector(".producto-foto");
    img.addEventListener("error", function manejarErrorImagen() {
        if (img.dataset.fallback !== "1") {
            img.dataset.fallback = "1";
            img.src = producto.imagenOriginal;
        } else {
            img.removeEventListener("error", manejarErrorImagen);
            img.style.display = "none";
            img.nextElementSibling.style.display = "flex";
        }
    });

    // Agregar al carrito sin usar onclick inline.
    tarjeta.querySelector(".btn-agregar").addEventListener("click", () => {
        agregarAlCarrito(producto.id);
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
    agregarProductoAlCarrito(productoPendiente, variante.nombre, variante.precio);

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

    agregarProductoAlCarrito(producto);
    mostrarCarrito();
}

function agregarProductoAlCarrito(producto, variante = null, precio = null) {
    const precioFinal = precio ?? producto.precio;
    const lineaId = obtenerLineaId(producto.id, variante);
    const existente = carrito.find(item => item.lineaId === lineaId);

    if (existente) {
        existente.cantidad++;
    } else {
        carrito.push({
            lineaId,
            id: producto.id,
            nombre: producto.nombre,
            variante,
            precio: precioFinal,
            cantidad: 1
        });
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
                ${producto.variante ? `<div class="carrito-item-variante">${escaparHTML(producto.variante)}</div>` : ""}
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
   (Antes duplicaba a mano la lógica de agregarProductoAlCarrito
   y usaba un precio distinto al mostrado en el HTML. Ahora el
   combo es un producto más — con UN solo precio, definido en
   productos.js — y reutiliza la misma función que todo lo demás.)
   ========================================================= */

if (btnCombo) {
    btnCombo.addEventListener("click", () => {
        const combo = obtenerProductoPorId(100);
        if (!combo) return;

        agregarProductoAlCarrito(combo);
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
   WHATSAPP
   ========================================================= */

function generarMensajeWhatsApp() {
    const tipoPedido = document.querySelector('input[name="tipoPedido"]:checked')?.value;
    const metodoPago = document.querySelector('input[name="metodoPago"]:checked')?.value;

    if (!tipoPedido || !metodoPago) return "";

    const total = calcularTotal();

    let mensaje = "Hola, Como Arroz 👋\n\nQuiero realizar el siguiente pedido:\n\n";

    carrito.forEach(producto => {
        const variante = producto.variante ? ` — ${producto.variante}` : "";
        const subtotal = producto.precio * producto.cantidad;
        mensaje += `🍽️ ${producto.nombre}${variante} x${producto.cantidad} — ${formatoPrecio(subtotal)}\n`;
    });

    mensaje += `\n💰 TOTAL: ${formatoPrecio(total)}\n\n`;

    if (tipoPedido === "domicilio") {
        mensaje += "🛵 TIPO DE PEDIDO: DOMICILIO\n\n";
        mensaje += `👤 Nombre: ${valorCampo("clienteNombre")}\n`;
        mensaje += `📞 Teléfono: ${valorCampo("clienteTelefono")}\n`;
        mensaje += `🏠 Dirección: ${valorCampo("clienteDireccion")}\n`;
        mensaje += `📍 Barrio: ${valorCampo("clienteBarrio")}\n`;

        const referencia = valorCampo("clienteReferencia");
        if (referencia) mensaje += `📌 Referencia: ${referencia}\n`;
    } else {
        mensaje += "🏪 TIPO DE PEDIDO: RECOGER EN EL RESTAURANTE\n\n";
        mensaje += `👤 Nombre: ${valorCampo("clienteNombre")}\n`;
        mensaje += `📞 Teléfono: ${valorCampo("clienteTelefono")}\n`;
        mensaje += `📍 Punto de recogida: ${document.getElementById("puntoRecogida")?.value || ""}\n`;
    }

    const nombresPago = { efectivo: "Efectivo", transferencia: "Transferencia", tarjeta: "Tarjeta" };
    mensaje += `\n💳 FORMA DE PAGO: ${nombresPago[metodoPago] || metodoPago}\n`;

    const observaciones = valorCampo("clienteObservaciones");
    if (observaciones) mensaje += `\n📝 Observaciones: ${observaciones}\n`;

    return mensaje + "\n¿Me confirman el pedido, por favor? 😊";
}

const btnEnviarWhatsApp = document.getElementById("btnEnviarWhatsApp");

if (btnEnviarWhatsApp) {
    btnEnviarWhatsApp.addEventListener("click", () => {
        if (!validarPedido()) return;

        if (carrito.length === 0) {
            mostrarError("Tu carrito está vacío.");
            return;
        }

        const mensaje = generarMensajeWhatsApp();
        if (!mensaje) {
            mostrarError("No fue posible generar el pedido.");
            return;
        }

        const url = `https://wa.me/${NUMERO_WHATSAPP}?text=${encodeURIComponent(mensaje)}`;
        window.open(url, "_blank", "noopener,noreferrer");

        // Pedido enviado: limpiamos el carrito para el próximo pedido.
        carrito = [];
        actualizarCarrito();
        modalPedido?.hide();
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

botonesCategoria.forEach(boton => {
    if (boton.dataset.categoria === "arroces") boton.classList.add("activo");
});

mostrarProductos("arroces");
actualizarCarrito();