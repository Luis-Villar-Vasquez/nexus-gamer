// ==========================================
// NEXUS GAMER - JAVASCRIPT PRINCIPAL
// ==========================================


// ==========================================
// FILTROS DE PRODUCTOS
// ==========================================

const botonesFiltro = document.querySelectorAll(".filtro");
const productos = document.querySelectorAll(".producto-card");

botonesFiltro.forEach((boton) => {

    boton.addEventListener("click", () => {

        // Quitar selección anterior
        botonesFiltro.forEach((btn) => {
            btn.classList.remove("activo");
        });

        // Activar botón seleccionado
        boton.classList.add("activo");

        const categoriaSeleccionada =
            boton.dataset.categoria;


        // Filtrar productos
        productos.forEach((producto) => {

            const categoriaProducto =
                producto.dataset.categoria;

            if (
                categoriaSeleccionada === "Todos" ||
                categoriaProducto === categoriaSeleccionada
            ) {

                producto.style.display = "block";

            } else {

                producto.style.display = "none";

            }

        });

    });

});

// ==========================================
// BUSCADOR DE PRODUCTOS
// ==========================================

const btnBuscar =
    document.getElementById("btn-buscar");

const buscadorPanel =
    document.getElementById("buscador-panel");

const buscadorInput =
    document.getElementById("buscador-input");

const cerrarBuscador =
    document.getElementById("cerrar-buscador");

const resultadoBusqueda =
    document.getElementById("resultado-busqueda");


// ==========================================
// ABRIR BUSCADOR
// ==========================================

btnBuscar.addEventListener("click", () => {

    buscadorPanel.classList.toggle("abierto");

    if (
        buscadorPanel.classList.contains("abierto")
    ) {

        setTimeout(() => {
            buscadorInput.focus();
        }, 200);

    }

});


// ==========================================
// CERRAR BUSCADOR
// ==========================================

cerrarBuscador.addEventListener("click", () => {

    buscadorPanel.classList.remove("abierto");

});


// ==========================================
// BUSCAR EN TIEMPO REAL
// ==========================================

buscadorInput.addEventListener("input", () => {

    const texto =
        buscadorInput.value
            .toLowerCase()
            .trim();

    let encontrados = 0;


    productos.forEach((producto) => {

        const contenido =
            producto.textContent
                .toLowerCase();

        if (
            contenido.includes(texto)
        ) {

            producto.style.display = "block";

            encontrados++;

        } else {

            producto.style.display = "none";

        }

    });


    // Si no escribió nada
    if (texto === "") {

        resultadoBusqueda.textContent = "";

        botonesFiltro.forEach((btn) => {
            btn.classList.remove("activo");
        });

        botonesFiltro[0].classList.add("activo");

        productos.forEach((producto) => {
            producto.style.display = "block";
        });

        return;

    }


    // Mostrar cantidad encontrada

    if (encontrados === 1) {

        resultadoBusqueda.textContent =
            "1 producto encontrado";

    } else {

        resultadoBusqueda.textContent =
            `${encontrados} productos encontrados`;

    }


    // Llevar al usuario a productos
    if (encontrados > 0) {

        document
            .getElementById("productos")
            .scrollIntoView({
                behavior: "smooth"
            });

    }

});


// ==========================================
// CERRAR CON ESC
// ==========================================

document.addEventListener("keydown", (event) => {

    if (event.key === "Escape") {

        buscadorPanel.classList.remove("abierto");

    }

});


// ==========================================
// CARRITO DE COMPRAS
// ==========================================

const btnAbrirCarrito =
    document.getElementById("btn-abrir-carrito");

const carritoPanel =
    document.getElementById("carrito-panel");

const carritoOverlay =
    document.getElementById("carrito-overlay");

const cerrarCarritoBtn =
    document.getElementById("cerrar-carrito");

const seguirComprando =
    document.getElementById("seguir-comprando");

const carritoProductos =
    document.getElementById("carrito-productos");

const contadorCarrito =
    document.getElementById("contador-carrito");

const carritoSubtotal =
    document.getElementById("carrito-subtotal");

const botonesCarrito =
    document.querySelectorAll(".btn-carrito");


// Recuperar carrito guardado
let carrito =
    JSON.parse(localStorage.getItem("nexusCarrito")) || [];


// ==========================================
// ABRIR / CERRAR
// ==========================================

function abrirCarrito() {

    carritoPanel.classList.add("abierto");

    carritoOverlay.classList.add("activo");

    document.body.classList.add("carrito-abierto");

}


