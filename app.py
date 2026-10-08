from flask import (
    Flask, render_template, request, jsonify,
    session, redirect, url_for
)
import mysql.connector
from mysql.connector import IntegrityError
from dotenv import load_dotenv
from google import genai
from google.genai import types
from decimal import Decimal, InvalidOperation
from functools import wraps
from werkzeug.security import check_password_hash
from datetime import date, datetime
import os
import re
import secrets
import hmac
import uuid
from pathlib import Path
from PIL import Image, UnidentifiedImageError
import cloudinary
import cloudinary.uploader
from cloudinary.exceptions import Error as CloudinaryError
from io import BytesIO
from flask import send_file
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
)
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.units import cm
from xml.sax.saxutils import escape

load_dotenv()

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True
)

app = Flask(__name__)

app.secret_key = os.getenv("SECRET_KEY")

if not app.secret_key:
    raise RuntimeError(
        "Falta configurar SECRET_KEY en el archivo .env"
    )

app.config["MAX_CONTENT_LENGTH"] = 6 * 1024 * 1024
app.config["UPLOAD_FOLDER"] = str(Path(app.static_folder) / "img" / "productos")

Path(app.config["UPLOAD_FOLDER"]).mkdir(parents=True, exist_ok=True)

app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = (
    os.getenv("FLASK_ENV") == "production"
)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

cliente_gemini = (
    genai.Client(api_key=GEMINI_API_KEY)
    if GEMINI_API_KEY else None
)


def conectar_db():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )


def cerrar_db(conexion=None, cursor=None):
    if cursor:
        cursor.close()

    if conexion:
        conexion.close()


def obtener_filas(consulta, parametros=()):
    conexion = None
    cursor = None

    try:
        conexion = conectar_db()
        cursor = conexion.cursor(dictionary=True)
        cursor.execute(consulta, parametros)

        return cursor.fetchall()

    finally:
        cerrar_db(conexion, cursor)


def obtener_valor(consulta, parametros=()):
    conexion = None
    cursor = None

    try:
        conexion = conectar_db()
        cursor = conexion.cursor()
        cursor.execute(consulta, parametros)

        fila = cursor.fetchone()

        return fila[0] if fila else 0

    finally:
        cerrar_db(conexion, cursor)


