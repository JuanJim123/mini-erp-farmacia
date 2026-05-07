from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import sqlite3
from database import init_db

app = Flask(__name__, static_folder='static')
CORS(app)
init_db()

def get_db():
    conn = sqlite3.connect('farmacia.db')
    conn.row_factory = sqlite3.Row
    return conn

# ── MEDICAMENTOS ──────────────────────────────

@app.route('/api/medicamentos', methods=['GET'])
def get_medicamentos():
    conn = get_db()
    rows = conn.execute('SELECT * FROM medicamentos ORDER BY nombre').fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@app.route('/api/medicamentos', methods=['POST'])
def add_medicamento():
    data = request.json
    conn = get_db()
    conn.execute(
        'INSERT INTO medicamentos (nombre, categoria, precio, stock, stock_minimo, fecha_vencimiento) VALUES (?,?,?,?,?,?)',
        (data['nombre'], data['categoria'], data['precio'], data['stock'],
         data.get('stock_minimo', 10), data.get('fecha_vencimiento', ''))
    )
    conn.commit(); conn.close()
    return jsonify({'ok': True}), 201

@app.route('/api/medicamentos/<int:id>', methods=['PUT'])
def update_medicamento(id):
    data = request.json
    conn = get_db()
    conn.execute(
        'UPDATE medicamentos SET nombre=?, categoria=?, precio=?, stock=?, stock_minimo=?, fecha_vencimiento=? WHERE id=?',
        (data['nombre'], data['categoria'], data['precio'], data['stock'],
         data.get('stock_minimo', 10), data.get('fecha_vencimiento', ''), id)
    )
    conn.commit(); conn.close()
    return jsonify({'ok': True})

@app.route('/api/medicamentos/<int:id>', methods=['DELETE'])
def delete_medicamento(id):
    conn = get_db()
    conn.execute('DELETE FROM medicamentos WHERE id=?', (id,))
    conn.commit(); conn.close()
    return jsonify({'ok': True})

# ── VENTAS ────────────────────────────────────

@app.route('/api/ventas', methods=['GET'])
def get_ventas():
    conn = get_db()
    rows = conn.execute('''
        SELECT v.*, m.nombre as medicamento_nombre
        FROM ventas v JOIN medicamentos m ON v.medicamento_id = m.id
        ORDER BY v.fecha DESC LIMIT 100
    ''').fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@app.route('/api/ventas', methods=['POST'])
def add_venta():
    data = request.json
    conn = get_db()
    med = conn.execute('SELECT * FROM medicamentos WHERE id=?', (data['medicamento_id'],)).fetchone()
    if not med:
        conn.close(); return jsonify({'error': 'Medicamento no encontrado'}), 404
    if med['stock'] < data['cantidad']:
        conn.close(); return jsonify({'error': 'Stock insuficiente'}), 400
    total = med['precio'] * data['cantidad']
    conn.execute(
        'INSERT INTO ventas (medicamento_id, cantidad, precio_unitario, total) VALUES (?,?,?,?)',
        (data['medicamento_id'], data['cantidad'], med['precio'], total)
    )
    conn.execute('UPDATE medicamentos SET stock = stock - ? WHERE id=?', (data['cantidad'], data['medicamento_id']))
    conn.commit(); conn.close()
    return jsonify({'ok': True, 'total': total}), 201

# ── PROVEEDORES ───────────────────────────────

@app.route('/api/proveedores', methods=['GET'])
def get_proveedores():
    conn = get_db()
    rows = conn.execute('SELECT * FROM proveedores ORDER BY nombre').fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@app.route('/api/proveedores', methods=['POST'])
def add_proveedor():
    data = request.json
    conn = get_db()
    conn.execute(
        'INSERT INTO proveedores (nombre, contacto, telefono, email, categoria) VALUES (?,?,?,?,?)',
        (data['nombre'], data.get('contacto',''), data.get('telefono',''),
         data.get('email',''), data.get('categoria','Otro'))
    )
    conn.commit(); conn.close()
    return jsonify({'ok': True}), 201

@app.route('/api/proveedores/<int:id>', methods=['PUT'])
def update_proveedor(id):
    data = request.json
    conn = get_db()
    conn.execute(
        'UPDATE proveedores SET nombre=?, contacto=?, telefono=?, email=?, categoria=? WHERE id=?',
        (data['nombre'], data.get('contacto',''), data.get('telefono',''),
         data.get('email',''), data.get('categoria','Otro'), id)
    )
    conn.commit(); conn.close()
    return jsonify({'ok': True})

@app.route('/api/proveedores/<int:id>', methods=['DELETE'])
def delete_proveedor(id):
    conn = get_db()
    conn.execute('DELETE FROM proveedores WHERE id=?', (id,))
    conn.commit(); conn.close()
    return jsonify({'ok': True})

# ── ÓRDENES DE COMPRA ─────────────────────────

@app.route('/api/ordenes', methods=['GET'])
def get_ordenes():
    conn = get_db()
    rows = conn.execute('''
        SELECT o.*, p.nombre as proveedor_nombre, m.nombre as medicamento_nombre
        FROM ordenes_compra o
        JOIN proveedores p ON o.proveedor_id = p.id
        JOIN medicamentos m ON o.medicamento_id = m.id
        ORDER BY o.fecha DESC
    ''').fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@app.route('/api/ordenes', methods=['POST'])