function cerrarCarrito() {

    carritoPanel.classList.remove("abierto");

    carritoOverlay.classList.remove("activo");

    document.body.classList.remove("carrito-abierto");

}


btnAbrirCarrito.addEventListener(
    "click",
    abrirCarrito
);


cerrarCarritoBtn.addEventListener(
    "click",
    cerrarCarrito
);


carritoOverlay.addEventListener(
    "click",
    cerrarCarrito
);


seguirComprando.addEventListener(
    "click",
    cerrarCarrito
);


// ESC
document.addEventListener("keydown", (event) => {

    if (event.key === "Escape") {
        cerrarCarrito();
    }

});


// ==========================================
// AGREGAR PRODUCTO
// ==========================================

botonesCarrito.forEach((boton) => {

    boton.addEventListener("click", () => {

        if (boton.disabled) {
            return;
        }

       const tarjeta =
    boton.closest(
        ".producto-card, .oferta-card, .novedad-card"
    );

let imagen = null;

if (tarjeta) {
    imagen = tarjeta.querySelector(
        ".producto-foto img, .oferta-imagen img, .novedad-imagen img"
    );
}


        const producto = {

            id: boton.dataset.id,

            nombre:
                boton.dataset.nombre,

            precio:
                Number(boton.dataset.precio),

            stock:
                Number(boton.dataset.stock),

            imagen:
                imagen
                    ? imagen.src
                    : ""

        };


        const existente =
            carrito.find(
                (item) =>
                    item.id === producto.id
            );


        if (existente) {

            if (
                existente.cantidad <
                producto.stock
            ) {

                existente.cantidad++;

            }

        } else {

            carrito.push({
                ...producto,
                cantidad: 1
            });

        }


        guardarCarrito();

        renderizarCarrito();

        abrirCarrito();

    });

});


// ==========================================
// GUARDAR
// ==========================================

function guardarCarrito() {

    localStorage.setItem(
        "nexusCarrito",
        JSON.stringify(carrito)
    );

}


// ==========================================
// RENDERIZAR CARRITO
// ==========================================

function renderizarCarrito() {

    carritoProductos.innerHTML = "";


    // Carrito vacío
    if (carrito.length === 0) {

        carritoProductos.innerHTML = `

            <div class="carrito-vacio">

                <div class="carrito-vacio-icono">
                    🛒
                </div>

                <h3>
                    Tu carrito está vacío
                </h3>

                <p>
                    Agrega productos gamer y
                    arma tu próximo setup.
                </p>

            </div>

        `;

    }


    // Productos
    carrito.forEach((producto) => {

        const item =
            document.createElement("div");

        item.classList.add("carrito-item");


        item.innerHTML = `

            <div class="carrito-item-imagen">

                ${
                    producto.imagen
                        ? `
                        <img
                            src="${producto.imagen}"
                            alt="${producto.nombre}">
                        `
                        : "🎮"
                }

            </div>


            <div class="carrito-item-info">

                <h4>
                    ${producto.nombre}
                </h4>

                <span class="carrito-item-precio">

                    S/
                    ${producto.precio.toFixed(2)}

                </span>


                <div class="carrito-cantidad">

                    <button
                        type="button"
                        onclick="cambiarCantidad(
                            '${producto.id}',
                            -1
                        )">

                        −

                    </button>


                    <span>
                        ${producto.cantidad}
                    </span>


                    <button
                        type="button"
                        onclick="cambiarCantidad(
                            '${producto.id}',
                            1
                        )">

                        +

                    </button>

                </div>

            </div>


            <button
                type="button"
                class="eliminar-carrito"
                onclick="eliminarProducto(
                    '${producto.id}'
                )"
                aria-label="Eliminar producto">

                ✕

            </button>

        `;


        carritoProductos.appendChild(item);

    });


    actualizarResumen();

}


// ==========================================
// CAMBIAR CANTIDAD
// ==========================================

function cambiarCantidad(id, cambio) {

    const producto =
        carrito.find(
            (item) => item.id === id
        );


    if (!producto) {
        return;
    }


    producto.cantidad += cambio;


    // Si llega a cero, eliminar
    if (producto.cantidad <= 0) {

        carrito =
            carrito.filter(
                (item) => item.id !== id
            );

    }


    // No superar stock
    else if (
        producto.cantidad >
        producto.stock
    ) {

        producto.cantidad =
            producto.stock;

    }


    guardarCarrito();

    renderizarCarrito();

}


// ==========================================
// ELIMINAR
// ==========================================

function eliminarProducto(id) {

    carrito =
        carrito.filter(
            (producto) =>
                producto.id !== id
        );


    guardarCarrito();

    renderizarCarrito();

}