def obtener_productos():
    return obtener_filas("""
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


@app.route("/")
def inicio():
    productos = obtener_productos()

    return render_template(
        "index.html",
        productos=productos
    )


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


def consultar_gemini(prompt):
    if cliente_gemini is None:
        raise RuntimeError("GEMINI_API_KEY no configurada.")

    modelos = [
        "gemini-3.5-flash-lite",
        "gemini-3.8-flash"
    ]

    ultimo_error = None

    for modelo in modelos:
        try:
            print(f"NEXUS AI usando: {modelo}")

            respuesta = cliente_gemini.models.generate_content(
                model=modelo,
                contents=prompt,
                config=types.GenerateContentConfig(
                    thinking_config=types.ThinkingConfig(
                        thinking_level="low"
                    )
                )
            )

            if respuesta and respuesta.text:
                return respuesta.text.strip()

            raise RuntimeError(
                "NEXUS AI recibió una respuesta vacía."
            )

        except Exception as error:
            ultimo_error = error
            texto_error = str(error).lower()

            print(f"Error con {modelo}:", error)

            es_error_temporal = (
                "503" in texto_error
                or "unavailable" in texto_error
                or "high demand" in texto_error
            )

            if es_error_temporal:
                continue

            raise

    raise ultimo_error


@app.route("/api/chat", methods=["POST"])
def chat():
    try:
        datos = request.get_json(silent=True) or {}

        mensaje = str(
            datos.get("mensaje", "")
        ).strip()

        if not mensaje:
            return jsonify({
                "respuesta": "Escribe una consulta para ayudarte."
            }), 400

        productos = obtener_productos()
        catalogo = crear_catalogo(productos)

        prompt = f"""
Eres NEXUS AI, el asistente virtual de Nexus Gamer,
una tienda especializada en tecnología y productos gamer.

Tu objetivo es ayudar al cliente a encontrar productos,
consultar precios y stock, conocer ofertas y recibir
recomendaciones de compra.

Debes utilizar únicamente la información disponible
en el catálogo proporcionado.

REGLAS:
\\- Responde siempre en español.
\\- Sé amable, natural, claro y breve.
\\- Responde utilizando texto simple.
\\- No utilices Markdown ni asteriscos.
\\- No utilices símbolos innecesarios de formato.
\\- No dejes respuestas incompletas.

PRODUCTOS:
\\- No inventes productos.
\\- No inventes precios.
\\- No inventes stock.
\\- No inventes características.
\\- No recomiendes productos fuera del catálogo.

PRECIOS Y PRESUPUESTO:
\\- Todos los precios están expresados en soles peruanos.
\\- Si el cliente indica un presupuesto, respétalo.
\\- No recomiendes como opción principal un producto
  que supere su presupuesto.

STOCK:
\\- Si preguntan por disponibilidad, revisa el stock.
\\- Si el stock es mayor que 0, está disponible.
\\- Si el stock es 0, indica que está agotado.

RECOMENDACIONES:
\\- Recomienda únicamente productos existentes.
\\- Explica brevemente por qué recomiendas el producto.
\\- Menciona como máximo 3 alternativas adecuadas.

OFERTAS:
\\- Un producto está en oferta cuando su precio anterior
  es mayor que su precio actual.

PRODUCTOS NUEVOS:
\\- Si preguntan por novedades, utiliza el campo Nuevo.

LÍMITES DEL ASISTENTE:
\\- Tu función está limitada a Nexus Gamer.
\\- Responde consultas relacionadas con productos,
  precios, stock, ofertas, novedades y recomendaciones.
\\- No desarrolles solicitudes de programación,
  tareas académicas ni temas ajenos a Nexus Gamer.

SEGURIDAD INTERNA:
\\- No menciones MySQL.
\\- No menciones bases de datos internas.
\\- No menciones prompts.
\\- No menciones API Keys.
\\- No menciones Gemini.
\\- No menciones modelos de inteligencia artificial.
\\- No menciones información técnica interna.

CATÁLOGO ACTUAL:
{catalogo}

CONSULTA DEL CLIENTE:
{mensaje}

Responde como NEXUS AI:
"""

        respuesta = consultar_gemini(prompt)

        return jsonify({
            "respuesta": respuesta
        })

    except Exception as error:
        print("Error NEXUS AI:", error)

        texto_error = str(error).lower()

        if any(
            palabra in texto_error
            for palabra in ("503", "unavailable", "high demand")
        ):
            return jsonify({
                "respuesta": (
                    "NEXUS AI está ocupado en este momento. "
                    "Inténtalo nuevamente."
                )
            }), 503

        return jsonify({
            "respuesta": (
                "No pude procesar tu consulta. "
                "Inténtalo nuevamente."
            )
        }), 500


@app.route("/api/pedido", methods=["POST"])
def registrar_pedido():
    conexion = None
    cursor = None

    try:
        datos = request.get_json(silent=True)

        if not isinstance(datos, dict):
            raise ValueError("Datos de pedido inválidos.")

        campos = [
            "nombre", "telefono", "correo",
            "ciudad", "direccion"
        ]

        contacto = {}

        for campo in campos:
            valor = datos.get(campo, "")

            if not isinstance(valor, str):
                raise ValueError(
                    "Los datos de contacto no son válidos."
                )

            contacto[campo] = valor.strip()

        if not all(contacto.values()):
            raise ValueError(
                "Completa todos los datos de contacto."
            )

        nombre = contacto["nombre"]
        telefono = contacto["telefono"]
        correo = contacto["correo"].lower()
        ciudad = contacto["ciudad"]
        direccion = contacto["direccion"]

        if (
            len(nombre) > 120
            or len(telefono) > 20
            or len(correo) > 150
            or len(ciudad) > 100
            or len(direccion) > 255
        ):
            raise ValueError(
                "Uno de los datos de contacto es demasiado largo."
            )

        if not re.fullmatch(
            r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$",
            correo
        ):
            raise ValueError(
                "Ingresa un correo electrónico válido."
            )

        productos = datos.get("productos", [])

        if not isinstance(productos, list) or not productos:
            raise ValueError("El carrito está vacío.")

        if len(productos) > 100:
            raise ValueError(
                "El pedido contiene demasiados productos."
            )

        cantidades = {}

        for item in productos:
            if not isinstance(item, dict):
                raise ValueError("Producto inválido.")

            id_original = item.get("id")
            cantidad_original = item.get("cantidad")

            if (
                isinstance(id_original, bool)
                or isinstance(cantidad_original, bool)
            ):
                raise ValueError("Producto inválido.")

            id_producto = int(id_original)
            cantidad = int(cantidad_original)

            if (
                str(id_original) != str(id_producto)
                or str(cantidad_original) != str(cantidad)
            ):
                raise ValueError("Producto inválido.")

            if id_producto <= 0 or cantidad <= 0:
                raise ValueError("Cantidad inválida.")

            cantidades[id_producto] = (
                cantidades.get(id_producto, 0) + cantidad
            )

            if cantidades[id_producto] > 1000:
                raise ValueError(
                    "La cantidad solicitada es demasiado alta."
                )

        conexion = conectar_db()
        conexion.start_transaction()

        cursor = conexion.cursor(dictionary=True)

        detalles = []
        total = Decimal("0.00")

        for id_producto in sorted(cantidades):
            cantidad = cantidades[id_producto]

            cursor.execute("""
                SELECT
                    id_producto,
                    nombre,
                    precio,
                    stock
                FROM productos
                WHERE id_producto = %s
                  AND activo = TRUE
                FOR UPDATE
            """, (id_producto,))

            producto = cursor.fetchone()

            if not producto:
                raise ValueError(
                    "Uno de los productos ya no está disponible."
                )

            if producto["stock"] < cantidad:
                raise ValueError(
                    f"Stock insuficiente para {producto['nombre']}."
                )

            precio = Decimal(str(producto["precio"]))
            subtotal = precio * cantidad
            total += subtotal

            detalles.append({
                "id_producto": id_producto,
                "cantidad": cantidad,
                "precio": precio,
                "subtotal": subtotal
            })

        cursor.execute("""
            SELECT id_cliente
            FROM clientes
            WHERE correo = %s
            FOR UPDATE
        """, (correo,))

        cliente = cursor.fetchone()

        if cliente:
            id_cliente = cliente["id_cliente"]

            cursor.execute("""
                UPDATE clientes
                SET nombre = %s,
                    telefono = %s,
                    ciudad = %s,
                    direccion = %s
                WHERE id_cliente = %s
            """, (
                nombre,
                telefono,
                ciudad,
                direccion,
                id_cliente
            ))

        else:
            cursor.execute("""
                INSERT INTO clientes (
                    nombre,
                    correo,
                    telefono,
                    ciudad,
                    direccion
                )
                VALUES (%s, %s, %s, %s, %s)
            """, (
                nombre,
                correo,
                telefono,
                ciudad,
                direccion
            ))

            id_cliente = cursor.lastrowid

        cursor.execute("""
            INSERT INTO ventas (
                id_cliente,
                total,
                estado
            )
            VALUES (%s, %s, %s)
        """, (
            id_cliente,
            total,
            "Pendiente"
        ))

        id_venta = cursor.lastrowid

        for detalle in detalles:
            cursor.execute("""
                INSERT INTO detalle_ventas (
                    id_venta,
                    id_producto,
                    cantidad,
                    precio_unitario,
                    subtotal
                )
                VALUES (%s, %s, %s, %s, %s)
            """, (
                id_venta,
                detalle["id_producto"],
                detalle["cantidad"],
                detalle["precio"],
                detalle["subtotal"]
            ))

            cursor.execute("""
                UPDATE productos
                SET stock = stock - %s
                WHERE id_producto = %s
                  AND stock >= %s
            """, (
                detalle["cantidad"],
                detalle["id_producto"],
                detalle["cantidad"]
            ))

            if cursor.rowcount != 1:
                raise ValueError(
                    "El stock cambió durante la compra."
                )

        conexion.commit()

        return jsonify({
            "ok": True,
            "mensaje": "Pedido registrado correctamente.",
            "id_venta": id_venta,
            "total": float(total)
        }), 201

    except (
        ValueError, TypeError, OverflowError
    ) as error:
        if conexion:
            conexion.rollback()

        return jsonify({
            "ok": False,
            "mensaje": str(error)
        }), 400

    except Exception as error:
        if conexion:
            conexion.rollback()

        app.logger.exception(
            "Error registrando pedido"
        )

        return jsonify({
            "ok": False,
            "mensaje": "No se pudo registrar el pedido."
        }), 500

    finally:
        cerrar_db(conexion, cursor)


def acceso_requerido(funcion):
    @wraps(funcion)
    def verificar(*args, **kwargs):
        if "usuario_id" not in session:
            return redirect(url_for("admin_login"))

        if session.get("usuario_rol") not in (
            "admin", "empleado"
        ):
            session.clear()
            return redirect(url_for("admin_login"))

        return funcion(*args, **kwargs)

    return verificar


def solo_admin(funcion):
    @wraps(funcion)
    def verificar(*args, **kwargs):
        if session.get("usuario_rol") != "admin":
            return jsonify({
                "ok": False,
                "mensaje": "Acceso exclusivo del administrador."
            }), 403

        return funcion(*args, **kwargs)

    return verificar


def proteger_admin(funcion):
    @wraps(funcion)
    def verificar(*args, **kwargs):
        if (
            "usuario_id" not in session
            or session.get("usuario_rol") not in (
                "admin", "empleado"
            )
        ):
            return jsonify({
                "ok": False,
                "mensaje": "Debes iniciar sesión."
            }), 401

        return funcion(*args, **kwargs)

    return verificar


def obtener_csrf():
    token = session.get("csrf_token")

    if not token:
        token = secrets.token_hex(32)
        session["csrf_token"] = token

    return token


@app.context_processor
def variables_seguridad():
    return {"csrf_token": obtener_csrf}


@app.route("/admin/csrf", methods=["GET"])
@proteger_admin
def admin_csrf():
    respuesta = jsonify({"ok": True, "csrf_token": obtener_csrf()})
    respuesta.headers["Cache-Control"] = "no-store"

    return respuesta


@app.before_request
def verificar_csrf_admin():
    if not (request.path.startswith("/admin/") and
            request.method in ("POST", "PUT", "PATCH", "DELETE")):
        return None

    recibido = (request.headers.get("X-CSRF-Token") or
                request.headers.get("X-CSRFToken") or
                request.form.get("csrf_token", ""))

    esperado = session.get("csrf_token")

    if not isinstance(recibido, str) or not isinstance(esperado, str) or not (
        recibido and esperado and hmac.compare_digest(recibido, esperado)
    ):
        app.logger.warning(
            "CSRF rechazado: ruta=%s token_recibido=%s token_sesion=%s usuario=%s",
            request.path, bool(recibido), bool(esperado), bool(session.get("usuario_id"))
        )

        if request.path == "/admin/login":
            return render_template("admin_login.html", error="La sesión expiró. Vuelve a intentarlo."), 403

        if request.path == "/admin/logout":
            return redirect(url_for("admin_dashboard"))

        return jsonify({
            "ok": False,
            "mensaje": "Sesión de seguridad inválida. Actualiza la página y vuelve a intentarlo."
        }), 403

    return None


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if session.get("usuario_id"):
        return redirect(url_for("admin_dashboard"))

    error = None

    if request.method == "POST":
        correo = request.form.get(
            "correo", ""
        ).strip().lower()

        password = request.form.get("password", "")

        conexion = None
        cursor = None

        try:
            conexion = conectar_db()
            cursor = conexion.cursor(dictionary=True)

            cursor.execute("""
                SELECT
                    id_usuario,
                    nombre,
                    correo,
                    password,
                    rol,
                    activo
                FROM usuarios
                WHERE correo = %s
                LIMIT 1
            """, (correo,))

            usuario = cursor.fetchone()

            if (
                usuario
                and usuario["activo"] == 1
                and usuario["rol"] in ("admin", "empleado")
                and check_password_hash(
                    usuario["password"],
                    password
                )
            ):
                token_login = session.get("csrf_token")

                session.clear()

                session["csrf_token"] = token_login or secrets.token_hex(32)
                session["usuario_id"] = usuario["id_usuario"]
                session["usuario_nombre"] = usuario["nombre"]
                session["usuario_rol"] = usuario["rol"]

                obtener_csrf()

                return redirect(url_for("admin_dashboard"))

            error = "Correo o contraseña incorrectos."

        except Exception:
            app.logger.exception("Error en login")
            error = "No se pudo iniciar sesión."

        finally:
            cerrar_db(conexion, cursor)

    return render_template(
        "admin_login.html",
        error=error
    )


def convertir_json(valor):
    if isinstance(valor, Decimal):
        return float(valor)

    if isinstance(valor, (datetime, date)):
        return valor.isoformat()

    if isinstance(valor, dict):
        return {
            clave: convertir_json(dato)
            for clave, dato in valor.items()
        }

    if isinstance(valor, list):
        return [convertir_json(dato) for dato in valor]

    return valor


def consultar_detalle_pedido(id_venta):
    conexion = None
    cursor = None

    try:
        conexion = conectar_db()
        cursor = conexion.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                v.id_venta,
                v.fecha,
                v.total,
                v.estado,
                c.nombre AS cliente,
                c.correo,
                c.telefono,
                c.ciudad,
                c.direccion
            FROM ventas v
            LEFT JOIN clientes c
                ON v.id_cliente = c.id_cliente
            WHERE v.id_venta = %s
            LIMIT 1
        """, (id_venta,))

        pedido = cursor.fetchone()

        if not pedido:
            return None

        cursor.execute("""
            SELECT
                d.id_producto,
                p.codigo,
                p.nombre,
                d.cantidad,
                d.precio_unitario,
                d.subtotal
            FROM detalle_ventas d
            LEFT JOIN productos p
                ON d.id_producto = p.id_producto
            WHERE d.id_venta = %s
            ORDER BY d.id_detalle
        """, (id_venta,))

        pedido["productos"] = cursor.fetchall()

        return pedido

    finally:
        cerrar_db(conexion, cursor)


