const botonesFiltro = document.querySelectorAll(".filtro");
const productos = document.querySelectorAll(".producto-card");

botonesFiltro.forEach((boton) => {
    boton.addEventListener("click", () => {
        botonesFiltro.forEach((btn) => btn.classList.remove("activo"));
        boton.classList.add("activo");

        const categoriaSeleccionada = boton.dataset.categoria;

        productos.forEach((producto) => {
            const categoriaProducto = producto.dataset.categoria;

            producto.style.display =
                categoriaSeleccionada === "Todos" ||
                categoriaProducto === categoriaSeleccionada
                    ? "block"
                    : "none";
        });
    });
});

const btnBuscar = document.getElementById("btn-buscar");
const buscadorPanel = document.getElementById("buscador-panel");
const buscadorInput = document.getElementById("buscador-input");
const cerrarBuscador = document.getElementById("cerrar-buscador");
const resultadoBusqueda = document.getElementById("resultado-busqueda");

btnBuscar.addEventListener("click", () => {
    buscadorPanel.classList.toggle("abierto");

    if (buscadorPanel.classList.contains("abierto")) {
        setTimeout(() => buscadorInput.focus(), 200);
    }
});

cerrarBuscador.addEventListener("click", () => {
    buscadorPanel.classList.remove("abierto");
});

buscadorInput.addEventListener("input", () => {
    const texto = buscadorInput.value.toLowerCase().trim();
    let encontrados = 0;

    productos.forEach((producto) => {
        const contenido = producto.textContent.toLowerCase();

        if (contenido.includes(texto)) {
            producto.style.display = "block";
            encontrados++;
        } else {
            producto.style.display = "none";
        }
    });

    if (texto === "") {
        resultadoBusqueda.textContent = "";

        botonesFiltro.forEach((btn) => btn.classList.remove("activo"));

        if (botonesFiltro.length > 0) {
            botonesFiltro[0].classList.add("activo");
        }

        productos.forEach((producto) => {
            producto.style.display = "block";
        });

        return;
    }

    resultadoBusqueda.textContent =
        encontrados === 1
            ? "1 producto encontrado"
            : `${encontrados} productos encontrados`;

    if (encontrados > 0) {
        document.getElementById("productos").scrollIntoView({
            behavior: "smooth"
        });
    }
});

document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
        buscadorPanel.classList.remove("abierto");
    }
});

const btnAbrirCarrito = document.getElementById("btn-abrir-carrito");
const carritoPanel = document.getElementById("carrito-panel");
const carritoOverlay = document.getElementById("carrito-overlay");
const cerrarCarritoBtn = document.getElementById("cerrar-carrito");
const seguirComprando = document.getElementById("seguir-comprando");
const carritoProductos = document.getElementById("carrito-productos");
const contadorCarrito = document.getElementById("contador-carrito");
const carritoSubtotal = document.getElementById("carrito-subtotal");
const botonesCarrito = document.querySelectorAll(".btn-carrito");

let carrito = JSON.parse(localStorage.getItem("nexusCarrito")) || [];

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

btnAbrirCarrito.addEventListener("click", abrirCarrito);
cerrarCarritoBtn.addEventListener("click", cerrarCarrito);
carritoOverlay.addEventListener("click", cerrarCarrito);
seguirComprando.addEventListener("click", cerrarCarrito);

document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") cerrarCarrito();
});