// ==========================================
// CONTADOR + SUBTOTAL
// ==========================================

function actualizarResumen() {

    const cantidadTotal =
        carrito.reduce(
            (total, producto) =>
                total + producto.cantidad,
            0
        );


    const subtotal =
        carrito.reduce(
            (total, producto) =>
                total +
                (
                    producto.precio *
                    producto.cantidad
                ),
            0
        );


    contadorCarrito.textContent =
        cantidadTotal;


    carritoSubtotal.textContent =
        `S/ ${subtotal.toFixed(2)}`;

}


// ==========================================
// CARGAR CARRITO AL INICIAR
// ==========================================

renderizarCarrito();

// ==========================================
// FAVORITOS
// ==========================================

const botonesFavoritos =
    document.querySelectorAll(".favorito");


// Recuperar favoritos guardados
let favoritos =
    JSON.parse(
        localStorage.getItem("nexusFavoritos")
    ) || [];


// ==========================================
// GUARDAR FAVORITOS
// ==========================================

function guardarFavoritos() {

    localStorage.setItem(
        "nexusFavoritos",
        JSON.stringify(favoritos)
    );

}


// ==========================================
// ACTUALIZAR CORAZONES
// ==========================================

function actualizarFavoritos() {

    botonesFavoritos.forEach((boton) => {

        const id = boton.dataset.id;

        const esFavorito =
            favoritos.some(
                (producto) =>
                    producto.id === id
            );


        if (esFavorito) {

            boton.classList.add("activo");

            boton.textContent = "♥";

            boton.setAttribute(
                "aria-label",
                "Eliminar de favoritos"
            );

        } else {

            boton.classList.remove("activo");

            boton.textContent = "♡";

            boton.setAttribute(
                "aria-label",
                "Agregar a favoritos"
            );

        }

    });

}


// ==========================================
// CLICK EN CORAZÓN
// ==========================================

botonesFavoritos.forEach((boton) => {

    boton.addEventListener("click", () => {

        const tarjeta =
    boton.closest(
        ".producto-card, .novedad-card"
    );


        const id =
            boton.dataset.id;


        const existente =
            favoritos.find(
                (producto) =>
                    producto.id === id
            );


        // ----------------------------------
        // SI YA EXISTE → ELIMINAR
        // ----------------------------------

        if (existente) {

            favoritos =
                favoritos.filter(
                    (producto) =>
                        producto.id !== id
                );

        }


        // ----------------------------------
        // SI NO EXISTE → AGREGAR
        // ----------------------------------

        else {

            const imagen =
    tarjeta
        ? tarjeta.querySelector(
            ".producto-foto img, .novedad-imagen img"
        )
        : null;

            const nombre =
                boton.dataset.nombre;


            const precioElemento =
    tarjeta
        ? tarjeta.querySelector(
            ".btn-carrito"
        )
        : null;


            favoritos.push({

                id: id,

                nombre: nombre,

                precio:
                    precioElemento
                        ? Number(
                            precioElemento.dataset.precio
                        )
                        : 0,

                imagen:
                    imagen
                        ? imagen.src
                        : ""

            });

        }


        guardarFavoritos();

        actualizarFavoritos();

    });

});


// ==========================================
// CARGAR FAVORITOS AL INICIAR
// ==========================================

actualizarFavoritos();

// ==========================================
// PANEL DE USUARIO
// ==========================================

const btnUsuario =
    document.getElementById("btn-usuario");

const usuarioPanel =
    document.getElementById("usuario-panel");

const usuarioOverlay =
    document.getElementById("usuario-overlay");

const cerrarUsuarioBtn =
    document.getElementById("cerrar-usuario");

const listaFavoritos =
    document.getElementById("lista-favoritos");

const contadorFavoritos =
    document.getElementById("contador-favoritos");

const cantidadFavoritosTexto =
    document.getElementById("cantidad-favoritos-texto");

const usuarioCarrito =
    document.getElementById("usuario-carrito");

const contadorCarritoUsuario =
    document.getElementById("contador-carrito-usuario");


// ==========================================
// ABRIR / CERRAR
// ==========================================

function abrirUsuario() {

    renderizarFavoritosUsuario();

    actualizarContadoresUsuario();

    usuarioPanel.classList.add("abierto");

    usuarioOverlay.classList.add("activo");

    document.body.classList.add("carrito-abierto");
}


function cerrarUsuario() {

    usuarioPanel.classList.remove("abierto");

    usuarioOverlay.classList.remove("activo");

    document.body.classList.remove("carrito-abierto");
}


