CREATE TABLE IF NOT EXISTS categorias (
    id_categoria INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS productos (
    id_producto INT AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(20) UNIQUE NOT NULL,
    nombre VARCHAR(150) NOT NULL,
    marca VARCHAR(100),
    id_categoria INT,
    descripcion TEXT,
    precio DECIMAL(10,2) NOT NULL,
    precio_anterior DECIMAL(10,2),
    stock INT DEFAULT 0,
    imagen VARCHAR(255),
    destacado BOOLEAN DEFAULT FALSE,
    nuevo BOOLEAN DEFAULT FALSE,
    activo BOOLEAN DEFAULT TRUE,

    FOREIGN KEY (id_categoria)
        REFERENCES categorias(id_categoria)
);

CREATE TABLE IF NOT EXISTS clientes (
    id_cliente INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(120) NOT NULL,
    apellido VARCHAR(120),
    correo VARCHAR(150) UNIQUE,
    telefono VARCHAR(20),
    fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS ventas (
    id_venta INT AUTO_INCREMENT PRIMARY KEY,
    id_cliente INT,
    fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
    total DECIMAL(10,2) NOT NULL,
    estado VARCHAR(50) DEFAULT 'Completada',

    FOREIGN KEY (id_cliente)
        REFERENCES clientes(id_cliente)
);

CREATE TABLE IF NOT EXISTS detalle_ventas (
    id_detalle INT AUTO_INCREMENT PRIMARY KEY,
    id_venta INT NOT NULL,
    id_producto INT NOT NULL,
    cantidad INT NOT NULL,
    precio_unitario DECIMAL(10,2) NOT NULL,
    subtotal DECIMAL(10,2) NOT NULL,

    FOREIGN KEY (id_venta)
        REFERENCES ventas(id_venta),

    FOREIGN KEY (id_producto)
        REFERENCES productos(id_producto)
);

CREATE TABLE IF NOT EXISTS ofertas (
    id_oferta INT AUTO_INCREMENT PRIMARY KEY,
    id_producto INT NOT NULL,
    descuento INT NOT NULL,
    fecha_inicio DATE,
    fecha_fin DATE,
    activa BOOLEAN DEFAULT TRUE,

    FOREIGN KEY (id_producto)
        REFERENCES productos(id_producto)
);

CREATE TABLE IF NOT EXISTS novedades (
    id_novedad INT AUTO_INCREMENT PRIMARY KEY,
    titulo VARCHAR(150) NOT NULL,
    descripcion TEXT,
    imagen VARCHAR(255),
    fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
    activa BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS usuarios (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(120) NOT NULL,
    correo VARCHAR(150) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    rol VARCHAR(50) DEFAULT 'cliente',
    activo BOOLEAN DEFAULT TRUE
);

INSERT INTO categorias (nombre, descripcion) VALUES

(
    'Laptops Gamer',
    'Laptops de alto rendimiento para gaming'
),

(
    'Componentes',
    'Tarjetas gráficas, procesadores y componentes para PC'
),

(
    'Monitores',
    'Monitores gaming de alta frecuencia'
),

(
    'Teclados',
    'Teclados mecánicos y gaming'
),

(
    'Mouse',
    'Mouse de alta precisión para gaming'
),

(
    'Audio',
    'Audífonos, micrófonos y audio gamer'
),

(
    'Almacenamiento',
    'SSD y almacenamiento de alta velocidad'
),

(
    'Setup Gamer',
    'Accesorios y equipamiento para setup'
);

INSERT INTO productos
(
    codigo,
    nombre,
    marca,
    id_categoria,
    descripcion,
    precio,
    precio_anterior,
    stock,
    imagen,
    destacado,
    nuevo
)
VALUES
(
    'NG001',
    'ASUS ROG Strix G16 RTX 4060',
    'ASUS',
    1,
    'Laptop gamer Intel Core i7, 16GB RAM, SSD 1TB y RTX 4060.',
    6399.00,
    6799.00,
    6,
    'asus-rog-g16.png',
    TRUE,
    FALSE
);

INSERT INTO productos
(
    codigo,
    nombre,
    marca,
    id_categoria,
    descripcion,
    precio,
    precio_anterior,
    stock,
    imagen,
    destacado,
    nuevo
)
VALUES
(
    'NG002',
    'Lenovo Legion 5 RTX 4060',
    'Lenovo',
    1,
    'Laptop gamer Ryzen 7, 16GB RAM, SSD 1TB y RTX 4060.',
    5799.00,
    6199.00,
    5,
    'lenovo-legion-5.png',
    TRUE,
    FALSE
);

INSERT INTO productos
(
    codigo,
    nombre,
    marca,
    id_categoria,
    descripcion,
    precio,
    precio_anterior,
    stock,
    imagen,
    destacado,
    nuevo
)
VALUES
(
    'NG003',
    'Acer Nitro V 15 RTX 4050',
    'Acer',
    1,
    'Laptop gamer Intel Core i7, 16GB RAM, SSD 512GB y RTX 4050.',
    4299.00,
    4599.00,
    9,
    'acer-nitro-v15.png',
    FALSE,
    TRUE
);

INSERT INTO productos
(
    codigo,
    nombre,
    marca,
    id_categoria,
    descripcion,
    precio,
    precio_anterior,
    stock,
    imagen,
    destacado,
    nuevo
)
VALUES
(
    'NG004',
    'GeForce RTX 5070 12GB',
    'NVIDIA',
    2,
    'Tarjeta gráfica de nueva generación para gaming de alto rendimiento.',
    3299.00,
    3499.00,
    4,
    'rtx-5070.png',
    TRUE,
    TRUE
);

INSERT INTO productos
(
    codigo,
    nombre,
    marca,
    id_categoria,
    descripcion,
    precio,
    precio_anterior,
    stock,
    imagen,
    destacado,
    nuevo
)
VALUES
(
    'NG005',
    'GeForce RTX 5060 Ti 16GB',
    'NVIDIA',
    2,
    'Tarjeta gráfica para gaming en alta resolución.',
    2499.00,
    2699.00,
    7,
    'rtx-5060-ti.png',
    TRUE,
    TRUE
);

INSERT INTO productos
(
    codigo,
    nombre,
    marca,
    id_categoria,
    descripcion,
    precio,
    precio_anterior,
    stock,
    imagen,
    destacado,
    nuevo
)
VALUES
(
    'NG006',
    'AMD Ryzen 7 7800X3D',
    'AMD',
    2,
    'Procesador de alto rendimiento optimizado para gaming.',
    1699.00,
    1849.00,
    8,
    'ryzen-7-7800x3d.png',
    TRUE,
    FALSE
);

INSERT INTO productos
(
    codigo,
    nombre,
    marca,
    id_categoria,
    descripcion,
    precio,
    precio_anterior,
    stock,
    imagen,
    destacado,
    nuevo
)
VALUES
(
    'NG007',
    'LG UltraGear 27" 180Hz',
    'LG',
    3,
    'Monitor gamer Full HD IPS de 27 pulgadas y 180Hz.',
    1099.00,
    1299.00,
    12,
    'lg-ultragear-27.png',
    TRUE,
    FALSE
);

INSERT INTO productos
(
    codigo,
    nombre,
    marca,
    id_categoria,
    descripcion,
    precio,
    precio_anterior,
    stock,
    imagen,
    destacado,
    nuevo
)
VALUES
(
    'NG008',
    'Samsung Odyssey G5 27"',
    'Samsung',
    3,
    'Monitor gaming QHD de 27 pulgadas y alta frecuencia.',
    1299.00,
    1499.00,
    8,
    'samsung-odyssey-g5.png',
    FALSE,
    FALSE
);

INSERT INTO productos
(
    codigo,
    nombre,
    marca,
    id_categoria,
    descripcion,
    precio,
    precio_anterior,
    stock,
    imagen,
    destacado,
    nuevo
)
VALUES
(
    'NG009',
    'ASUS TUF Gaming 27" 180Hz',
    'ASUS',
    3,
    'Monitor gamer IPS Full HD de 180Hz.',
    1199.00,
    1349.00,
    10,
    'asus-tuf-monitor.png',
    TRUE,
    TRUE
);

INSERT INTO productos
(
    codigo,
    nombre,
    marca,
    id_categoria,
    descripcion,
    precio,
    precio_anterior,
    stock,
    imagen,
    destacado,
    nuevo
)
VALUES
(
    'NG010',
    'HyperX Alloy Origins Core',
    'HyperX',
    4,
    'Teclado mecánico gamer TKL con iluminación RGB.',
    349.00,
    399.00,
    15,
    'hyperx-alloy.png',
    TRUE,
    FALSE
);

INSERT INTO productos
(
    codigo,
    nombre,
    marca,
    id_categoria,
    descripcion,
    precio,
    precio_anterior,
    stock,
    imagen,
    destacado,
    nuevo
)
VALUES
(
    'NG011',
    'Logitech G Pro X TKL',
    'Logitech',
    4,
    'Teclado gamer TKL diseñado para gaming competitivo.',
    699.00,
    749.00,
    7,
    'logitech-pro-x-tkl.png',
    FALSE,
    TRUE
);

INSERT INTO productos
(
    codigo,
    nombre,
    marca,
    id_categoria,
    descripcion,
    precio,
    precio_anterior,
    stock,
    imagen,
    destacado,
    nuevo
)
VALUES
(
    'NG012',
    'Razer BlackWidow V4',
    'Razer',
    4,
    'Teclado mecánico gamer RGB con switches de alto rendimiento.',
    649.00,
    729.00,
    6,
    'razer-blackwidow-v4.png',
    TRUE,
    FALSE
);

INSERT INTO productos
(
    codigo,
    nombre,
    marca,
    id_categoria,
    descripcion,
    precio,
    precio_anterior,
    stock,
    imagen,
    destacado,
    nuevo
)
VALUES
(
    'NG013',
    'Logitech G502 X',
    'Logitech',
    5,
    'Mouse gamer con sensor HERO 25K y switches LIGHTFORCE.',
    309.00,
    399.00,
    18,
    'logitech-g502x.png',
    TRUE,
    FALSE
);

INSERT INTO productos
(
    codigo,
    nombre,
    marca,
    id_categoria,
    descripcion,
    precio,
    precio_anterior,
    stock,
    imagen,
    destacado,
    nuevo
)
VALUES
(
    'NG014',
    'Logitech G Pro X Superlight 2',
    'Logitech',
    5,
    'Mouse inalámbrico ultraligero para gaming competitivo.',
    599.00,
    649.00,
    10,
    'logitech-superlight-2.png',
    TRUE,
    TRUE
);

INSERT INTO productos
(
    codigo,
    nombre,
    marca,
    id_categoria,
    descripcion,
    precio,
    precio_anterior,
    stock,
    imagen,
    destacado,
    nuevo
)
VALUES
(
    'NG015',
    'Razer DeathAdder V3',
    'Razer',
    5,
    'Mouse gamer ergonómico de alta precisión.',
    299.00,
    349.00,
    13,
    'razer-deathadder-v3.png',
    FALSE,
    FALSE
);

INSERT INTO productos
(
    codigo,
    nombre,
    marca,
    id_categoria,
    descripcion,
    precio,
    precio_anterior,
    stock,
    imagen,
    destacado,
    nuevo
)
VALUES
(
    'NG016',
    'HyperX Cloud III',
    'HyperX',
    6,
    'Audífonos gamer con sonido envolvente y micrófono desmontable.',
    399.00,
    449.00,
    11,
    'hyperx-cloud-3.png',
    TRUE,
    FALSE
);

INSERT INTO productos
(
    codigo,
    nombre,
    marca,
    id_categoria,
    descripcion,
    precio,
    precio_anterior,
    stock,
    imagen,
    destacado,
    nuevo
)
VALUES
(
    'NG017',
    'Logitech G733 Lightspeed',
    'Logitech',
    6,
    'Audífonos gamer inalámbricos con iluminación RGB.',
    499.00,
    569.00,
    8,
    'logitech-g733.png',
    FALSE,
    FALSE
);

INSERT INTO productos
(
    codigo,
    nombre,
    marca,
    id_categoria,
    descripcion,
    precio,
    precio_anterior,
    stock,
    imagen,
    destacado,
    nuevo
)
VALUES
(
    'NG018',
    'Razer BlackShark V2 Pro',
    'Razer',
    6,
    'Headset inalámbrico para gaming competitivo.',
    699.00,
    749.00,
    5,
    'razer-blackshark-v2.png',
    TRUE,
    TRUE
);

INSERT INTO productos
(
    codigo,
    nombre,
    marca,
    id_categoria,
    descripcion,
    precio,
    precio_anterior,
    stock,
    imagen,
    destacado,
    nuevo
)
VALUES
(
    'NG019',
    'Kingston NV3 SSD 1TB',
    'Kingston',
    7,
    'SSD NVMe PCIe de 1TB para almacenamiento de alta velocidad.',
    299.00,
    349.00,
    20,
    'kingston-nv3-1tb.png',
    FALSE,
    FALSE
);

INSERT INTO productos
(
    codigo,
    nombre,
    marca,
    id_categoria,
    descripcion,
    precio,
    precio_anterior,
    stock,
    imagen,
    destacado,
    nuevo
)
VALUES
(
    'NG020',
    'Samsung 990 PRO SSD 1TB',
    'Samsung',
    7,
    'SSD NVMe de alto rendimiento para gaming y creación de contenido.',
    499.00,
    549.00,
    12,
    'samsung-990-pro.png',
    TRUE,
    FALSE
);

INSERT INTO productos
(
    codigo,
    nombre,
    marca,
    id_categoria,
    descripcion,
    precio,
    precio_anterior,
    stock,
    imagen,
    destacado,
    nuevo
)
VALUES
(
    'NG021',
    'Corsair Vengeance RGB 32GB DDR5',
    'Corsair',
    2,
    'Kit de memoria RAM DDR5 32GB con iluminación RGB.',
    499.00,
    559.00,
    14,
    'corsair-ddr5.png',
    FALSE,
    FALSE
);

INSERT INTO productos
(
    codigo,
    nombre,
    marca,
    id_categoria,
    descripcion,
    precio,
    precio_anterior,
    stock,
    imagen,
    destacado,
    nuevo
)
VALUES
(
    'NG022',
    'Secretlab Titan Evo',
    'Secretlab',
    8,
    'Silla ergonómica premium diseñada para largas sesiones gaming.',
    2199.00,
    2399.00,
    3,
    'secretlab-titan.png',
    TRUE,
    FALSE
);

INSERT INTO productos
(
    codigo,
    nombre,
    marca,
    id_categoria,
    descripcion,
    precio,
    precio_anterior,
    stock,
    imagen,
    destacado,
    nuevo
)
VALUES
(
    'NG023',
    'Logitech G923 Racing Wheel',
    'Logitech',
    8,
    'Volante gamer con tecnología TRUEFORCE y pedales.',
    1499.00,
    1699.00,
    4,
    'logitech-g923.png',
    TRUE,
    FALSE
);

INSERT INTO productos
(
    codigo,
    nombre,
    marca,
    id_categoria,
    descripcion,
    precio,
    precio_anterior,
    stock,
    imagen,
    destacado,
    nuevo
)
VALUES
(
    'NG024',
    'Razer Firefly V2 RGB',
    'Razer',
    8,
    'Mousepad gaming rígido con iluminación RGB.',
    249.00,
    299.00,
    16,
    'razer-firefly.png',
    FALSE,
    FALSE
);

SELECT
    p.codigo,
    p.nombre,
    p.marca,
    c.nombre AS categoria,
    p.precio,
    p.precio_anterior,
    p.stock
FROM productos p
INNER JOIN categorias c
    ON p.id_categoria = c.id_categoria
ORDER BY p.id_producto;

UPDATE productos
SET imagen = CASE codigo

    WHEN 'NG001' THEN 'ASUS ROG Strix G16 RTX 4060.webp'
    WHEN 'NG002' THEN 'Lenovo Legion 5 RTX 4060.webp'
    WHEN 'NG003' THEN 'Acer Nitro V 15 RTX 4050.webp'
    WHEN 'NG004' THEN 'GeForce RTX 5070 12GB.webp'
    WHEN 'NG005' THEN 'GeForce RTX 5060 Ti 16GB.webp'
    WHEN 'NG006' THEN 'AMD Ryzen 7 7800X3D.webp'
    WHEN 'NG007' THEN 'LG UltraGear 27 180Hz.webp'
    WHEN 'NG008' THEN 'Samsung Odyssey G5 27.webp'
    WHEN 'NG009' THEN 'ASUS TUF Gaming 27 180Hz.webp'
    WHEN 'NG010' THEN 'HyperX Alloy Origins Core.webp'
    WHEN 'NG011' THEN 'Logitech G Pro X TKL.webp'
    WHEN 'NG012' THEN 'Razer BlackWidow V4.webp'
    WHEN 'NG013' THEN 'Logitech G502 X.webp'
    WHEN 'NG014' THEN 'Logitech G Pro X Superlight 2.jpg'
    WHEN 'NG015' THEN 'Razer DeathAdder V3.webp'
    WHEN 'NG016' THEN 'HyperX Cloud III.webp'
    WHEN 'NG017' THEN 'Logitech G733 Lightspeed.webp'
    WHEN 'NG018' THEN 'Razer BlackShark V2 Pro.webp'
    WHEN 'NG019' THEN 'Kingston NV3 SSD 1TB.webp'
    WHEN 'NG020' THEN 'Samsung 990 PRO SSD 1TB.webp'
    WHEN 'NG021' THEN 'Corsair Vengeance RGB 32GB DDR5.webp'
    WHEN 'NG022' THEN 'Secretlab Titan Evo.webp'
    WHEN 'NG023' THEN 'Logitech G923 Racing Wheel.jpg'
    WHEN 'NG024' THEN 'Razer Firefly V2 RGB.webp'

END
WHERE codigo BETWEEN 'NG001' AND 'NG024';

SELECT
    codigo,
    nombre,
    imagen
FROM productos
ORDER BY id_producto;