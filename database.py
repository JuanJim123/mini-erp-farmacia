import sqlite3

def init_db():
    conn = sqlite3.connect('farmacia.db')
    c = conn.cursor()

    # ── TABLAS ──────────────────────────────────────────────────────────────

    c.execute('''CREATE TABLE IF NOT EXISTS medicamentos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        categoria TEXT NOT NULL,
        precio REAL NOT NULL,
        stock INTEGER NOT NULL,
        stock_minimo INTEGER NOT NULL DEFAULT 10,
        fecha_vencimiento TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS ventas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        medicamento_id INTEGER NOT NULL,
        cantidad INTEGER NOT NULL,
        precio_unitario REAL NOT NULL,
        total REAL NOT NULL,
        fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (medicamento_id) REFERENCES medicamentos(id)
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS proveedores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        contacto TEXT,
        telefono TEXT,
        email TEXT,
        categoria TEXT DEFAULT 'Otro',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS ordenes_compra (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        proveedor_id INTEGER NOT NULL,
        medicamento_id INTEGER NOT NULL,
        cantidad INTEGER NOT NULL,
        precio_unitario REAL NOT NULL,
        costo_total REAL NOT NULL,
        estado TEXT DEFAULT 'pendiente',
        fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (proveedor_id) REFERENCES proveedores(id),
        FOREIGN KEY (medicamento_id) REFERENCES medicamentos(id)
    )''')

    # ── MEDICAMENTOS ────────────────────────────────────────────────────────

    c.execute("SELECT COUNT(*) FROM medicamentos")
    if c.fetchone()[0] == 0:
        medicamentos = [
            # (nombre, categoria, precio, stock, stock_minimo, fecha_vencimiento)

            # Vigentes
            ('Paracetamol 500mg',      'Analgésico',        5.50,  95,  20, '2026-12-01'),
            ('Amoxicilina 500mg',      'Antibiótico',      18.00,  38,  15, '2026-08-15'),
            ('Ibuprofeno 400mg',       'Antiinflamatorio',  7.25,  62,  20, '2027-03-10'),
            ('Loratadina 10mg',        'Antihistamínico',   6.00,  54,  10, '2026-11-20'),
            ('Omeprazol 20mg',         'Gastro',           12.50,  22,  10, '2026-09-05'),
            ('Metformina 850mg',       'Antidiabético',     9.00,  18,  15, '2027-01-30'),
            ('Atorvastatina 20mg',     'Cardiovascular',   22.00,  14,  10, '2026-10-12'),
            ('Vitamina C 1000mg',      'Suplemento',        4.75, 130,  30, '2027-06-01'),
            ('Azitromicina 500mg',     'Antibiótico',      24.00,   8,  10, '2026-07-20'),
            ('Diclofenac 50mg',        'Antiinflamatorio',  6.50,  45,  15, '2027-02-28'),
            ('Ranitidina 150mg',       'Gastro',            8.00,  30,  10, '2026-10-30'),
            ('Clonazepam 0.5mg',       'Neurológico',      15.00,   7,  10, '2026-06-15'),
            ('Metronidazol 500mg',     'Antibiótico',      10.50,  25,  10, '2026-12-20'),
            ('Salbutamol Inhalador',   'Respiratorio',     45.00,  12,   5, '2027-04-01'),
            ('Losartan 50mg',          'Cardiovascular',   14.00,  20,  10, '2027-01-15'),
            ('Glibenclamida 5mg',      'Antidiabético',     7.00,  16,  10, '2026-11-10'),
            ('Hidrocortisona Crema',   'Dermatológico',    18.50,  28,   8, '2027-05-20'),
            ('Cetirizina 10mg',        'Antihistamínico',   5.25,  40,  10, '2027-03-15'),
            ('Vitamina D3 1000UI',     'Suplemento',        9.50,  85,  20, '2027-08-01'),
            ('Hierro Fumarato 200mg',  'Suplemento',       11.00,  33,  15, '2027-02-10'),

            # Proximos a vencer (dentro de 30 dias desde el 6 de mayo)
            ('Eritromicina 250mg',     'Antibiótico',      14.00,  11,   8, '2026-05-20'),
            ('Nifedipino 10mg',        'Cardiovascular',   19.00,   9,   5, '2026-05-28'),

            # Ya vencidos (fechas anteriores al 6 de mayo de 2026)
            ('Aspirina 100mg',         'Analgésico',        3.50,  15,  10, '2026-03-15'),
            ('Ampicilina 500mg',       'Antibiótico',      16.00,   9,  10, '2026-04-01'),
            ('Dexametasona 4mg',       'Antiinflamatorio', 11.00,   6,   5, '2026-04-20'),
            ('Vitamina B12 1000mcg',   'Suplemento',        8.25,  22,  10, '2026-05-01'),
            ('Clopidogrel 75mg',       'Cardiovascular',   28.00,   4,   5, '2026-05-03'),
        ]
        c.executemany(
            "INSERT INTO medicamentos (nombre, categoria, precio, stock, stock_minimo, fecha_vencimiento) VALUES (?,?,?,?,?,?)",
            medicamentos
        )

    # ── PROVEEDORES ─────────────────────────────────────────────────────────

    c.execute("SELECT COUNT(*) FROM proveedores")
    if c.fetchone()[0] == 0:
        proveedores = [
            ('Distribuidora Médica SA',   'Carlos López',    '+502 5555-1234', 'ventas@distmed.com',       'Medicamentos generales', '2026-04-27 08:00:00'),
            ('FarmaSupply GT',            'Ana Rodríguez',   '+502 4444-5678', 'pedidos@farmasupply.com',  'Antibióticos',           '2026-04-27 09:30:00'),
            ('Suplementos Naturales',     'Pedro Martínez',  '+502 3333-9012', 'info@supnat.com',          'Suplementos',            '2026-04-28 10:00:00'),
            ('CardioFarma GT',            'Lucía Herrera',   '+502 2222-3456', 'compras@cardiofarma.com',  'Cardiovascular',         '2026-04-28 14:00:00'),
            ('BioLab Centroamérica',      'Mario Fuentes',   '+502 6666-7890', 'mario@biolab.com',         'Medicamentos generales', '2026-04-29 08:30:00'),
            ('Dermaceutica GT',           'Sofía Méndez',    '+502 7777-2345', 'sofia@dermaceutica.com',   'Dermatológico',          '2026-04-30 11:00:00'),
            ('NutriVida SA',              'Roberto Paz',     '+502 8888-6789', 'roberto@nutrivida.com',    'Suplementos',            '2026-05-02 09:00:00'),
            ('RespiraMed',                'Diana Torres',    '+502 9999-0123', 'diana@respiramed.com',     'Respiratorio',           '2026-05-03 10:30:00'),
        ]
        c.executemany(
            "INSERT INTO proveedores (nombre, contacto, telefono, email, categoria, created_at) VALUES (?,?,?,?,?,?)",
            proveedores
        )

    # ── VENTAS ──────────────────────────────────────────────────────────────

    c.execute("SELECT COUNT(*) FROM ventas")
    if c.fetchone()[0] == 0:
        ventas = [
            # Lunes 27 de abril
            (1,  4,  5.50,  22.00, '2026-04-27 08:15:00'),
            (3,  2,  7.25,  14.50, '2026-04-27 09:02:00'),
            (8,  3,  4.75,  14.25, '2026-04-27 09:45:00'),
            (2,  1, 18.00,  18.00, '2026-04-27 10:20:00'),
            (4,  2,  6.00,  12.00, '2026-04-27 11:00:00'),
            (10, 3,  6.50,  19.50, '2026-04-27 11:35:00'),
            (1,  6,  5.50,  33.00, '2026-04-27 12:10:00'),
            (5,  1, 12.50,  12.50, '2026-04-27 13:05:00'),
            (19, 2,  9.50,  19.00, '2026-04-27 14:20:00'),
            (8,  5,  4.75,  23.75, '2026-04-27 15:00:00'),
            (6,  1,  9.00,   9.00, '2026-04-27 15:45:00'),
            (13, 2, 10.50,  21.00, '2026-04-27 16:30:00'),

            # Martes 28 de abril
            (1,  5,  5.50,  27.50, '2026-04-28 08:10:00'),
            (7,  1, 22.00,  22.00, '2026-04-28 09:00:00'),
            (3,  3,  7.25,  21.75, '2026-04-28 09:50:00'),
            (18, 2,  5.25,  10.50, '2026-04-28 10:30:00'),
            (2,  2, 18.00,  36.00, '2026-04-28 11:15:00'),
            (11, 1,  8.00,   8.00, '2026-04-28 12:00:00'),
            (4,  3,  6.00,  18.00, '2026-04-28 13:20:00'),
            (8,  4,  4.75,  19.00, '2026-04-28 14:05:00'),
            (15, 2, 14.00,  28.00, '2026-04-28 14:50:00'),
            (20, 1, 11.00,  11.00, '2026-04-28 15:30:00'),
            (1,  3,  5.50,  16.50, '2026-04-28 16:20:00'),

            # Miercoles 29 de abril
            (3,  4,  7.25,  29.00, '2026-04-29 08:05:00'),
            (8,  6,  4.75,  28.50, '2026-04-29 08:55:00'),
            (1,  7,  5.50,  38.50, '2026-04-29 09:40:00'),
            (9,  1, 24.00,  24.00, '2026-04-29 10:15:00'),
            (5,  2, 12.50,  25.00, '2026-04-29 11:00:00'),
            (6,  1,  9.00,   9.00, '2026-04-29 11:45:00'),
            (17, 1, 18.50,  18.50, '2026-04-29 12:30:00'),
            (14, 1, 45.00,  45.00, '2026-04-29 13:10:00'),
            (4,  4,  6.00,  24.00, '2026-04-29 14:00:00'),
            (10, 2,  6.50,  13.00, '2026-04-29 14:45:00'),
            (19, 3,  9.50,  28.50, '2026-04-29 15:30:00'),
            (2,  1, 18.00,  18.00, '2026-04-29 16:15:00'),

            # Jueves 30 de abril
            (1,  8,  5.50,  44.00, '2026-04-30 08:20:00'),
            (3,  3,  7.25,  21.75, '2026-04-30 09:10:00'),
            (7,  2, 22.00,  44.00, '2026-04-30 09:55:00'),
            (18, 3,  5.25,  15.75, '2026-04-30 10:40:00'),
            (8,  5,  4.75,  23.75, '2026-04-30 11:20:00'),
            (11, 2,  8.00,  16.00, '2026-04-30 12:05:00'),
            (13, 1, 10.50,  10.50, '2026-04-30 12:50:00'),
            (15, 1, 14.00,  14.00, '2026-04-30 13:35:00'),
            (5,  2, 12.50,  25.00, '2026-04-30 14:20:00'),
            (20, 2, 11.00,  22.00, '2026-04-30 15:00:00'),
            (4,  2,  6.00,  12.00, '2026-04-30 15:45:00'),
            (16, 1,  7.00,   7.00, '2026-04-30 16:30:00'),
            (1,  4,  5.50,  22.00, '2026-04-30 17:00:00'),

            # Viernes 2 de mayo
            (1,  6,  5.50,  33.00, '2026-05-02 08:10:00'),
            (2,  3, 18.00,  54.00, '2026-05-02 08:55:00'),
            (3,  5,  7.25,  36.25, '2026-05-02 09:35:00'),
            (8,  8,  4.75,  38.00, '2026-05-02 10:10:00'),
            (9,  2, 24.00,  48.00, '2026-05-02 10:50:00'),
            (4,  3,  6.00,  18.00, '2026-05-02 11:30:00'),
            (19, 2,  9.50,  19.00, '2026-05-02 12:15:00'),
            (10, 4,  6.50,  26.00, '2026-05-02 13:00:00'),
            (14, 1, 45.00,  45.00, '2026-05-02 13:40:00'),
            (7,  1, 22.00,  22.00, '2026-05-02 14:20:00'),
            (5,  1, 12.50,  12.50, '2026-05-02 15:05:00'),
            (18, 4,  5.25,  21.00, '2026-05-02 15:50:00'),
            (20, 1, 11.00,  11.00, '2026-05-02 16:30:00'),

            # Sabado 3 de mayo
            (1,  9,  5.50,  49.50, '2026-05-03 08:30:00'),
            (3,  4,  7.25,  29.00, '2026-05-03 09:20:00'),
            (8,  7,  4.75,  33.25, '2026-05-03 10:00:00'),
            (2,  2, 18.00,  36.00, '2026-05-03 10:45:00'),
            (11, 2,  8.00,  16.00, '2026-05-03 11:30:00'),
            (4,  5,  6.00,  30.00, '2026-05-03 12:15:00'),
            (15, 2, 14.00,  28.00, '2026-05-03 13:00:00'),
            (17, 2, 18.50,  37.00, '2026-05-03 13:45:00'),
            (19, 4,  9.50,  38.00, '2026-05-03 14:30:00'),
            (6,  2,  9.00,  18.00, '2026-05-03 15:15:00'),
            (13, 3, 10.50,  31.50, '2026-05-03 16:00:00'),

            # Domingo 4 de mayo
            (1,  5,  5.50,  27.50, '2026-05-04 09:00:00'),
            (8,  4,  4.75,  19.00, '2026-05-04 09:45:00'),
            (3,  2,  7.25,  14.50, '2026-05-04 10:30:00'),
            (18, 3,  5.25,  15.75, '2026-05-04 11:15:00'),
            (4,  2,  6.00,  12.00, '2026-05-04 12:00:00'),
            (7,  1, 22.00,  22.00, '2026-05-04 12:45:00'),
            (5,  1, 12.50,  12.50, '2026-05-04 13:30:00'),
            (20, 2, 11.00,  22.00, '2026-05-04 14:15:00'),

            # Lunes 5 de mayo
            (1,  7,  5.50,  38.50, '2026-05-05 08:05:00'),
            (2,  2, 18.00,  36.00, '2026-05-05 08:50:00'),
            (3,  4,  7.25,  29.00, '2026-05-05 09:35:00'),
            (9,  1, 24.00,  24.00, '2026-05-05 10:20:00'),
            (8,  6,  4.75,  28.50, '2026-05-05 11:00:00'),
            (4,  3,  6.00,  18.00, '2026-05-05 11:45:00'),
            (15, 1, 14.00,  14.00, '2026-05-05 12:30:00'),
            (10, 3,  6.50,  19.50, '2026-05-05 13:15:00'),
            (19, 2,  9.50,  19.00, '2026-05-05 14:00:00'),
            (16, 2,  7.00,  14.00, '2026-05-05 14:45:00'),
            (7,  1, 22.00,  22.00, '2026-05-05 15:30:00'),
            (11, 1,  8.00,   8.00, '2026-05-05 16:15:00'),

            # Martes 6 de mayo
            (1,  5,  5.50,  27.50, '2026-05-06 08:00:00'),
            (3,  3,  7.25,  21.75, '2026-05-06 08:45:00'),
            (8,  4,  4.75,  19.00, '2026-05-06 09:30:00'),
            (2,  1, 18.00,  18.00, '2026-05-06 10:15:00'),
            (4,  2,  6.00,  12.00, '2026-05-06 11:00:00'),
            (18, 2,  5.25,  10.50, '2026-05-06 11:45:00'),
            (7,  1, 22.00,  22.00, '2026-05-06 12:30:00'),
            (5,  1, 12.50,  12.50, '2026-05-06 13:15:00'),
        ]
        c.executemany(
            "INSERT INTO ventas (medicamento_id, cantidad, precio_unitario, total, fecha) VALUES (?,?,?,?,?)",
            ventas
        )

    # ── ORDENES DE COMPRA ───────────────────────────────────────────────────

    c.execute("SELECT COUNT(*) FROM ordenes_compra")
    if c.fetchone()[0] == 0:
        ordenes = [
            # 27 abril
            (1, 1,  200, 2.80,  560.00, 'recibida',  '2026-04-27 10:00:00'),
            (2, 2,   80, 9.50,  760.00, 'recibida',  '2026-04-27 10:30:00'),
            (5, 10, 100, 3.20,  320.00, 'recibida',  '2026-04-27 14:00:00'),
            # 28 abril
            (1, 3,  150, 3.50,  525.00, 'recibida',  '2026-04-28 09:00:00'),
            (3, 8,  200, 2.10,  420.00, 'recibida',  '2026-04-28 11:00:00'),
            (4, 7,   50, 11.00, 550.00, 'recibida',  '2026-04-28 15:00:00'),
            # 29 abril
            (2, 9,   60, 12.00, 720.00, 'recibida',  '2026-04-29 08:30:00'),
            (5, 11, 100, 4.00,  400.00, 'recibida',  '2026-04-29 13:00:00'),
            (6, 17,  80, 9.50,  760.00, 'recibida',  '2026-04-29 16:00:00'),
            # 30 abril
            (3, 19, 150, 5.00,  750.00, 'recibida',  '2026-04-30 09:00:00'),
            (4, 15, 100, 7.00,  700.00, 'recibida',  '2026-04-30 14:00:00'),
            (7, 20, 120, 5.50,  660.00, 'recibida',  '2026-04-30 16:00:00'),
            # 2 mayo
            (1, 1,  150, 2.80,  420.00, 'recibida',  '2026-05-02 08:00:00'),
            (2, 13, 100, 5.20,  520.00, 'recibida',  '2026-05-02 10:00:00'),
            (8, 14,  30, 22.00, 660.00, 'recibida',  '2026-05-02 14:00:00'),
            # 3 mayo
            (5, 3,  200, 3.50,  700.00, 'recibida',  '2026-05-03 09:30:00'),
            (3, 18, 200, 2.60,  520.00, 'recibida',  '2026-05-03 12:00:00'),
            (1, 4,  150, 3.00,  450.00, 'aprobada',  '2026-05-03 15:00:00'),
            # 4 mayo
            (4, 7,   60, 11.00, 660.00, 'aprobada',  '2026-05-04 10:00:00'),
            (6, 12,  50, 7.50,  375.00, 'pendiente', '2026-05-04 14:00:00'),
            # 5 mayo
            (2, 9,   80, 12.00, 960.00, 'pendiente', '2026-05-05 09:00:00'),
            (7, 8,  200, 2.10,  420.00, 'pendiente', '2026-05-05 11:00:00'),
            (1, 5,   80, 6.00,  480.00, 'pendiente', '2026-05-05 14:30:00'),
            # 6 mayo
            (5, 6,  100, 4.50,  450.00, 'pendiente', '2026-05-06 08:30:00'),
            (8, 14,  20, 22.00, 440.00, 'pendiente', '2026-05-06 10:00:00'),
        ]
        c.executemany(
            "INSERT INTO ordenes_compra (proveedor_id, medicamento_id, cantidad, precio_unitario, costo_total, estado, fecha) VALUES (?,?,?,?,?,?,?)",
            ordenes
        )

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    print("Base de datos creada correctamente.")