btnUsuario.addEventListener(
    "click",
    abrirUsuario
);


cerrarUsuarioBtn.addEventListener(
    "click",
    cerrarUsuario
);


usuarioOverlay.addEventListener(
    "click",
    cerrarUsuario
);


// ==========================================
// MOSTRAR FAVORITOS
// ==========================================

function renderizarFavoritosUsuario() {

    listaFavoritos.innerHTML = "";


    if (favoritos.length === 0) {

        listaFavoritos.innerHTML = `

            <div class="sin-favoritos">

                <span>♡</span>

                <h4>
                    Aún no tienes favoritos
                </h4>

                <p>
                    Guarda productos usando
                    el corazón.
                </p>

            </div>

        `;

        return;
    }


    favoritos.forEach((producto) => {

        const elemento =
            document.createElement("div");


        elemento.classList.add(
            "favorito-item"
        );


        elemento.innerHTML = `

            <div class="favorito-item-imagen">

                ${
                    producto.imagen
                    ? `
                        <img
                            src="${producto.imagen}"
                            alt="${producto.nombre}">
                      `
                    : "🎮"
                }

            </div>


            <div class="favorito-item-info">

                <h4>
                    ${producto.nombre}
                </h4>

                <strong>
                    S/ ${producto.precio.toFixed(2)}
                </strong>

            </div>


            <button
                type="button"
                class="eliminar-favorito"
                onclick="eliminarFavoritoUsuario(
                    '${producto.id}'
                )"
                aria-label="Eliminar favorito">

                ♥

            </button>

        `;


        listaFavoritos.appendChild(
            elemento
        );

    });

}


// ==========================================
// ELIMINAR DESDE PANEL
// ==========================================

function eliminarFavoritoUsuario(id) {

    favoritos =
        favoritos.filter(
            (producto) =>
                producto.id !== id
        );


    guardarFavoritos();

    actualizarFavoritos();

    renderizarFavoritosUsuario();

    actualizarContadoresUsuario();
}


// ==========================================
// CONTADORES
// ==========================================

function actualizarContadoresUsuario() {

    const cantidadFavoritos =
        favoritos.length;


    contadorFavoritos.textContent =
        cantidadFavoritos;


    cantidadFavoritosTexto.textContent =
        cantidadFavoritos === 1
            ? "1 producto"
            : `${cantidadFavoritos} productos`;


    const cantidadCarrito =
        carrito.reduce(
            (total, producto) =>
                total + producto.cantidad,
            0
        );


    contadorCarritoUsuario.textContent =
        cantidadCarrito;
}


// ==========================================
// ABRIR CARRITO DESDE USUARIO
// ==========================================

usuarioCarrito.addEventListener(
    "click",
    () => {

        cerrarUsuario();

        abrirCarrito();

    }
);


// ==========================================
// ESC
// ==========================================

document.addEventListener(
    "keydown",
    (event) => {

        if (event.key === "Escape") {
            cerrarUsuario();
        }

    }
);

// ==========================================
// NEXUS AI - CHATBOT
// ==========================================

const btnNexusAI =
    document.getElementById("btn-nexus-ai");

const nexusAIPanel =
    document.getElementById("nexus-ai-panel");

const cerrarNexusAI =
    document.getElementById("cerrar-nexus-ai");

const nexusAIForm =
    document.getElementById("nexus-ai-form");

const nexusAIInput =
    document.getElementById("nexus-ai-input");

const nexusAIMensajes =
    document.getElementById("nexus-ai-mensajes");

const nexusAIEnviar =
    document.getElementById("nexus-ai-enviar");

const sugerenciasNexusAI =
    document.querySelectorAll(
        ".nexus-ai-sugerencias button"
    );


// ==========================================
// ABRIR CHAT
// ==========================================

function abrirNexusAI() {

    nexusAIPanel.classList.add("abierto");

    btnNexusAI.classList.add("chat-abierto");

    setTimeout(() => {
        nexusAIInput.focus();
    }, 250);
}


// ==========================================
// CERRAR CHAT
// ==========================================

function cerrarPanelNexusAI() {

    nexusAIPanel.classList.remove("abierto");

    btnNexusAI.classList.remove("chat-abierto");
}


// ==========================================
// BOTONES ABRIR / CERRAR
// ==========================================

btnNexusAI.addEventListener(
    "click",
    abrirNexusAI
);


cerrarNexusAI.addEventListener(
    "click",
    cerrarPanelNexusAI
);


// Cerrar con ESC

