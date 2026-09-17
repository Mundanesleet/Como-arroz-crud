/* =========================================================
   COMO ARROZ - PRODUCTOS.JS
   Catálogo de productos del menú.
   Este archivo solo contiene DATOS. La lógica vive en app.js.
   Debe cargarse en el HTML ANTES de app.js:
   <script src="js/productos.js"></script>
   <script src="js/app.js"></script>
   ========================================================= */

function crearProducto(id, nombre, categoria, imagen, descripcion, precio, etiqueta = "") {
    const base = `img/${categoria}/${imagen}`;
    return {
        id,
        nombre,
        categoria,
        ...(Array.isArray(precio) ? { variantes: precio } : { precio }),
        imagen: `img/web/${categoria}/${imagen}.webp`,
        imagenOriginal: `${base}.jpg`,
        descripcion,
        etiqueta
    };
}

const productos = [
    // ARROCES
    crearProducto(1, "Arroz Tailandés", "arroces", "arroz-thai",
        "Arroz frito al wok con lomo de cerdo, carne desmechada, camarones, raíces, salsa teriyaki y vegetales frescos.",
        [{ nombre: "¼ porción", precio: 27000 }, { nombre: "½ porción", precio: 40000 }, { nombre: "Caja", precio: 60000 }], "RECOMENDADO"),

    crearProducto(2, "Arroz Chino", "arroces", "arroz-chino",
        "Arroz frito al wok con vegetales frescos, raíces, lomo de cerdo, pechuga en trozos, camarones salteados y salsa de soya china.",
        [{ nombre: "¼ porción", precio: 27000 }, { nombre: "½ porción", precio: 40000 }, { nombre: "Caja", precio: 60000 }]),

    crearProducto(3, "Arroz Ranchero", "arroces", "arroz-ranchero",
        "Arroz frito al wok con jamón, salchicha llanera, lomo de cerdo, maíz tierno y vegetales frescos salteados.",
        [{ nombre: "¼ porción", precio: 27000 }, { nombre: "½ porción", precio: 40000 }, { nombre: "Caja", precio: 60000 }], "MÁS PEDIDO"),

    crearProducto(4, "Arroz Italiano", "arroces", "arroz-italiano",
        "Arroz preparado con carne desmechada, pechuga en trozos, salchicha llanera, queso, salsa italiana y salsa de soya.",
        [{ nombre: "¼ porción", precio: 27000 }, { nombre: "½ porción", precio: 40000 }, { nombre: "Caja", precio: 60000 }]),

    crearProducto(5, "Arroz Mexicano", "arroces", "arroz-mexicano",
        "Arroz frito al wok preparado con vegetales, salchicha llanera, jamón ahumado, jalapeños, lomo de cerdo y doritos.",
        [{ nombre: "¼ porción", precio: 27000 }, { nombre: "½ porción", precio: 40000 }, { nombre: "Caja", precio: 60000 }]),

    crearProducto(6, "Arroz Queso y Jamón", "arroces", "arroz-queso-jamon",
        "Arroz preparado con queso y jamón, con carne y pollo en trozos y salsa de la casa.",
        [{ nombre: "¼ porción", precio: 27000 }, { nombre: "½ porción", precio: 40000 }, { nombre: "Caja", precio: 60000 }]),

    crearProducto(7, "Arroz Vegetariano", "arroces", "arroz-vegetariano",
        "Arroz preparado con maíz tierno, zanahoria, pimentón, calabacín, cebolla en julianas, brócoli, coliflor y queso.",
        [{ nombre: "¼ porción", precio: 27000 }, { nombre: "½ porción", precio: 40000 }, { nombre: "Caja", precio: 60000 }], "VEGETARIANO"),

    crearProducto(8, "Arroz Demasiadas Carnes", "arroces", "arroz-demasiadas-carnes",
        "Arroz frito al wok con una preparación de todas las carnes: lomo de cerdo, pechuga, jamón, salchicha y carne de res desmechada con salsa de soya y BBQ.",
        [{ nombre: "¼ porción", precio: 38000 }, { nombre: "½ porción", precio: 51000 }, { nombre: "Caja", precio: 75000 }], "🔥 ESPECIAL"),

    crearProducto(9, "Arroz con Camarones", "arroces", "arroz-camarones",
        "Arroz preparado con vegetales frescos, pollo en trozos, lomo de cerdo y camarón tigre.",
        [{ nombre: "¼ porción", precio: 38000 }, { nombre: "½ porción", precio: 51000 }, { nombre: "Caja", precio: 75000 }], "🦐 ESPECIAL"),

    crearProducto(10, "Arroz Mixto", "arroces", "arroz-mixto",
        "Arroz preparado con vegetales frescos, raíces, plátano maduro, maíz, tocineta, chicharrón, pollo y chorizo.",
        [{ nombre: "¼ porción", precio: 38000 }, { nombre: "½ porción", precio: 51000 }, { nombre: "Caja", precio: 75000 }], "ESPECIAL"),

    // ESPAGUETIS
    crearProducto(11, "Espagueti Vegetariano", "espaguetis", "espagueti-vegetariano",
        "Delicioso espagueti con maíz tierno, raíces, zanahoria, pimentón, calabacín, brócoli, champiñones, coliflor y queso.",
        28000, "VEGETARIANO"),

    crearProducto(12, "Espagueti Tailandés", "espaguetis", "espagueti-thai",
        "Delicioso espagueti preparado con carne desmechada, camarones, vegetales frescos, queso y salsa de la casa.",
        28000, "RECOMENDADO"),

    crearProducto(13, "Espagueti Ranchero", "espaguetis", "espagueti-ranchero",
        "Espagueti en salsa de la casa con salchicha llanera, jamón ahumado, maíz tierno, queso y vegetales frescos.",
        28000),

    crearProducto(14, "Espagueti Mexicano", "espaguetis", "espagueti-mexicano",
        "Espagueti en salsa de la casa con salchicha llanera, jamón, jalapeños, queso y vegetales frescos.",
        28000),

    crearProducto(15, "Espagueti Italiano", "espaguetis", "espagueti-italiano",
        "Espagueti con queso, vegetales, carne desmechada, pechuga en trozos y salsa de la casa.",
        28000),

    crearProducto(16, "Espagueti Demasiadas Carnes", "espaguetis", "espagueti-demasiadas-carnes",
        "Espagueti con salsa de la casa, vegetales frescos y una cama de carnes picadas, salchicha, cerdo, jamón, carne desmechada, pechuga en trozos y queso.",
        43000, "🔥 ESPECIAL"),

    crearProducto(17, "Espagueti Camarones", "espaguetis", "espagueti-camarones",
        "Espagueti con pechuga en trozos, vegetales frescos y una cama de camarones de primera.",
        43000, "🦐 ESPECIAL"),

    // CARNES
    crearProducto(18, "Churrasco", "carnes", "churrasco",
        "Lomo de res de 270 gramos con ensalada fría y papas a la francesa.", 33000),

    crearProducto(19, "Pechuga a la Plancha", "carnes", "pechuga-plancha",
        "Filete de pechuga de 270 gramos con ensalada fría y papas a la francesa.", 27500),

    crearProducto(20, "Lomo de Cerdo", "carnes", "lomo-cerdo",
        "Lomo de cerdo de 270 gramos con ensalada fría y papas a la francesa.", 33000),

    crearProducto(21, "Picada de Carnes", "carnes", "picada-carnes",
        "Lomo de cerdo, lomo de res, pechuga, chorizo, salchicha llanera, papas a la francesa, plátanos y huevos de codorniz.",
        38000, "PARA COMPARTIR"),

    crearProducto(22, "Costillas BBQ", "carnes", "costillas-bbq",
        "400 gramos de costillas acompañadas de papa a la francesa.", 38000),

    crearProducto(23, "Ceviche de Camarones", "carnes", "ceviche-camarones",
        "250 gramos de camarón tigre con salsa de tomate, mayonesa, ajo, ají, pimentón, cebolla y cilantro, acompañado con galletas saltín y jugo de naranja.",
        25000, "🦐"),

    crearProducto(24, "Ceviche Especial", "carnes", "ceviche-especial",
        "Ceviche con ingredientes frescos, camarón tigre, pimentón, cilantro, salsa de ajo y sal, acompañado con galletas saltín y jugo de naranja.",
        29000, "🦐 ESPECIAL"),

    // MAZORCADAS
    crearProducto(25, "Mazorcada de Pollo", "mazorcadas", "mazorcada-pollo",
        "Pechuga en trozos, maíz tierno, queso, ripio de papa y salsas.", 28500),

    crearProducto(26, "Mazorcada de Carnes", "mazorcadas", "mazorcada-carnes",
        "Carne desmechada, maíz tierno, queso, ripio de papa y salsas.", 28500),

    crearProducto(27, "Mazorcada Mixta", "mazorcadas", "mazorcada-mixta",
        "Carne desmechada, pechuga en trozos, tocineta, maíz tierno, queso, ripio de papa y salsas.",
        32000, "MÁS PEDIDO"),

    crearProducto(28, "Mazorcada Media Mixta", "mazorcadas", "mazorcada-media-mixta",
        "Carne desmechada, pechuga en trozos, tocineta, maíz tierno, queso, ripio de papa y salsas.", 20000),

    // HAMBURGUESAS Y COMIDAS RÁPIDAS
    crearProducto(29, "Hamburguesa Sencilla", "hamburguesas", "hamburguesa-sencilla",
        "Pan o patacón, carne de res o pollo apanado, lechuga, tomate, cebolla sofrita y salsas.",
        [{ nombre: "Pan", precio: 19000 }, { nombre: "Patacón", precio: 20000 }]),

    crearProducto(30, "Hamburguesa Especial", "hamburguesas", "hamburguesa-especial",
        "Doble carne de res, pollo apanado o mixta, doble queso, lechuga, tomate, cebolla sofrita y champiñones.",
        [{ nombre: "Pan", precio: 27500 }, { nombre: "Patacón", precio: 29000 }], "MÁS PEDIDO"),

    crearProducto(31, "Choripapa", "hamburguesas", "choripapa",
        "300 gramos de papa a la francesa, chorizo de Las Brisas, queso y huevos de codorniz.", 22000),

    crearProducto(32, "Chorizo", "hamburguesas", "chorizo",
        "Chorizo de Las Brisas acompañado con 150 gramos de papas a la francesa, lechuga y tomate.", 10000),

    crearProducto(33, "Nuggets de Pollo", "hamburguesas", "nuggets-pollo",
        "Nuggets de pollo acompañados con papas a la francesa.", 19000),

    crearProducto(34, "Salchipapa Especial", "hamburguesas", "salchipapa-especial",
        "300 gramos de papa a la francesa, salchicha llanera, queso y huevo de codorniz.", 21000),

    crearProducto(35, "Salchipapa Junior", "hamburguesas", "salchipapa-junior",
        "Papa a la francesa, salchicha llanera, queso y huevo de codorniz.", 13000),

    // CHOP SUEY
    crearProducto(36, "Chop Suey Vegetales", "chop-suey", "chop-suey-vegetales",
        "Vegetales frescos: cebolla, brócoli, coliflor, pimentón, calabacín, raíces y zanahoria en delicioso caldo de pollo.", 22000),

    crearProducto(37, "Chop Suey con Lomo de Cerdo", "chop-suey", "chop-suey-cerdo",
        "Chop Suey de vegetales acompañado de lomo de cerdo.", 30000),

    crearProducto(38, "Chop Suey con Pollo", "chop-suey", "chop-suey-pollo",
        "Chop Suey de vegetales acompañado de pollo.", 30000),

    crearProducto(39, "Chop Suey Mixto", "chop-suey", "chop-suey-mixto",
        "Chop Suey mixto de pollo, cerdo y camarón.", 34000, "RECOMENDADO"),

    // BEBIDAS
    crearProducto(40, "Jugo Natural en Agua", "bebidas", "jugo-agua",
        "Sabores: fresa, mora, maracuyá, mango, lulo, guanábana y limonada.",
        [{ nombre: "Vaso 22 oz", precio: 6500 }, { nombre: "Jarra 40 oz", precio: 12000 }]),

    crearProducto(41, "Jugo Natural en Leche", "bebidas", "jugo-leche",
        "Sabores: fresa, mora, maracuyá, mango, lulo, guanábana y limonada.",
        [{ nombre: "Vaso 22 oz", precio: 8500 }, { nombre: "Jarra 40 oz", precio: 16000 }]),

    crearProducto(42, "Jugo Hit Personal", "bebidas", "hit-personal", "Jugo Hit personal.", 4500),
    crearProducto(43, "Jugo Hit Litro", "bebidas", "hit-litro", "Jugo Hit en presentación de litro.", 6500),
    crearProducto(44, "Gaseosa Tropikola 400 ml", "bebidas", "tropikola-400", "Gaseosa Tropikola de 400 ml.", 5500),
    crearProducto(45, "Gaseosa PET 400 ml", "bebidas", "gaseosa-pet-400", "Gaseosa PET de 400 ml.", 5000),
    crearProducto(46, "Gaseosa 1.5 L", "bebidas", "gaseosa-1-5", "Gaseosa familiar de 1.5 litros.", 9500),
    crearProducto(47, "Gaseosa 3 L", "bebidas", "gaseosa-3", "Gaseosa familiar de 3 litros.", 13000),
    crearProducto(48, "Power", "bebidas", "power", "Bebida Power.", 5500),
    crearProducto(49, "Agua", "bebidas", "agua", "Botella de agua.", 3000),
    crearProducto(50, "Agua con Gas", "bebidas", "agua-gas", "Botella de agua con gas.", 4000),
    crearProducto(51, "Cerveza Águila o Poker", "bebidas", "aguila-poker", "Presentación disponible según existencia.", 5000),
    crearProducto(52, "Cerveza Club Colombia", "bebidas", "club-colombia", "Cerveza Club Colombia.", 6000),
    crearProducto(53, "Cerveza Corona / Heineken", "bebidas", "corona-heineken", "Presentación disponible según existencia.", 7000),
    crearProducto(54, "Limonada de Coco", "bebidas", "limonada-coco", "Limonada de coco.", 13000, "NUEVA"),
    crearProducto(55, "Limonada de Cereza", "bebidas", "limonada-cereza", "Limonada de cereza.", 13000, "NUEVA"),
    crearProducto(56, "Malteada", "bebidas", "malteada", "Malteada de la casa.", 13000, "NUEVA"),
    crearProducto(57, "Limonada Mango Biche", "bebidas", "limonada-mango-biche", "Limonada de mango biche.", 13000, "NUEVA"),
    crearProducto(58, "Maltiricrunch", "bebidas", "maltiricrunch", "Nueva bebida de la casa con topping especial.", 16500, "NUEVA"),

    // ADICIONALES
    crearProducto(59, "Papas a la Francesa 125 g", "adicionales", "papas-125", "Porción de papas a la francesa de 125 gramos.", 4500),
    crearProducto(60, "Papas a la Francesa 250 g", "adicionales", "papas-250", "Porción de papas a la francesa de 250 gramos.", 8000),
    crearProducto(61, "Yuca Frita", "adicionales", "yuca", "Porción de yuca frita.", 4500),
    crearProducto(62, "Patacón", "adicionales", "patacon", "Porción de patacón.", 5500),
    crearProducto(63, "Camarón Tigre 250 g", "adicionales", "camaron", "Porción de camarón tigre de 250 gramos.", 19000, "🦐"),
    crearProducto(64, "Queso", "adicionales", "queso", "Porción adicional de queso.", 3000),
    crearProducto(65, "Jalapeños", "adicionales", "jalapenos", "Porción adicional de jalapeños.", 2200),
    crearProducto(66, "Maíz Tierno", "adicionales", "maiz-tierno", "Porción adicional de maíz tierno.", 6000),
    crearProducto(67, "Ensalada Fría", "adicionales", "ensalada", "Porción de ensalada fría.", 7500),
    crearProducto(68, "Huevos de Codorniz", "adicionales", "huevos-codorniz", "Porción de huevos de codorniz.", 6000),
    crearProducto(69, "Tocineta", "adicionales", "tocineta", "Porción adicional de tocineta.", 4000),
    crearProducto(70, "Empaque", "adicionales", "empaque", "Empaque para llevar.", 1500),

    // ENTRADAS
    crearProducto(71, "Rollos Primavera (Lumpias) x2", "entradas", "lumpias", "2 rollos primavera (lumpias).", 7000, "ENTRADA"),
    crearProducto(72, "Rollos Primavera (Lumpias) x4", "entradas", "lumpias", "4 rollos primavera (lumpias).", 13000, "ENTRADA"),
    crearProducto(73, "Plato de Arroz Demasiadas Carnes", "entradas", "plato-arroz-demasiadas-carnes",
        "Arroz frito al wok con una preparación especial de todas las carnes, con salsa de soya y BBQ.", 21000, "ESPECIAL"),

    // COMBO — antes vivía "suelto" en app.js con un precio distinto al mostrado en el HTML.
    // Ahora es un producto más: una sola fuente de verdad para su precio.
    crearProducto(100, "Combo de lunes a viernes", "combos", "combo",
        "Arroz de la casa, papas a la francesa, ensalada, gaseosa de 250 ml y filete de carne de 125 gr.",
        12300)
];