@app.route("/admin/pedidos/<int:id_venta>/detalle")
@proteger_admin
def admin_detalle_pedido(id_venta):
    try:
        pedido = consultar_detalle_pedido(id_venta)

        if not pedido:
            return jsonify({
                "ok": False,
                "mensaje": "El pedido no existe."
            }), 404

        return jsonify({
            "ok": True,
            "pedido": convertir_json(pedido)
        })

    except Exception:
        app.logger.exception("Error consultando pedido")

        return jsonify({
            "ok": False,
            "mensaje": "No se pudo consultar el pedido."
        }), 500


@app.route("/admin/pedidos/<int:id_venta>/pdf")
@acceso_requerido
def admin_pdf_pedido(id_venta):
    try:
        pedido = consultar_detalle_pedido(id_venta)

        if not pedido:
            return "El pedido no existe.", 404

        buffer = BytesIO()

        documento = SimpleDocTemplate(
            buffer,
            pagesize=(21 * cm, 29.7 * cm),
            rightMargin=1.5 * cm,
            leftMargin=1.5 * cm,
            topMargin=1.5 * cm,
            bottomMargin=1.5 * cm
        )

        estilos = getSampleStyleSheet()
        estilos["Title"].alignment = TA_CENTER

        elementos = []

        elementos.append(
            Paragraph("NEXUS GAMER", estilos["Title"])
        )

        elementos.append(
            Paragraph(
                "Orden de pedido N.º {}".format(
                    pedido["id_venta"]
                ),
                estilos["Heading2"]
            )
        )

        elementos.append(Spacer(1, 0.5 * cm))

        fecha = (
            pedido["fecha"].strftime("%d/%m/%Y %H:%M")
            if pedido["fecha"] else "-"
        )

        def texto(valor):
            return escape(str(valor if valor is not None else "-"))

        datos_cliente = [
            ("Fecha", fecha),
            ("Cliente", pedido["cliente"]),
            ("Correo", pedido["correo"]),
            ("Teléfono", pedido["telefono"]),
            ("Ciudad", pedido["ciudad"]),
            ("Dirección", pedido["direccion"]),
            ("Estado", pedido["estado"])
        ]

        for etiqueta, valor in datos_cliente:
            elementos.append(
                Paragraph(
                    "<b>{}:</b> {}".format(
                        escape(etiqueta),
                        texto(valor)
                    ),
                    estilos["Normal"]
                )
            )

            elementos.append(Spacer(1, 0.15 * cm))

        elementos.append(Spacer(1, 0.6 * cm))

        elementos.append(
            Paragraph("Productos del pedido", estilos["Heading2"])
        )

        filas = [[
            "Producto", "Cant.", "P. unitario", "Subtotal"
        ]]

        for producto in pedido["productos"]:
            filas.append([
                Paragraph(
                    texto(producto["nombre"] or
                          producto["codigo"] or
                          "Producto"),
                    estilos["Normal"]
                ),
                str(producto["cantidad"]),
                "S/ {:.2f}".format(
                    producto["precio_unitario"]
                ),
                "S/ {:.2f}".format(
                    producto["subtotal"]
                )
            ])

        tabla = Table(
            filas,
            colWidths=[8.2 * cm, 2 * cm, 3.8 * cm, 4 * cm],
            repeatRows=1
        )

        tabla.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#22203D")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("GRID", (0, 0), (-1, -1), 0.4, colors.lightgrey),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
            ("TOPPADDING", (0, 0), (-1, -1), 9),
            ("ALIGN", (1, 1), (-1, -1), "RIGHT")
        ]))

        elementos.append(tabla)
        elementos.append(Spacer(1, 0.6 * cm))

        elementos.append(
            Paragraph(
                "<b>TOTAL: S/ {:.2f}</b>".format(
                    pedido["total"]
                ),
                estilos["Heading2"]
            )
        )

        elementos.append(Spacer(1, 1 * cm))

        elementos.append(
            Paragraph(
                "Documento generado por Nexus Gamer. "
                "Esta orden registra el pedido y no "
                "constituye un comprobante tributario "
                "ni acredita el pago.",
                estilos["Normal"]
            )
        )

        documento.build(elementos)

        buffer.seek(0)

        return send_file(
            buffer,
            mimetype="application/pdf",
            as_attachment=True,
            download_name="pedido_{}.pdf".format(id_venta)
        )

    except Exception:
        app.logger.exception("Error generando PDF")

        return "No se pudo generar el PDF.", 500