document.addEventListener(
    "keydown",
    (event) => {

        if (event.key === "Escape") {
            cerrarPanelNexusAI();
        }

    }
);


// ==========================================
// MOSTRAR MENSAJE DEL USUARIO
// ==========================================

function mostrarMensajeUsuario(mensaje) {

    const elemento =
        document.createElement("div");

    elemento.classList.add(
        "mensaje-usuario"
    );

    const parrafo =
        document.createElement("p");

    parrafo.textContent = mensaje;

    elemento.appendChild(parrafo);

    nexusAIMensajes.appendChild(
        elemento
    );

    bajarChat();
}


// ==========================================
// MOSTRAR RESPUESTA DE NEXUS AI
// ==========================================

function mostrarMensajeAI(mensaje) {

    const elemento =
        document.createElement("div");

    elemento.classList.add(
        "mensaje-ai"
    );


    const avatar =
        document.createElement("div");

    avatar.classList.add(
        "mensaje-avatar"
    );

    avatar.textContent = "🤖";


    const contenido =
        document.createElement("div");

    contenido.classList.add(
        "mensaje-contenido"
    );


    const nombre =
        document.createElement("span");

    nombre.textContent =
        "NEXUS AI";


    const parrafo =
        document.createElement("p");

    parrafo.textContent = mensaje;


    contenido.appendChild(nombre);

    contenido.appendChild(parrafo);


    elemento.appendChild(avatar);

    elemento.appendChild(contenido);


    nexusAIMensajes.appendChild(
        elemento
    );


    bajarChat();
}


// ==========================================
// INDICADOR ESCRIBIENDO
// ==========================================

function mostrarEscribiendo() {

    eliminarEscribiendo();

    const escribiendo =
        document.createElement("div");

    escribiendo.classList.add(
        "nexus-ai-escribiendo"
    );

    escribiendo.id =
        "nexus-ai-escribiendo";


    escribiendo.innerHTML = `
        <span></span>
        <span></span>
        <span></span>
    `;


    nexusAIMensajes.appendChild(
        escribiendo
    );


    bajarChat();
}


function eliminarEscribiendo() {

    const escribiendo =
        document.getElementById(
            "nexus-ai-escribiendo"
        );

    if (escribiendo) {
        escribiendo.remove();
    }
}


// ==========================================
// BAJAR AUTOMÁTICAMENTE EL CHAT
// ==========================================

function bajarChat() {

    nexusAIMensajes.scrollTop =
        nexusAIMensajes.scrollHeight;
}


// ==========================================
// ENVIAR MENSAJE A FLASK / GEMINI
// ==========================================

async function enviarMensajeNexusAI(mensaje) {

    const texto =
        mensaje.trim();

    if (!texto) {
        return;
    }


    // Mostrar mensaje del usuario

    mostrarMensajeUsuario(texto);


    // Limpiar input

    nexusAIInput.value = "";


    // Bloquear mientras responde

    nexusAIInput.disabled = true;

    nexusAIEnviar.disabled = true;


    // Mostrar animación

    mostrarEscribiendo();


    try {

        const respuesta =
            await fetch("/api/chat", {

                method: "POST",

                headers: {
                    "Content-Type":
                        "application/json"
                },

                body: JSON.stringify({
                    mensaje: texto
                })

            });


        const datos =
            await respuesta.json();


        eliminarEscribiendo();


        if (!respuesta.ok) {

            mostrarMensajeAI(
                datos.respuesta ||
                "No pude procesar tu consulta."
            );

            return;
        }


        mostrarMensajeAI(
            datos.respuesta
        );


    } catch (error) {

        console.error(
            "Error NEXUS AI:",
            error
        );


        eliminarEscribiendo();


        mostrarMensajeAI(
            "No pude conectarme con el servidor. " +
            "Inténtalo nuevamente."
        );

    } finally {

        nexusAIInput.disabled = false;

        nexusAIEnviar.disabled = false;

        nexusAIInput.focus();

    }

}


// ==========================================
// FORMULARIO
// ==========================================

nexusAIForm.addEventListener(
    "submit",
    (event) => {

        event.preventDefault();

        const mensaje =
            nexusAIInput.value;

        enviarMensajeNexusAI(
            mensaje
        );

    }
);


// ==========================================
// PREGUNTAS RÁPIDAS
// ==========================================

sugerenciasNexusAI.forEach(
    (boton) => {

        boton.addEventListener(
            "click",
            () => {

                const pregunta =
                    boton.textContent.trim();

                enviarMensajeNexusAI(
                    pregunta
                );

            }
        );

    }
);



