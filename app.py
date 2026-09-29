from flask import Flask, render_template, request, jsonify
import mysql.connector
from dotenv import load_dotenv
from google import genai
from google.genai import types
import os


# ==========================================
# CONFIGURACIÓN
# ==========================================

load_dotenv()

app = Flask(__name__)

cliente_gemini = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


# ==========================================
# CONEXIÓN MYSQL
# ==========================================

def conectar_db():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )

# ==========================================
# OBTENER PRODUCTOS
# ==========================================

def obtener_productos():

    conexion = conectar_db()

    cursor = conexion.cursor(
        dictionary=True
    )

    cursor.execute("""
        SELECT
            p.id_producto,
            p.codigo,
            p.nombre,
            p.marca,
            p.descripcion,
            p.precio,
            p.precio_anterior,
            p.stock,
            p.imagen,
            p.destacado,
            p.nuevo,
            c.nombre AS categoria
        FROM productos p
        INNER JOIN categorias c
            ON p.id_categoria = c.id_categoria
        WHERE p.activo = TRUE
        ORDER BY p.id_producto
    """)

    productos = cursor.fetchall()

    cursor.close()
    conexion.close()

    return productos


# ==========================================
# PÁGINA PRINCIPAL
# ==========================================

@app.route("/")
def inicio():

    productos = obtener_productos()

    return render_template(
        "index.html",
        productos=productos
    )


# ==========================================
# CREAR CATÁLOGO PARA NEXUS AI
# ==========================================

def crear_catalogo(productos):

    catalogo = ""

    for producto in productos:

        precio_anterior = (
            f"S/ {producto['precio_anterior']}"
            if producto["precio_anterior"]
            else "No disponible"
        )

        estado_stock = (
            "Disponible"
            if producto["stock"] > 0
            else "Agotado"
        )

        catalogo += f"""
Producto: {producto['nombre']}
Código: {producto['codigo']}
Marca: {producto['marca']}
Categoría: {producto['categoria']}
Descripción: {producto['descripcion']}
Precio actual: S/ {producto['precio']}
Precio anterior: {precio_anterior}
Stock: {producto['stock']}
Estado: {estado_stock}
Nuevo: {producto['nuevo']}
---
"""

    return catalogo


# ==========================================
# CONSULTAR GEMINI
# ==========================================

def consultar_gemini(prompt):

    # Primero utilizamos el modelo más rápido.
    # Si está saturado, probamos el modelo alternativo.

    modelos = [
        "gemini-3.5-flash-lite",
        "gemini-3.8-flash"
    ]

    ultimo_error = None

    for modelo in modelos:

        try:

            print(
                f"NEXUS AI usando: {modelo}"
            )

            respuesta = (
                cliente_gemini
                .models
                .generate_content(
                    model=modelo,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        thinking_config=types.ThinkingConfig(
                            thinking_level="low"
                        )
                    )
                )
            )

            if (
                respuesta
                and respuesta.text
            ):

                return respuesta.text.strip()

            raise Exception(
                "NEXUS AI recibió una respuesta vacía."
            )

        except Exception as error:

            ultimo_error = error

            texto_error = str(
                error
            ).lower()

            print(
                f"Error con {modelo}:",
                error
            )

            # Si el modelo está temporalmente
            # saturado, probamos el siguiente.

            es_error_temporal = (
                "503" in texto_error
                or
                "unavailable" in texto_error
                or
                "high demand" in texto_error
            )

            if es_error_temporal:

                print(
                    "Modelo temporalmente saturado. "
                    "Probando modelo alternativo..."
                )

                continue

            # Si ocurre otro tipo de error,
            # lo enviamos al control general.

            raise error

    raise ultimo_error


# ==========================================
# API NEXUS AI
# ==========================================