@app.route("/admin/dashboard")
@acceso_requerido
def admin_dashboard():
    conexion = None
    cursor = None

    try:
        conexion = conectar_db()
        cursor = conexion.cursor(dictionary=True)

        def consultar_uno(sql):
            cursor.execute(sql)
            return cursor.fetchone()

        def consultar_todos(sql):
            cursor.execute(sql)
            return cursor.fetchall()

        ingresos_mes = consultar_uno("""
            SELECT COALESCE(SUM(total), 0) AS total
            FROM ventas
            WHERE estado = 'Completada'
              AND fecha >= DATE_FORMAT(
                  CURDATE(), '%Y-%m-01'
              )
              AND fecha < DATE_FORMAT(
                  CURDATE() + INTERVAL 1 MONTH,
                  '%Y-%m-01'
              )
        """)["total"]

        pedidos_mes = consultar_uno("""
            SELECT COUNT(*) AS total
            FROM ventas
            WHERE fecha >= DATE_FORMAT(
                CURDATE(), '%Y-%m-01'
            )
              AND fecha < DATE_FORMAT(
                CURDATE() + INTERVAL 1 MONTH,
                '%Y-%m-01'
            )
        """)["total"]

        productos_disponibles = consultar_uno("""
            SELECT COUNT(*) AS total
            FROM productos
            WHERE activo = TRUE
              AND stock > 0
        """)["total"]

        clientes_registrados = consultar_uno("""
            SELECT COUNT(*) AS total
            FROM clientes
        """)["total"]

        pedidos = consultar_todos("""
            SELECT
                v.id_venta,
                v.fecha,
                v.total,
                v.estado,
                c.nombre AS cliente,
                c.telefono,
                c.correo,
                c.ciudad,
                c.direccion
            FROM ventas v
            LEFT JOIN clientes c
                ON v.id_cliente = c.id_cliente
            ORDER BY v.fecha DESC, v.id_venta DESC
            LIMIT 100
        """)

        productos_admin = consultar_todos("""
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
                p.id_categoria,
                p.destacado,
                p.nuevo,
                p.activo,
                c.nombre AS categoria
            FROM productos p
            LEFT JOIN categorias c
                ON p.id_categoria = c.id_categoria
            ORDER BY p.id_producto DESC
        """)

        categorias_admin = consultar_todos("""
            SELECT id_categoria, nombre
            FROM categorias
            ORDER BY nombre
        """)

        ventas_mensuales = consultar_todos("""
            SELECT DATE_FORMAT(fecha, '%Y-%m') AS mes,
                   COUNT(*) AS pedidos,
                   COALESCE(SUM(total), 0) AS ingresos
            FROM ventas
            WHERE estado = 'Completada'
              AND fecha >= DATE_FORMAT(CURDATE() - INTERVAL 11 MONTH, '%Y-%m-01')
              AND fecha < DATE_FORMAT(CURDATE() + INTERVAL 1 MONTH, '%Y-%m-01')
            GROUP BY DATE_FORMAT(fecha, '%Y-%m')
            ORDER BY mes
        """) if session.get("usuario_rol") == "admin" else []

        productos_mas_vendidos = consultar_todos("""
            SELECT COALESCE(p.nombre, CONCAT('Producto #', d.id_producto)) AS nombre,
                   DATE_FORMAT(v.fecha, '%Y-%m') AS mes,
                   SUM(d.cantidad) AS unidades,
                   COALESCE(SUM(d.subtotal), 0) AS ingresos
            FROM detalle_ventas d
            JOIN ventas v ON v.id_venta = d.id_venta
            LEFT JOIN productos p ON p.id_producto = d.id_producto
            WHERE v.estado = 'Completada'
              AND v.fecha >= DATE_FORMAT(CURDATE() - INTERVAL 11 MONTH, '%Y-%m-01')
              AND v.fecha < DATE_FORMAT(CURDATE() + INTERVAL 1 MONTH, '%Y-%m-01')
            GROUP BY d.id_producto, p.nombre, DATE_FORMAT(v.fecha, '%Y-%m')
            ORDER BY mes, unidades DESC
        """) if session.get("usuario_rol") == "admin" else []

        ventas_por_categoria = consultar_todos("""
            SELECT COALESCE(c.nombre, 'Sin categoría') AS categoria,
                   DATE_FORMAT(v.fecha, '%Y-%m') AS mes,
                   SUM(d.cantidad) AS unidades,
                   COALESCE(SUM(d.subtotal), 0) AS ingresos
            FROM detalle_ventas d
            JOIN ventas v ON v.id_venta = d.id_venta
            LEFT JOIN productos p ON p.id_producto = d.id_producto
            LEFT JOIN categorias c ON c.id_categoria = p.id_categoria
            WHERE v.estado = 'Completada'
              AND v.fecha >= DATE_FORMAT(CURDATE() - INTERVAL 11 MONTH, '%Y-%m-01')
              AND v.fecha < DATE_FORMAT(CURDATE() + INTERVAL 1 MONTH, '%Y-%m-01')
            GROUP BY c.id_categoria, c.nombre, DATE_FORMAT(v.fecha, '%Y-%m')
            ORDER BY mes, unidades DESC
        """) if session.get("usuario_rol") == "admin" else []

        clientes_admin = []

        if session.get("usuario_rol") == "admin":
            clientes_admin = consultar_todos("""
                SELECT
                    id_cliente,
                    nombre,
                    correo,
                    telefono,
                    ciudad,
                    direccion
                FROM clientes
                ORDER BY id_cliente DESC
                LIMIT 100
            """)

        return render_template(
            "admin_dashboard.html",
            nombre=session.get("usuario_nombre"),
            rol=session.get("usuario_rol"),
            ingresos_mes=ingresos_mes,
            pedidos_mes=pedidos_mes,
            productos_disponibles=productos_disponibles,
            clientes_registrados=clientes_registrados,
            pedidos=pedidos,
            productos_admin=convertir_json(
                productos_admin
            ),
            categorias_admin=categorias_admin,
            clientes_admin=clientes_admin,
            ventas_mensuales=convertir_json(ventas_mensuales),
            productos_mas_vendidos=convertir_json(productos_mas_vendidos),
            ventas_por_categoria=convertir_json(ventas_por_categoria)
        )

    except Exception:
        app.logger.exception(
            "Error cargando dashboard"
        )

        return (
            "No se pudieron cargar los datos del dashboard.",
            500
        )

    finally:
        cerrar_db(conexion, cursor)


