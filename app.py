import os
import html
import psycopg2
from flask import Flask, request, redirect, url_for

app = Flask(__name__)

def get_db_connection():
    return psycopg2.connect(
        host=os.environ.get("DB_HOST", "esteban-db"),
        database=os.environ.get("DB_NAME", "yavirac_db"),
        user=os.environ.get("DB_USER", "esteban"),
        password=os.environ.get("DB_PASSWORD", "yavirac_pass")
    )

def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS mensajes (
            id SERIAL PRIMARY KEY,
            autor VARCHAR(100) NOT NULL,
            contenido TEXT NOT NULL,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    cur.close()
    conn.close()

@app.route("/", methods=["GET", "POST"])
def home():
    error_msg = None
    db_version = ""
    registros = []

    try:
        init_db()
        conn = get_db_connection()
        cur = conn.cursor()

        if request.method == "POST":
            autor = request.form.get("autor", "").strip()
            contenido = request.form.get("contenido", "").strip()
            if autor and contenido:
                cur.execute(
                    "INSERT INTO mensajes (autor, contenido) VALUES (%s, %s);",
                    (autor, contenido)
                )
                conn.commit()
                cur.close()
                conn.close()
                return redirect(url_for("home"))

        cur.execute("SELECT version();")
        db_version = cur.fetchone()[0].split(",")[0]

        cur.execute("SELECT id, autor, contenido, TO_CHAR(fecha, 'DD/MM/YYYY HH24:MI:SS') FROM mensajes ORDER BY id DESC;")
        registros = cur.fetchall()
        cur.close()
        conn.close()
    except Exception as e:
        error_msg = str(e)

    filas_html = ""
    if registros:
        for r in registros:
            filas_html += f"""
            <tr>
                <td>#{r[0]}</td>
                <td><strong>{html.escape(r[1])}</strong></td>
                <td>{html.escape(r[2])}</td>
                <td class="fecha">{r[3]}</td>
                <td>
                    <form method="POST" action="/eliminar/{r[0]}" style="margin:0;">
                        <button type="submit" class="btn-del">🗑️</button>
                    </form>
                </td>
            </tr>
            """
    else:
        filas_html = '<tr><td colspan="5" style="text-align:center; color:#777;">Aún no hay registros en PostgreSQL. ¡Escribe el primero arriba!</td></tr>'

    estado_html = (
        f'<div class="status-ok">✅ Conectado a <strong>esteban-db</strong> ({db_version})</div>'
        if not error_msg
        else f'<div class="status-err">❌ Error BD: {html.escape(error_msg)}</div>'
    )

    return f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>App + PostgreSQL - Bryan Esteban Polo Amaya</title>
        <style>
            * {{ box-sizing: border-box; font-family: 'Segoe UI', sans-serif; }}
            body {{
                background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
                min-height: 100vh;
                margin: 0;
                padding: 30px 15px;
                display: flex;
                justify-content: center;
                align-items: flex-start;
            }}
            .container {{
                background: #ffffff;
                border-radius: 20px;
                padding: 35px;
                max-width: 780px;
                width: 100%;
                box-shadow: 0 20px 50px rgba(0,0,0,0.4);
            }}
            .header {{ text-align: center; margin-bottom: 25px; }}
            .yavirac {{
                display: inline-block;
                background: linear-gradient(90deg, #ff512f, #dd2476);
                color: #fff;
                padding: 8px 20px;
                border-radius: 50px;
                font-weight: bold;
                font-size: 16px;
                margin: 10px 0;
            }}
            .status-ok {{
                background: #e6fffa;
                color: #0b6e4f;
                border: 1px solid #38ef7d;
                padding: 10px 15px;
                border-radius: 10px;
                font-size: 14px;
                margin-top: 10px;
            }}
            .status-err {{
                background: #ffe6e6;
                color: #a80000;
                padding: 10px 15px;
                border-radius: 10px;
                font-size: 14px;
                margin-top: 10px;
            }}
            .form-box {{
                background: #f4f7f9;
                padding: 20px;
                border-radius: 14px;
                margin-bottom: 25px;
            }}
            .form-row {{
                display: flex;
                gap: 12px;
                flex-wrap: wrap;
            }}
            input {{
                padding: 12px 14px;
                border: 1px solid #ccd6dd;
                border-radius: 10px;
                font-size: 15px;
                flex: 1;
                min-width: 180px;
            }}
            .btn-save {{
                background: linear-gradient(90deg, #00b4db, #0083b0);
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 10px;
                font-size: 15px;
                font-weight: bold;
                cursor: pointer;
            }}
            .btn-save:hover {{ opacity: 0.92; }}
            .btn-del {{
                background: #ff4b2b;
                color: white;
                border: none;
                padding: 6px 10px;
                border-radius: 6px;
                cursor: pointer;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 10px;
            }}
            th {{
                background: #1a2a3a;
                color: #ffffff;
                text-align: left;
                padding: 12px;
                font-size: 14px;
            }}
            td {{
                padding: 12px;
                border-bottom: 1px solid #eee;
                font-size: 14px;
            }}
            .fecha {{ color: #666; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1 style="margin:0; color:#1a2a3a;">Registro en Base de Datos Docker 🐳</h1>
                <div class="yavirac">🎓 Yo estudio en Yavirac</div>
                <p style="margin:5px 0; color:#444;">Estudiante: <strong>Bryan Esteban Polo Amaya</strong> • Servidor: <strong>161.97.140.245</strong></p>
                {estado_html}
            </div>

            <div class="form-box">
                <form method="POST" action="/">
                    <div class="form-row">
                        <input type="text" name="autor" placeholder="Tu nombre (ej. Esteban)" required>
                        <input type="text" name="contenido" placeholder="Escribe un mensaje para guardar en PostgreSQL..." required style="flex:2;">
                        <button type="submit" class="btn-save">💾 Guardar en BD</button>
                    </div>
                </form>
            </div>

            <h3 style="color:#1a2a3a; margin-bottom:8px;">📋 Datos guardados en el contenedor PostgreSQL (esteban-db):</h3>
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Autor</th>
                        <th>Mensaje</th>
                        <th>Fecha</th>
                        <th>Acción</th>
                    </tr>
                </thead>
                <tbody>
                    {filas_html}
                </tbody>
            </table>
        </div>
    </body>
    </html>
    """

@app.route("/eliminar/<int:msg_id>", methods=["POST"])
def eliminar(msg_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM mensajes WHERE id = %s;", (msg_id,))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