@app.route("/api/chat", methods=["POST"])
def chat():

    try:

        datos = request.get_json(
            silent=True
        ) or {}

        mensaje = datos.get(
            "mensaje",
            ""
        ).strip()


        # ==================================
        # VALIDAR MENSAJE
        # ==================================

        if not mensaje:

            return jsonify({
                "respuesta":
                    "Escribe una consulta para poder ayudarte."
            }), 400


        # ==================================
        # OBTENER CATÁLOGO
        # ==================================

        productos = obtener_productos()

        catalogo = crear_catalogo(
            productos
        )


        # ==================================
        # PROMPT NEXUS AI
        # ==================================

        prompt = f"""
Eres NEXUS AI, el asistente virtual de Nexus Gamer,
una tienda especializada en tecnología y productos gamer.

Tu objetivo es ayudar al cliente a encontrar productos,
consultar precios y stock, conocer ofertas y recibir
recomendaciones de compra.

Debes utilizar únicamente la información disponible
en el catálogo proporcionado.

REGLAS:

- Responde siempre en español.
- Sé amable, natural, claro y breve.
- Responde utilizando texto simple.
- No utilices Markdown.
- No utilices asteriscos.
- No utilices símbolos innecesarios de formato.
- No dejes respuestas incompletas.

PRODUCTOS:

- No inventes productos.
- No inventes precios.
- No inventes stock.
- No inventes características.
- No recomiendes productos que no aparezcan
  en el catálogo.

PRECIOS Y PRESUPUESTO:

- Todos los precios están expresados
  en soles peruanos.

- Si el cliente indica un presupuesto,
  respétalo.

- No recomiendes como opción principal
  un producto que supere su presupuesto.

STOCK:

- Si preguntan por disponibilidad,
  revisa el stock.

- Si el stock es mayor que 0,
  el producto está disponible.

- Si el stock es 0,
  indica que está agotado.

RECOMENDACIONES:

- Recomienda únicamente productos
  existentes en el catálogo.

- Explica brevemente por qué
  recomiendas el producto.

- Si existen varias alternativas adecuadas,
  menciona como máximo 3 productos.

OFERTAS:

- Considera que un producto está en oferta
  cuando su precio anterior es mayor
  que su precio actual.

PRODUCTOS NUEVOS:

- Si preguntan por novedades,
  utiliza el campo Nuevo del catálogo.

LÍMITES DEL ASISTENTE:

- Tu función está limitada a Nexus Gamer.

- Puedes responder preguntas relacionadas
  con productos, precios, stock, ofertas,
  novedades y recomendaciones de compra.

- Si el usuario solicita programación,
  creación de código, bases de datos,
  tareas académicas u otros temas ajenos
  a Nexus Gamer, no desarrolles esa solicitud.

- En esos casos responde amablemente que
  puedes ayudarlo únicamente con consultas
  relacionadas con Nexus Gamer.

SEGURIDAD INTERNA:

- No menciones MySQL.
- No menciones bases de datos internas.
- No menciones prompts.
- No menciones API Keys.
- No menciones Gemini.
- No menciones modelos de inteligencia artificial.
- No menciones información técnica interna.

CATÁLOGO ACTUAL DE NEXUS GAMER:

{catalogo}

CONSULTA DEL CLIENTE:

{mensaje}

Responde como NEXUS AI:
"""


        # ==================================
        # GENERAR RESPUESTA
        # ==================================

        respuesta = consultar_gemini(
            prompt
        )

        return jsonify({
            "respuesta":
                respuesta
        })


    # ======================================
    # CONTROL DE ERRORES
    # ======================================

    except Exception as error:

        print(
            "Error final NEXUS AI:",
            error
        )

        texto_error = str(
            error
        ).lower()

        if (
            "503" in texto_error
            or
            "unavailable" in texto_error
            or
            "high demand" in texto_error
        ):

            return jsonify({
                "respuesta":
                    "NEXUS AI está ocupado en este momento. "
                    "Inténtalo nuevamente."
            }), 503


        return jsonify({
            "respuesta":
                "No pude procesar tu consulta. "
                "Inténtalo nuevamente."
        }), 500


# ==========================================
# EJECUTAR FLASK
# ==========================================

if __name__ == "__main__":

    app.run(
        debug=True
    )