def validar_producto(datos):
    if not isinstance(datos, dict):
        raise ValueError("Datos del producto inválidos.")

    codigo = str(datos.get("codigo") or "").strip()
    nombre = str(datos.get("nombre") or "").strip()
    marca = str(datos.get("marca") or "").strip()

    descripcion = str(
        datos.get("descripcion") or ""
    ).strip()

    imagen = str(datos.get("imagen") or "").strip()

    if not codigo or not nombre:
        raise ValueError(
            "El código y el nombre son obligatorios."
        )

    if (
        len(codigo) > 20
        or len(nombre) > 150
        or len(marca) > 100
        or len(imagen) > 255
    ):
        raise ValueError(
            "Uno de los campos supera el tamaño permitido."
        )

    if imagen and not (
        imagen.startswith("/static/img/")
        or imagen.startswith("https://")
    ):
        raise ValueError(
            "Utiliza una ruta /static/img/ o una URL HTTPS."
        )

    try:
        id_categoria = int(datos.get("id_categoria"))
        stock = int(datos.get("stock"))
        precio = Decimal(str(datos.get("precio")))

        anterior_texto = datos.get("precio_anterior")

        precio_anterior = (
            Decimal(str(anterior_texto))
            if anterior_texto not in (None, "")
            else None
        )

    except (
        ValueError, TypeError, InvalidOperation
    ):
        raise ValueError(
            "Verifica la categoría, precio y stock."
        )

    if id_categoria <= 0 or stock < 0:
        raise ValueError(
            "La categoría o el stock no son válidos."
        )

    if (
        precio < 0
        or not precio.is_finite()
        or precio > Decimal("99999999.99")
    ):
        raise ValueError("Precio inválido.")

    if precio.as_tuple().exponent < -2:
        raise ValueError(
            "El precio admite máximo dos decimales."
        )

    if precio_anterior is not None:
        if (
            precio_anterior < 0
            or not precio_anterior.is_finite()
            or precio_anterior > Decimal("99999999.99")
            or precio_anterior.as_tuple().exponent < -2
        ):
            raise ValueError(
                "El precio anterior no es válido."
            )

    return {
        "codigo": codigo,
        "nombre": nombre,
        "marca": marca,
        "descripcion": descripcion,
        "imagen": imagen,
        "id_categoria": id_categoria,
        "precio": precio,
        "precio_anterior": precio_anterior,
        "stock": stock
    }