botonesCarrito.forEach((boton) => {
    boton.addEventListener("click", () => {
        if (boton.disabled) return;

        const tarjeta = boton.closest(
            ".producto-card, .oferta-card, .novedad-card"
        );

        const imagen = tarjeta
            ? tarjeta.querySelector(
                  ".producto-foto img, .oferta-imagen img, .novedad-imagen img"
              )
            : null;

        const producto = {
            id: boton.dataset.id,
            nombre: boton.dataset.nombre,
            precio: Number(boton.dataset.precio),
            stock: Number(boton.dataset.stock),
            imagen: imagen ? imagen.src : ""
        };

        const existente = carrito.find(
            (item) => item.id === producto.id
        );

        if (existente) {
            if (existente.cantidad < producto.stock) {
                existente.cantidad++;
            }
        } else if (producto.stock > 0) {
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

function guardarCarrito() {
    localStorage.setItem("nexusCarrito", JSON.stringify(carrito));
}

function renderizarCarrito() {
    carritoProductos.innerHTML = "";

    if (carrito.length === 0) {
        carritoProductos.innerHTML = `
            <div class="carrito-vacio">
                <div class="carrito-vacio-icono">🛒</div>
                <h3>Tu carrito está vacío</h3>
                <p>Agrega productos gamer y arma tu próximo setup.</p>
            </div>
        `;

        actualizarResumen();
        return;
    }

    carrito.forEach((producto) => {
        const item = document.createElement("div");
        item.classList.add("carrito-item");

        item.innerHTML = `
            <div class="carrito-item-imagen">
                ${
                    producto.imagen
                        ? `<img src="${producto.imagen}" alt="${producto.nombre}">`
                        : "🎮"
                }
            </div>

            <div class="carrito-item-info">
                <h4>${producto.nombre}</h4>
                <span class="carrito-item-precio">
                    S/ ${producto.precio.toFixed(2)}
                </span>

                <div class="carrito-cantidad">
                    <button type="button"
                        onclick="cambiarCantidad('${producto.id}', -1)">−</button>

                    <span>${producto.cantidad}</span>

                    <button type="button"
                        onclick="cambiarCantidad('${producto.id}', 1)">+</button>
                </div>
            </div>

            <button type="button"
                class="eliminar-carrito"
                onclick="eliminarProducto('${producto.id}')"
                aria-label="Eliminar producto">✕</button>
        `;

        carritoProductos.appendChild(item);
    });

    actualizarResumen();
}

function cambiarCantidad(id, cambio) {
    const producto = carrito.find((item) => item.id === id);

    if (!producto) return;

    producto.cantidad += cambio;

    if (producto.cantidad <= 0) {
        carrito = carrito.filter((item) => item.id !== id);
    } else if (producto.cantidad > producto.stock) {
        producto.cantidad = producto.stock;
    }

    guardarCarrito();
    renderizarCarrito();
}

function eliminarProducto(id) {
    carrito = carrito.filter((producto) => producto.id !== id);

    guardarCarrito();
    renderizarCarrito();
}

function actualizarResumen() {
    const cantidadTotal = carrito.reduce(
        (total, producto) => total + producto.cantidad,
        0
    );

    const subtotal = carrito.reduce(
        (total, producto) =>
            total + producto.precio * producto.cantidad,
        0
    );

    contadorCarrito.textContent = cantidadTotal;
    carritoSubtotal.textContent = `S/ ${subtotal.toFixed(2)}`;
}

renderizarCarrito();

const botonesFavoritos = document.querySelectorAll(".favorito");

let favoritos =
    JSON.parse(localStorage.getItem("nexusFavoritos")) || [];

function guardarFavoritos() {
    localStorage.setItem("nexusFavoritos", JSON.stringify(favoritos));
}

function actualizarFavoritos() {
    botonesFavoritos.forEach((boton) => {
        const id = boton.dataset.id;

        const esFavorito = favoritos.some(
            (producto) => producto.id === id
        );

        boton.classList.toggle("activo", esFavorito);
        boton.textContent = esFavorito ? "♥" : "♡";

        boton.setAttribute(
            "aria-label",
            esFavorito
                ? "Eliminar de favoritos"
                : "Agregar a favoritos"
        );
    });
}

botonesFavoritos.forEach((boton) => {
    boton.addEventListener("click", () => {
        const tarjeta = boton.closest(
            ".producto-card, .novedad-card"
        );

        const id = boton.dataset.id;
        const existente = favoritos.find(
            (producto) => producto.id === id
        );

        if (existente) {
            favoritos = favoritos.filter(
                (producto) => producto.id !== id
            );
        } else {
            const imagen = tarjeta
                ? tarjeta.querySelector(
                      ".producto-foto img, .novedad-imagen img"
                  )
                : null;

            const precioElemento = tarjeta
                ? tarjeta.querySelector(".btn-carrito")
                : null;

            favoritos.push({
                id,
                nombre: boton.dataset.nombre,
                precio: precioElemento
                    ? Number(precioElemento.dataset.precio)
                    : 0,
                imagen: imagen ? imagen.src : ""
            });
        }

        guardarFavoritos();
        actualizarFavoritos();
    });
});

actualizarFavoritos();

const btnUsuario = document.getElementById("btn-usuario");
const usuarioPanel = document.getElementById("usuario-panel");
const usuarioOverlay = document.getElementById("usuario-overlay");
const cerrarUsuarioBtn = document.getElementById("cerrar-usuario");
const listaFavoritos = document.getElementById("lista-favoritos");
const contadorFavoritos = document.getElementById("contador-favoritos");
const cantidadFavoritosTexto = document.getElementById("cantidad-favoritos-texto");
const usuarioCarrito = document.getElementById("usuario-carrito");
const contadorCarritoUsuario = document.getElementById("contador-carrito-usuario");

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

btnUsuario.addEventListener("click", abrirUsuario);
cerrarUsuarioBtn.addEventListener("click", cerrarUsuario);
usuarioOverlay.addEventListener("click", cerrarUsuario);

function renderizarFavoritosUsuario() {
    listaFavoritos.innerHTML = "";

    if (favoritos.length === 0) {
        listaFavoritos.innerHTML = `
            <div class="sin-favoritos">
                <span>♡</span>
                <h4>Aún no tienes favoritos</h4>
                <p>Guarda productos usando el corazón.</p>
            </div>
        `;
        return;
    }

    favoritos.forEach((producto) => {
        const elemento = document.createElement("div");
        elemento.classList.add("favorito-item");

        elemento.innerHTML = `
            <div class="favorito-item-imagen">
                ${
                    producto.imagen
                        ? `<img src="${producto.imagen}" alt="${producto.nombre}">`
                        : "🎮"
                }
            </div>

            <div class="favorito-item-info">
                <h4>${producto.nombre}</h4>
                <strong>S/ ${producto.precio.toFixed(2)}</strong>
            </div>

            <button type="button"
                class="eliminar-favorito"
                onclick="eliminarFavoritoUsuario('${producto.id}')"
                aria-label="Eliminar favorito">♥</button>
        `;

        listaFavoritos.appendChild(elemento);
    });
}

function eliminarFavoritoUsuario(id) {
    favoritos = favoritos.filter(
        (producto) => producto.id !== id
    );

    guardarFavoritos();
    actualizarFavoritos();
    renderizarFavoritosUsuario();
    actualizarContadoresUsuario();
}

function actualizarContadoresUsuario() {
    const cantidadFavoritos = favoritos.length;

    contadorFavoritos.textContent = cantidadFavoritos;

    cantidadFavoritosTexto.textContent =
        cantidadFavoritos === 1
            ? "1 producto"
            : `${cantidadFavoritos} productos`;

    const cantidadCarrito = carrito.reduce(
        (total, producto) => total + producto.cantidad,
        0
    );

    contadorCarritoUsuario.textContent = cantidadCarrito;
}

usuarioCarrito.addEventListener("click", () => {
    cerrarUsuario();
    abrirCarrito();
});

document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") cerrarUsuario();
});

const btnNexusAI = document.getElementById("btn-nexus-ai");
const nexusAIPanel = document.getElementById("nexus-ai-panel");
const cerrarNexusAI = document.getElementById("cerrar-nexus-ai");
const nexusAIForm = document.getElementById("nexus-ai-form");
const nexusAIInput = document.getElementById("nexus-ai-input");
const nexusAIMensajes = document.getElementById("nexus-ai-mensajes");
const nexusAIEnviar = document.getElementById("nexus-ai-enviar");
const sugerenciasNexusAI = document.querySelectorAll(
    ".nexus-ai-sugerencias button"
);

function abrirNexusAI() {
    nexusAIPanel.classList.add("abierto");
    btnNexusAI.classList.add("chat-abierto");

    setTimeout(() => nexusAIInput.focus(), 250);
}

function cerrarPanelNexusAI() {
    nexusAIPanel.classList.remove("abierto");
    btnNexusAI.classList.remove("chat-abierto");
}

btnNexusAI.addEventListener("click", abrirNexusAI);
cerrarNexusAI.addEventListener("click", cerrarPanelNexusAI);

document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") cerrarPanelNexusAI();
});

function mostrarMensajeUsuario(mensaje) {
    const elemento = document.createElement("div");
    elemento.classList.add("mensaje-usuario");

    const parrafo = document.createElement("p");
    parrafo.textContent = mensaje;

    elemento.appendChild(parrafo);
    nexusAIMensajes.appendChild(elemento);

    bajarChat();
}

function mostrarMensajeAI(mensaje) {
    const elemento = document.createElement("div");
    elemento.classList.add("mensaje-ai");

    const avatar = document.createElement("div");
    avatar.classList.add("mensaje-avatar");
    avatar.textContent = "🤖";

    const contenido = document.createElement("div");
    contenido.classList.add("mensaje-contenido");

    const nombre = document.createElement("span");
    nombre.textContent = "NEXUS AI";

    const parrafo = document.createElement("p");
    parrafo.textContent = mensaje;

    contenido.appendChild(nombre);
    contenido.appendChild(parrafo);

    elemento.appendChild(avatar);
    elemento.appendChild(contenido);

    nexusAIMensajes.appendChild(elemento);

    bajarChat();
}

function mostrarEscribiendo() {
    eliminarEscribiendo();

    const escribiendo = document.createElement("div");
    escribiendo.classList.add("nexus-ai-escribiendo");
    escribiendo.id = "nexus-ai-escribiendo";

    escribiendo.innerHTML = `
        <span></span>
        <span></span>
        <span></span>
    `;

    nexusAIMensajes.appendChild(escribiendo);
    bajarChat();
}

function eliminarEscribiendo() {
    const escribiendo = document.getElementById(
        "nexus-ai-escribiendo"
    );

    if (escribiendo) escribiendo.remove();
}

function bajarChat() {
    nexusAIMensajes.scrollTop = nexusAIMensajes.scrollHeight;
}

async function enviarMensajeNexusAI(mensaje) {
    const texto = mensaje.trim();

    if (!texto) return;

    mostrarMensajeUsuario(texto);
    nexusAIInput.value = "";

    nexusAIInput.disabled = true;
    nexusAIEnviar.disabled = true;

    mostrarEscribiendo();

    try {
        const respuesta = await fetch("/api/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                mensaje: texto
            })
        });

        const datos = await respuesta.json();

        eliminarEscribiendo();

        if (!respuesta.ok) {
            mostrarMensajeAI(
                datos.respuesta ||
                "No pude procesar tu consulta."
            );
            return;
        }

        mostrarMensajeAI(datos.respuesta);

    } catch (error) {
        console.error("Error NEXUS AI:", error);

        eliminarEscribiendo();

        mostrarMensajeAI(
            "No pude conectarme con el servidor. Inténtalo nuevamente."
        );

    } finally {
        nexusAIInput.disabled = false;
        nexusAIEnviar.disabled = false;
        nexusAIInput.focus();
    }
}

