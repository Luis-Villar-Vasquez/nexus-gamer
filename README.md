# 🎮 NEXUS GAMER

## Descripción del proyecto

Nexus Gamer es una tienda web orientada a la venta de productos tecnológicos y gaming.

El proyecto fue desarrollado utilizando Flask como framework de Python, MySQL para la gestión de los datos y tecnologías web como HTML, CSS y JavaScript para la interfaz.

Además, cuenta con un asistente virtual llamado **NEXUS AI**, que permite realizar consultas sobre los productos disponibles en la tienda, precios, stock, ofertas y recomendaciones de compra.

---

## 🚀 Tecnologías utilizadas

- Python
- Flask
- MySQL
- HTML5
- CSS3
- JavaScript
- Google GenAI
- python-dotenv
- Visual Studio Code

---

## 📁 Estructura del proyecto

```text
nexus_gamer/
│
├── app.py
├── .env
├── requirements.txt
├── README.md
│
├── database/
│   └── nexus_gamer.sql
│
├── templates/
│   └── index.html
│
├── static/
│   ├── css/
│   │   └── style.css
│   │
│   ├── js/
│   │   └── main.js
│   │
│   └── img/
│       └── imágenes de los productos
│
└── venv/
```

---

## 🛒 Funcionalidades principales

Nexus Gamer cuenta con las siguientes funcionalidades:

- Visualización del catálogo de productos.
- Búsqueda de productos.
- Filtros por categorías.
- Sección de ofertas.
- Sección de novedades.
- Carrito de compras.
- Productos favoritos.
- Panel de usuario.
- Diseño responsive para diferentes tamaños de pantalla.
- Asistente virtual NEXUS AI.

---

## 🗄️ Base de datos

El proyecto utiliza una base de datos MySQL llamada:

```text
nexus_gamer_db
```

La base de datos almacena la información necesaria para administrar el catálogo y otras operaciones de la tienda.

Las principales tablas son:

- categorias
- productos
- clientes
- ventas
- detalle_ventas
- ofertas
- novedades
- usuarios

El catálogo contiene 8 categorías:

- Laptops Gamer
- Componentes
- Monitores
- Teclados
- Mouse
- Audio
- Almacenamiento
- Setup Gamer

Actualmente se utilizan 24 productos de prueba distribuidos entre estas categorías.

---

## 🤖 NEXUS AI

NEXUS AI es el asistente virtual integrado en Nexus Gamer.

Su objetivo es ayudar al cliente a encontrar información relacionada con los productos de la tienda.

Puede responder consultas sobre:

- Productos disponibles.
- Precios.
- Stock.
- Ofertas.
- Productos nuevos.
- Recomendaciones según el presupuesto del cliente.
- Comparación básica de alternativas disponibles.

NEXUS AI utiliza la información actual del catálogo obtenida desde la aplicación y responde únicamente sobre productos registrados en Nexus Gamer.

El asistente está configurado para evitar inventar productos, precios o cantidades de stock que no estén disponibles en el catálogo.

También limita sus respuestas a consultas relacionadas con Nexus Gamer.

---

## 🔄 Funcionamiento de NEXUS AI

El funcionamiento general del asistente es:

```text
Usuario
   ↓
Interfaz web
   ↓
JavaScript
   ↓
Flask
   ↓
Catálogo de productos
   ↓
NEXUS AI
   ↓
Respuesta al usuario
```

Cuando el cliente realiza una pregunta, la aplicación obtiene los productos disponibles y prepara la información necesaria para que NEXUS AI pueda responder utilizando los datos del catálogo.

---

## 🧠 Modelos utilizados

NEXUS AI utiliza como modelo principal:

```text
gemini-3.5-flash-lite
```

Si el modelo principal presenta temporalmente un problema de disponibilidad, la aplicación intenta utilizar:

```text
gemini-3.8-flash
```

Esto permite contar con una alternativa cuando el modelo principal no se encuentra disponible.

---

## ⚙️ Instalación

### 1. Crear el entorno virtual

Desde la terminal:

```bash
python -m venv venv
```

### 2. Activar el entorno virtual

En Windows:

```bash
venv\Scripts\activate
```

Cuando esté activado aparecerá:

```text
(venv)
```

al inicio de la terminal.

---

## 📦 Instalar dependencias

El archivo `requirements.txt` contiene:

```text
Flask
mysql-connector-python
python-dotenv
google-genai
```

Para instalar las dependencias ejecutar:

```bash
pip install -r requirements.txt
```

---

## 🗃️ Configuración de MySQL

Importar el archivo:

```text
database/nexus_gamer.sql
```

Este archivo crea la base de datos:

```text
nexus_gamer_db
```

y las tablas necesarias para el proyecto.

También contiene los datos utilizados para el catálogo de prueba.

---

## 🔐 Variables de entorno

El proyecto utiliza un archivo `.env` para almacenar información privada de configuración.

Ejemplo:

```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=tu_contraseña
DB_NAME=nexus_gamer_db

GEMINI_API_KEY=tu_api_key
```

Por seguridad, las contraseñas y API Keys reales no deben compartirse ni publicarse.

---

## ▶️ Ejecutar el proyecto

Con MySQL funcionando y el entorno virtual activado, ejecutar:

```bash
python app.py
```

Flask iniciará el servidor local.

Luego ingresar desde el navegador a:

```text
http://127.0.0.1:5000
```

---

## 💬 Ejemplo de uso de NEXUS AI

El usuario puede escribir:

```text
Tengo S/ 5000 para comprar una laptop gamer.
¿Cuál me recomiendas y por qué?
```

NEXUS AI revisa los productos disponibles y puede recomendar una alternativa que se encuentre dentro del presupuesto indicado.

Otro ejemplo:

```text
Quiero una memoria RAM de 32 GB.
¿Qué tienen disponible?
```

El asistente consulta la información disponible en el catálogo y responde utilizando el producto correspondiente, junto con su precio y stock.

---

## 🎯 Objetivo del proyecto

El objetivo de Nexus Gamer es desarrollar una tienda web funcional que permita integrar programación web, base de datos e inteligencia artificial dentro de una misma aplicación.

El proyecto busca demostrar cómo una tienda virtual puede mejorar la interacción con sus usuarios mediante un asistente de IA conectado con la información de su catálogo.

---

## 👨‍💻 Proyecto académico

Nexus Gamer fue desarrollado con fines académicos como una aplicación web de comercio electrónico enfocada en productos tecnológicos y gaming.