def guardar_imagen_producto(archivo):
    if not archivo or not archivo.filename:
        return None

    try:
        archivo.stream.seek(0)

        with Image.open(archivo.stream) as imagen:
            formato = imagen.format
            imagen.verify()

        if formato not in ("JPEG", "PNG", "WEBP"):
            raise ValueError("Solo se permiten imágenes JPG, PNG y WEBP.")

        archivo.stream.seek(0, os.SEEK_END)

        if archivo.stream.tell() > 5 * 1024 * 1024:
            raise ValueError("La imagen no puede superar 5 MB.")

        archivo.stream.seek(0)

        resultado = cloudinary.uploader.upload(
            archivo.stream,
            folder="nexus_gamer/productos",
            public_id=uuid.uuid4().hex,
            resource_type="image",
            overwrite=False
        )

        if not resultado.get("secure_url"):
            raise RuntimeError("Cloudinary no devolvió la URL de la imagen.")

        return resultado["secure_url"]

    except (UnidentifiedImageError, OSError, Image.DecompressionBombError) as error:
        raise ValueError("El archivo no es una imagen válida.") from error

    except CloudinaryError as error:
        app.logger.exception("Error al subir imagen a Cloudinary")
        raise RuntimeError("No se pudo subir la imagen a Cloudinary.") from error