nexusAIForm.addEventListener("submit", (event) => {
    event.preventDefault();

    const mensaje = nexusAIInput.value;
    enviarMensajeNexusAI(mensaje);
});

sugerenciasNexusAI.forEach((boton) => {
    boton.addEventListener("click", () => {
        const pregunta = boton.textContent.trim();
        enviarMensajeNexusAI(pregunta);
    });
});

const btnFinalizar = document.getElementById("btn-finalizar");
const checkoutModal = document.getElementById("checkout-modal");
const checkoutOverlay = document.getElementById("checkout-overlay");
const cerrarCheckout = document.getElementById("cerrar-checkout");
const checkoutForm = document.getElementById("checkout-form");

function abrirCheckout() {
    if (carrito.length === 0) {
        alert("Tu carrito está vacío.");
        return;
    }

    checkoutModal.classList.add("activo");
    checkoutOverlay.classList.add("activo");
    document.body.style.overflow = "hidden";
}

function cerrarFormularioCheckout() {
    checkoutModal.classList.remove("activo");
    checkoutOverlay.classList.remove("activo");
    document.body.style.overflow = "";
}

if (btnFinalizar) {
    btnFinalizar.addEventListener("click", abrirCheckout);
}

if (cerrarCheckout) {
    cerrarCheckout.addEventListener(
        "click",
        cerrarFormularioCheckout
    );
}

