"""
Script simple para servir datos de la base de datos en una página web.
"""

from flask import Flask, jsonify, render_string
import psycopg2
from psycopg2.extras import RealDictCursor
import json

app = Flask(__name__)

def get_db_connection():
    conn = psycopg2.connect(
        dbname='skyanalytics',
        user='admin',
        password='secretpassword',
        host='localhost',
        port='5432'
    )
    return conn

@app.route('/')
def index():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    # Obtener estadísticas
    stats = {}
    
    cur.execute("SELECT COUNT(*) as count FROM users")
    stats['usuarios'] = cur.fetchone()['count']
    
    cur.execute("SELECT COUNT(*) as count FROM pasajeros")
    stats['pasajeros'] = cur.fetchone()['count']
    
    cur.execute("SELECT COUNT(*) as count FROM transacciones")
    stats['transacciones'] = cur.fetchone()['count']
    
    cur.execute("SELECT COUNT(*) as count FROM airports")
    stats['aeropuertos'] = cur.fetchone()['count']
    
    cur.execute("SELECT COUNT(*) as count FROM millas_acumuladas")
    stats['millas_acumuladas'] = cur.fetchone()['count']
    
    # Obtener usuarios
    cur.execute("SELECT id, username, email, is_active FROM users LIMIT 10")
    usuarios = cur.fetchall()
    
    cur.close()
    conn.close()
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>SkyAnalytics - Base de Datos</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
            .container {{ max-width: 1000px; margin: 0 auto; }}
            h1 {{ color: #333; }}
            .stats {{ display: grid; grid-template-columns: repeat(5, 1fr); gap: 10px; margin: 20px 0; }}
            .stat-card {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); text-align: center; }}
            .stat-number {{ font-size: 32px; font-weight: bold; color: #007bff; }}
            .stat-label {{ color: #666; margin-top: 10px; }}
            table {{ width: 100%; border-collapse: collapse; background: white; margin: 20px 0; }}
            th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
            th {{ background: #007bff; color: white; }}
            tr:hover {{ background: #f9f9f9; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📊 SkyAnalytics - Datos de la Base de Datos</h1>
            
            <div class="stats">
                <div class="stat-card">
                    <div class="stat-number">{stats['usuarios']}</div>
                    <div class="stat-label">Usuarios</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{stats['pasajeros']}</div>
                    <div class="stat-label">Pasajeros</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{stats['transacciones']}</div>
                    <div class="stat-label">Transacciones</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{stats['aeropuertos']}</div>
                    <div class="stat-label">Aeropuertos</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{stats['millas_acumuladas']}</div>
                    <div class="stat-label">Millas Acumuladas</div>
                </div>
            </div>
            
            <h2>Usuarios Registrados</h2>
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Usuario</th>
                        <th>Email</th>
                        <th>Activo</th>
                    </tr>
                </thead>
                <tbody>
    """
    
    for usuario in usuarios:
        activo = "✅ Sí" if usuario['is_active'] else "❌ No"
        html += f"""
                    <tr>
                        <td>{usuario['id']}</td>
                        <td>{usuario['username']}</td>
                        <td>{usuario['email']}</td>
                        <td>{activo}</td>
                    </tr>
        """
    
    html += """
                </tbody>
            </table>
        </div>
    </body>
    </html>
    """
    
    return html

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5555, debug=False)
