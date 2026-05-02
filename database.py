import sqlite3

def init_db():
    conn = sqlite3.connect('farmacia.db')
    c = conn.cursor()

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

    c.execute("SELECT COUNT(*) FROM medicamentos")
    if c.fetchone()[0] == 0:
        medicamentos = [
            ('Paracetamol 500mg', 'Analgésico', 5.50, 120, 20, '2026-12-01'),
            ('Amoxicilina 500mg', 'Antibiótico', 18.00, 45, 15, '2026-08-15'),
            ('Ibuprofeno 400mg', 'Antiinflamatorio', 7.25, 80, 20, '2027-03-10'),
            ('Loratadina 10mg', 'Antihistamínico', 6.00, 60, 10, '2026-11-20'),
            ('Omeprazol 20mg', 'Gastro', 12.50, 30, 10, '2026-09-05'),
            ('Metformina 850mg', 'Antidiabético', 9.00, 25, 15, '2027-01-30'),
            ('Atorvastatina 20mg', 'Cardiovascular', 22.00, 18, 10, '2026-10-12'),
            ('Vitamina C 1000mg', 'Suplemento', 4.75, 150, 30, '2027-06-01'),
        ]
        c.executemany(
            "INSERT INTO medicamentos (nombre, categoria, precio, stock, stock_minimo, fecha_vencimiento) VALUES (?,?,?,?,?,?)",
            medicamentos
        )

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    print("Base de datos creada correctamente.")