@app.route("/admin/productos/guardar", methods=["POST"])
@proteger_admin
@solo_admin
def admin_guardar_producto():
    conexion = None
    cursor = None
    imagen_nueva = None
    guardado = False

    try:
        datos = request.form.to_dict() if request.mimetype == "multipart/form-data" else request.get_json(silent=True)

        if not isinstance(datos, dict):
            raise ValueError("Datos del producto inválidos.")

        id_original = datos.get("id_producto")
        id_producto = int(id_original) if id_original not in (None, "") else None

        if id_producto is not None and id_producto <= 0:
            raise ValueError("ID de producto inválido.")

        conexion = conectar_db()
        cursor = conexion.cursor(dictionary=True)

        if id_producto is not None:
            cursor.execute("SELECT imagen FROM productos WHERE id_producto = %s FOR UPDATE", (id_producto,))
            anterior = cursor.fetchone()

            if anterior is None:
                raise ValueError("El producto no existe.")

            datos["imagen"] = anterior["imagen"] or ""

        else:
            datos["imagen"] = ""

        archivo = request.files.get("imagen_archivo")

        if archivo and archivo.filename:
            imagen_nueva = guardar_imagen_producto(archivo)
            datos["imagen"] = imagen_nueva

        elif id_producto is None and request.is_json:
            datos["imagen"] = str((request.get_json(silent=True) or {}).get("imagen") or "")

        producto = validar_producto(datos)

        cursor.execute("SELECT id_categoria FROM categorias WHERE id_categoria = %s", (producto["id_categoria"],))

        if not cursor.fetchone():
            raise ValueError("La categoría seleccionada no existe.")

        valores = (
            producto["codigo"], producto["nombre"], producto["marca"],
            producto["descripcion"], producto["precio"], producto["precio_anterior"],
            producto["stock"], producto["imagen"], producto["id_categoria"]
        )

        if id_producto is not None:
            cursor.execute("""
                UPDATE productos SET codigo = %s, nombre = %s, marca = %s,
                    descripcion = %s, precio = %s, precio_anterior = %s,
                    stock = %s, imagen = %s, id_categoria = %s
                WHERE id_producto = %s
            """, valores + (id_producto,))

            mensaje = "Producto actualizado correctamente."

        else:
            cursor.execute("""
                INSERT INTO productos (
                    codigo, nombre, marca, descripcion, precio, precio_anterior,
                    stock, imagen, id_categoria, activo
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, TRUE)
            """, valores)

            id_producto = cursor.lastrowid
            mensaje = "Producto agregado y publicado correctamente."

        conexion.commit()
        guardado = True

        return jsonify({"ok": True, "mensaje": mensaje, "id_producto": id_producto})

    except IntegrityError:
        if conexion:
            conexion.rollback()

        return jsonify({"ok": False, "mensaje": "El código del producto ya existe. Utiliza uno diferente."}), 400

    except (ValueError, TypeError, InvalidOperation) as error:
        if conexion:
            conexion.rollback()

        return jsonify({"ok": False, "mensaje": str(error)}), 400

    except Exception:
        if conexion:
            conexion.rollback()

        app.logger.exception("Error guardando producto")

        return jsonify({"ok": False, "mensaje": "No se pudo guardar el producto."}), 500

    finally:
        if imagen_nueva and not guardado:
            try:
                from urllib.parse import urlparse

                ruta = urlparse(imagen_nueva).path
                public_id = ruta.split("/upload/", 1)[1]
                public_id = public_id.split("/", 1)[1]
                public_id = public_id.rsplit(".", 1)[0]

                if public_id.startswith("nexus_gamer/productos/"):
                    cloudinary.uploader.destroy(public_id, resource_type="image")

            except Exception:
                app.logger.exception("No se pudo limpiar la imagen de Cloudinary")

        cerrar_db(conexion, cursor)