if (checkoutOverlay) {
    checkoutOverlay.addEventListener(
        "click",
        cerrarFormularioCheckout
    );
}

if (checkoutForm) {
    checkoutForm.addEventListener("submit", async function (e) {
        e.preventDefault();

        if (carrito.length === 0) {
            alert("Tu carrito está vacío.");
            return;
        }

        const nombre = document
            .getElementById("checkout-nombre")
            .value.trim();

        const telefono = document
            .getElementById("checkout-telefono")
            .value.trim();

        const correo = document
            .getElementById("checkout-correo")
            .value.trim();

        const ciudad = document
            .getElementById("checkout-ciudad")
            .value.trim();

        const direccion = document
            .getElementById("checkout-direccion")
            .value.trim();

        const botonEnviar = checkoutForm.querySelector(
            'button[type="submit"]'
        );

        if (botonEnviar.disabled) return;

        botonEnviar.disabled = true;
        botonEnviar.textContent = "REGISTRANDO PEDIDO...";

        try {
            const respuesta = await fetch("/api/pedido", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    nombre,
                    telefono,
                    correo,
                    ciudad,
                    direccion,
                    productos: carrito.map((producto) => ({
                        id: producto.id,
                        cantidad: producto.cantidad
                    }))
                })
            });

            const datos = await respuesta.json();

            if (!respuesta.ok || !datos.ok) {
                throw new Error(
                    datos.mensaje ||
                    "No se pudo registrar el pedido."
                );
            }

            alert(
                "¡Pedido registrado correctamente!\n" +
                "Número de pedido: " + datos.id_venta + "\n" +
                "Total: S/ " + Number(datos.total).toFixed(2) +
                "\n\nNos comunicaremos contigo para coordinar tu compra."
            );

            carrito = [];
            guardarCarrito();
            renderizarCarrito();

            checkoutForm.reset();
            cerrarFormularioCheckout();
            cerrarCarrito();

            actualizarContadoresUsuario();

        } catch (error) {
            console.error("Error al registrar pedido:", error);

            alert(
                error.message ||
                "Ocurrió un error al enviar el pedido."
            );

        } finally {
            botonEnviar.disabled = false;
            botonEnviar.textContent = "CONFIRMAR Y ENVIAR PEDIDO";
        }
    });
}

const btnLoginAdmin = document.getElementById("btn-login-admin");
const loginAdminPanel = document.getElementById("login-admin-panel");
const btnVolverCuenta = document.getElementById("btn-volver-cuenta");

if (btnLoginAdmin && loginAdminPanel) {
    btnLoginAdmin.addEventListener("click", () => {
        loginAdminPanel.hidden = false;
        btnLoginAdmin.hidden = true;
    });
}

if (btnVolverCuenta && loginAdminPanel && btnLoginAdmin) {
    btnVolverCuenta.addEventListener("click", () => {
        loginAdminPanel.hidden = true;
        btnLoginAdmin.hidden = false;
    });
}