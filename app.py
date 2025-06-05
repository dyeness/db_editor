from flask import Flask, render_template, request, redirect, send_file, url_for, jsonify
import sqlite3
import os
from werkzeug.utils import secure_filename
from datetime import datetime

app = Flask(__name__)
UPLOAD_FOLDER = 'uploaded'
DB_PATH = os.path.join(UPLOAD_FOLDER, 'current.db')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ===== 📦 ЗАГРУЗКА БАЗЫ ДАННЫХ =====
@app.route('/load_db', methods=['POST'])
def load_db():
    file = request.files['file']
    if file.filename.endswith('.db'):
        path = os.path.join(UPLOAD_FOLDER, 'current.db')
        file.save(path)
    return redirect(url_for('main'))


# ===== 💾 СКАЧИВАНИЕ АКТУАЛЬНОЙ БАЗЫ =====
@app.route('/download_db')
def download_db():
    return send_file(DB_PATH, as_attachment=True, download_name='database.db')


# ===== 🏠 ГЛАВНАЯ СТРАНИЦА =====
@app.route('/', methods=['GET'])
def main():
    if not os.path.exists(DB_PATH):
        return render_template("main.html", tables=[], selected_table=None)

    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cur.fetchall()]

        selected_table = request.args.get('table')
        if selected_table:
            cur.execute(f"PRAGMA table_info({selected_table})")
            columns = [row[1] for row in cur.fetchall()]
            cur.execute(f"SELECT * FROM {selected_table}")
            rows = cur.fetchall()
            return render_template("main.html", tables=tables, selected_table=selected_table, columns=columns, rows=rows)

        return render_template("main.html", tables=tables, selected_table=None)


# ===== ➕ ДОБАВЛЕНИЕ ЗАПИСИ =====
@app.route('/add/<table>', methods=['POST'])
def add_entry(table):
    data = [request.form[col] for col in request.form]
    placeholders = ', '.join(['?'] * len(data))
    columns = ', '.join(request.form.keys())

    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(f"INSERT INTO {table} ({columns}) VALUES ({placeholders})", data)
        conn.commit()
    return redirect(f"/?table={table}")


# ===== 💾 ОБНОВЛЕНИЕ ЗАПИСИ =====
@app.route('/update/<table>/<int:row_id>', methods=['POST'])
def update_entry(table, row_id):
    updates = [f"{col} = ?" for col in request.form]
    values = list(request.form.values())

    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(f"UPDATE {table} SET {', '.join(updates)} WHERE id = ?", values + [row_id])
        conn.commit()
    return redirect(f"/?table={table}")


# ===== 🗑 УДАЛЕНИЕ ЗАПИСИ =====
@app.route('/delete/<table>/<int:row_id>')
def delete_entry(table, row_id):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(f"DELETE FROM {table} WHERE id = ?", (row_id,))
        conn.commit()
    return redirect(f"/?table={table}")


# ===== 🧱 СОЗДАНИЕ ТАБЛИЦЫ =====
@app.route('/create_table', methods=['POST'])
def create_table():
    name = request.form['table_name']
    columns = request.form['columns']
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(f"CREATE TABLE IF NOT EXISTS {name} ({columns})")
        conn.commit()
    return redirect(f"/?table={name}")


# ===== 🧠 ВЫПОЛНЕНИЕ SQL ЗАПРОСА =====
@app.route('/query', methods=['POST'])
def run_query():
    sql = request.form['query']
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute(sql)
            if sql.strip().lower().startswith("select"):
                rows = cur.fetchall()
                result = [dict(row) for row in rows]
                return jsonify(result=result)
            else:
                conn.commit()
                return jsonify(result=[])
    except Exception as e:
        return jsonify(error=str(e))


# ===== 📊 ER-ДИАГРАММА =====
@app.route('/er')
def er_page():
    diagram = generate_er_diagram()
    return render_template("er.html", diagram=diagram)


def generate_er_diagram():
    if not os.path.exists(DB_PATH):
        return "erDiagram\n"

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()

        diagram = "erDiagram\n"

        for (table,) in tables:
            cursor.execute(f"PRAGMA table_info({table})")
            columns = cursor.fetchall()
            if not columns:
                continue

            diagram += f"    {table} {{\n"
            for col in columns:
                name = col[1]
                type_ = col[2].split('(')[0].upper()  # убираем (255) и т.д.
                if name and type_:
                    diagram += f"        {type_} {name}\n"
            diagram += f"    }}\n"

        # Добавляем связи по foreign keys
        for (table,) in tables:
            cursor.execute(f"PRAGMA foreign_key_list({table})")
            fks = cursor.fetchall()
            for fk in fks:
                ref_table = fk[2]
                diagram += f"    {table} ||--o{{ {ref_table} : FK\n"

        return diagram



# ===== 🚀 ЗАПУСК СЕРВЕРА =====
if __name__ == '__main__':
    app.run(host="26.201.251.196", port=5000, debug=True)