def add_orden():
    data = request.json
    costo_total = data['cantidad'] * data['precio_unitario']
    conn = get_db()
    conn.execute(
        'INSERT INTO ordenes_compra (proveedor_id, medicamento_id, cantidad, precio_unitario, costo_total, estado) VALUES (?,?,?,?,?,?)',
        (data['proveedor_id'], data['medicamento_id'], data['cantidad'],
         data['precio_unitario'], costo_total, 'pendiente')
    )
    conn.commit(); conn.close()
    return jsonify({'ok': True}), 201

@app.route('/api/ordenes/<int:id>', methods=['PUT'])
def update_orden(id):
    data = request.json
    nuevo_estado = data.get('estado')
    conn = get_db()
    orden = conn.execute('SELECT * FROM ordenes_compra WHERE id=?', (id,)).fetchone()
    if not orden:
        conn.close(); return jsonify({'error': 'Orden no encontrada'}), 404
    if nuevo_estado == 'recibida' and orden['estado'] != 'recibida':
        conn.execute('UPDATE medicamentos SET stock = stock + ? WHERE id=?',
                     (orden['cantidad'], orden['medicamento_id']))
    conn.execute('UPDATE ordenes_compra SET estado=? WHERE id=?', (nuevo_estado, id))
    conn.commit(); conn.close()
    return jsonify({'ok': True})

# ── DASHBOARD ─────────────────────────────────

@app.route('/api/dashboard', methods=['GET'])
def get_dashboard():
    conn = get_db()

    total_medicamentos = conn.execute('SELECT COUNT(*) FROM medicamentos').fetchone()[0]
    stock_critico      = conn.execute('SELECT COUNT(*) FROM medicamentos WHERE stock <= stock_minimo').fetchone()[0]
    total_ventas       = conn.execute('SELECT COUNT(*) FROM ventas').fetchone()[0]
    ingresos_hoy       = conn.execute("SELECT COALESCE(SUM(total),0) FROM ventas WHERE date(fecha)=date('now')").fetchone()[0]
    ingresos_mes       = conn.execute("SELECT COALESCE(SUM(total),0) FROM ventas WHERE strftime('%Y-%m',fecha)=strftime('%Y-%m','now')").fetchone()[0]

    # Vencimientos: próximos 30 días (que aún no han vencido)
    vencimientos_proximos = conn.execute(
        "SELECT COUNT(*) FROM medicamentos "
        "WHERE fecha_vencimiento != '' "
        "AND fecha_vencimiento >= date('now') "
        "AND fecha_vencimiento <= date('now','+30 days')"
    ).fetchone()[0]

    # Ya vencidos (fecha pasada)
    total_vencidos = conn.execute(
        "SELECT COUNT(*) FROM medicamentos "
        "WHERE fecha_vencimiento != '' AND fecha_vencimiento < date('now')"
    ).fetchone()[0]

    top_vendidos = conn.execute('''
        SELECT m.nombre, SUM(v.cantidad) as unidades, SUM(v.total) as ingresos
        FROM ventas v JOIN medicamentos m ON v.medicamento_id = m.id
        GROUP BY v.medicamento_id ORDER BY unidades DESC LIMIT 5
    ''').fetchall()

    por_categoria = conn.execute('''
        SELECT categoria, SUM(stock) as stock_total, COUNT(*) as productos
        FROM medicamentos GROUP BY categoria ORDER BY stock_total DESC
    ''').fetchall()

    stock_bajo = conn.execute('''
        SELECT nombre, stock, stock_minimo FROM medicamentos
        WHERE stock <= stock_minimo ORDER BY stock ASC LIMIT 8
    ''').fetchall()

    ventas_por_dia = conn.execute('''
        SELECT date(fecha) as dia, COALESCE(SUM(total),0) as total
        FROM ventas GROUP BY dia ORDER BY dia DESC LIMIT 7
    ''').fetchall()

    # Vencidos + próximos a vencer juntos, ordenados por fecha (primero los más viejos/urgentes)
    vencimientos_detalle = conn.execute(
        "SELECT nombre, stock, fecha_vencimiento, "
        "CASE WHEN fecha_vencimiento < date('now') THEN 'vencido' ELSE 'proximo' END as estado_vencimiento "
        "FROM medicamentos "
        "WHERE fecha_vencimiento != '' AND fecha_vencimiento <= date('now','+30 days') "
        "ORDER BY fecha_vencimiento ASC LIMIT 15"
    ).fetchall()

    conn.close()

    return jsonify({
        'kpis': {
            'total_medicamentos':    total_medicamentos,
            'stock_critico':         stock_critico,
            'vencimientos_proximos': vencimientos_proximos,
            'total_vencidos':        total_vencidos,
            'ingresos_hoy':          round(ingresos_hoy, 2),
            'ingresos_mes':          round(ingresos_mes, 2),
            'total_ventas':          total_ventas,
        },
        'top_vendidos':          [dict(r) for r in top_vendidos],
        'por_categoria':         [dict(r) for r in por_categoria],
        'stock_bajo':            [dict(r) for r in stock_bajo],
        'ventas_por_dia':        [dict(r) for r in ventas_por_dia],
        'vencimientos_detalle':  [dict(r) for r in vencimientos_detalle],
    })

# ── STATIC ────────────────────────────────────

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('static', path)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