@app.route(
    "/admin/productos/<int:id_producto>/estado",
    methods=["POST"]
)
@proteger_admin
@solo_admin
def admin_estado_producto(id_producto):
    conexion = None
    cursor = None

    try:
        datos = request.get_json(silent=True) or {}

        activo = datos.get("activo")

        if not isinstance(activo, bool):
            raise ValueError(
                "El estado debe ser verdadero o falso."
            )

        conexion = conectar_db()
        cursor = conexion.cursor()

        cursor.execute("""
            UPDATE productos
            SET activo = %s
            WHERE id_producto = %s
        """, (
            activo,
            id_producto
        ))

        if cursor.rowcount == 0:
            cursor.execute("""
                SELECT id_producto
                FROM productos
                WHERE id_producto = %s
            """, (id_producto,))

            if not cursor.fetchone():
                raise ValueError(
                    "El producto no existe."
                )

        conexion.commit()

        return jsonify({
            "ok": True,
            "mensaje": (
                "Producto restaurado correctamente."
                if activo
                else "Producto ocultado correctamente."
            )
        })

    except ValueError as error:
        if conexion:
            conexion.rollback()

        return jsonify({
            "ok": False,
            "mensaje": str(error)
        }), 400

    except Exception:
        if conexion:
            conexion.rollback()

        app.logger.exception(
            "Error cambiando estado del producto"
        )

        return jsonify({
            "ok": False,
            "mensaje": "No se pudo cambiar el estado."
        }), 500

    finally:
        cerrar_db(conexion, cursor)


@app.route(
    "/admin/pedidos/<int:id_venta>/estado",
    methods=["POST"]
)
@proteger_admin
@solo_admin
def admin_estado_pedido(id_venta):
    conexion = None
    cursor = None

    try:
        datos = request.get_json(silent=True) or {}

        estado = datos.get("estado")

        estados_permitidos = (
            "Pendiente",
            "Procesando",
            "Completada",
            "Cancelada"
        )

        if estado not in estados_permitidos:
            raise ValueError(
                "El estado del pedido no es válido."
            )

        conexion = conectar_db()
        cursor = conexion.cursor(dictionary=True)

        cursor.execute("""
            SELECT estado
            FROM ventas
            WHERE id_venta = %s
            FOR UPDATE
        """, (id_venta,))

        pedido = cursor.fetchone()

        if not pedido:
            raise ValueError(
                "El pedido no existe."
            )

        if (
            pedido["estado"] in ("Completada", "Cancelada")
            and pedido["estado"] != estado
        ):
            raise ValueError(
                "No puedes cambiar un pedido ya cerrado."
            )

        cursor.execute("""
            UPDATE ventas
            SET estado = %s
            WHERE id_venta = %s
        """, (
            estado,
            id_venta
        ))

        conexion.commit()

        return jsonify({
            "ok": True,
            "mensaje": "Estado del pedido actualizado."
        })

    except ValueError as error:
        if conexion:
            conexion.rollback()

        return jsonify({
            "ok": False,
            "mensaje": str(error)
        }), 400

    except Exception:
        if conexion:
            conexion.rollback()

        app.logger.exception(
            "Error actualizando pedido"
        )

        return jsonify({
            "ok": False,
            "mensaje": "No se pudo actualizar el pedido."
        }), 500

    finally:
        cerrar_db(conexion, cursor)


@app.route("/admin/logout", methods=["POST"])
@acceso_requerido
def admin_logout():
    session.clear()

    return redirect(url_for("admin_login"))


if __name__ == "__main__":
    app.run(
        debug=os.getenv("FLASK_DEBUG") == "1"
    )