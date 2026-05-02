from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import sqlite3
import os
from database import init_db

app = Flask(__name__, static_folder='static')
CORS(app)

init_db()

def get_db():
    conn = sqlite3.connect('farmacia.db')
    conn.row_factory = sqlite3.Row
    return conn

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
        (data['nombre'], data['categoria'], data['precio'], data['stock'], data.get('stock_minimo', 10), data.get('fecha_vencimiento', ''))
    )
    conn.commit()
    conn.close()
    return jsonify({'ok': True}), 201

@app.route('/api/medicamentos/<int:id>', methods=['PUT'])
def update_medicamento(id):
    data = request.json
    conn = get_db()
    conn.execute(
        'UPDATE medicamentos SET nombre=?, categoria=?, precio=?, stock=?, stock_minimo=?, fecha_vencimiento=? WHERE id=?',
        (data['nombre'], data['categoria'], data['precio'], data['stock'], data.get('stock_minimo', 10), data.get('fecha_vencimiento', ''), id)
    )
    conn.commit()
    conn.close()
    return jsonify({'ok': True})

@app.route('/api/medicamentos/<int:id>', methods=['DELETE'])
def delete_medicamento(id):
    conn = get_db()
    conn.execute('DELETE FROM medicamentos WHERE id=?', (id,))
    conn.commit()
    conn.close()
    return jsonify({'ok': True})

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
        return jsonify({'error': 'Medicamento no encontrado'}), 404
    if med['stock'] < data['cantidad']:
        return jsonify({'error': 'Stock insuficiente'}), 400
    total = med['precio'] * data['cantidad']
    conn.execute(
        'INSERT INTO ventas (medicamento_id, cantidad, precio_unitario, total) VALUES (?,?,?,?)',
        (data['medicamento_id'], data['cantidad'], med['precio'], total)
    )
    conn.execute('UPDATE medicamentos SET stock = stock - ? WHERE id=?', (data['cantidad'], data['medicamento_id']))
    conn.commit()
    conn.close()
    return jsonify({'ok': True, 'total': total}), 201

@app.route('/api/dashboard', methods=['GET'])
def get_dashboard():
    conn = get_db()
    total_medicamentos = conn.execute('SELECT COUNT(*) FROM medicamentos').fetchone()[0]
    stock_critico = conn.execute('SELECT COUNT(*) FROM medicamentos WHERE stock <= stock_minimo').fetchone()[0]
    vencimientos = conn.execute(
        "SELECT COUNT(*) FROM medicamentos WHERE fecha_vencimiento != '' AND fecha_vencimiento <= date('now','+30 days')"
    ).fetchone()[0]
    ingresos_hoy = conn.execute(
        "SELECT COALESCE(SUM(total),0) FROM ventas WHERE date(fecha)=date('now')"
    ).fetchone()[0]
    ingresos_mes = conn.execute(
        "SELECT COALESCE(SUM(total),0) FROM ventas WHERE strftime('%Y-%m', fecha)=strftime('%Y-%m','now')"
    ).fetchone()[0]
    total_ventas = conn.execute('SELECT COUNT(*) FROM ventas').fetchone()[0]
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
    conn.close()
    return jsonify({
        'kpis': {
            'total_medicamentos': total_medicamentos,
            'stock_critico': stock_critico,
            'vencimientos_proximos': vencimientos,
            'ingresos_hoy': round(ingresos_hoy, 2),
            'ingresos_mes': round(ingresos_mes, 2),
            'total_ventas': total_ventas,
        },
        'top_vendidos': [dict(r) for r in top_vendidos],
        'por_categoria': [dict(r) for r in por_categoria],
        'stock_bajo': [dict(r) for r in stock_bajo],
        'ventas_por_dia': [dict(r) for r in ventas_por_dia],
    })

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('static', path)

if __name__ == '__main__':
    app.run(debug=True, port=5000)