from flask import Flask, render_template, request, redirect, url_for, send_file, jsonify
import sqlite3, os, threading, webbrowser
from werkzeug.utils import secure_filename
import shutil

app = Flask(__name__)
UPLOAD_FOLDER = './'
DB_PATH = 'database.db'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def get_tables():
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        return [row[0] for row in cur.fetchall()]

def get_table_data(table):
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute(f"PRAGMA table_info({table})")
        columns = [col[1] for col in cur.fetchall()]
        cur.execute(f"SELECT rowid, * FROM {table}")
        rows = cur.fetchall()
    return columns, rows

@app.route('/')
def index():
    tables = get_tables()
    selected_table = request.args.get('table')
    columns, rows = [], []
    if selected_table:
        columns, rows = get_table_data(selected_table)
    return render_template('main.html', tables=tables, selected_table=selected_table, columns=columns, rows=rows)

@app.route('/add/<table>', methods=['POST'])
def add_row(table):
    values = tuple(request.form.get(col) for col in request.form)
    columns = ','.join(request.form.keys())
    placeholders = ','.join('?' * len(values))
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute(f"INSERT INTO {table} ({columns}) VALUES ({placeholders})", values)
    return redirect(url_for('index', table=table))

@app.route('/update/<table>/<int:rowid>', methods=['POST'])
def update_row(table, rowid):
    columns = request.form.keys()
    values = [request.form[col] for col in columns]
    assignments = ", ".join(f"{col}=?" for col in columns)
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute(f"UPDATE {table} SET {assignments} WHERE rowid=?", (*values, rowid))
    return redirect(url_for('index', table=table))

@app.route('/delete/<table>/<int:rowid>')
def delete_row(table, rowid):
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute(f"DELETE FROM {table} WHERE rowid = ?", (rowid,))
    return redirect(url_for('index', table=table))

@app.route('/query', methods=['POST'])
def custom_query():
    query = request.form['query']
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cur = conn.cursor()
            cur.execute(query)
            if query.strip().upper().startswith("SELECT"):
                result = cur.fetchall()
                return jsonify({'result': result})
            else:
                conn.commit()
                return jsonify({'result': []})
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/load_db', methods=['POST'])
def load_db():
    global DB_PATH
    file = request.files['file']
    if file and file.filename.endswith('.db'):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        DB_PATH = filepath
    return redirect(url_for('index'))

@app.route('/create_table', methods=['POST'])
def create_table():
    table_name = request.form.get("table_name")
    column_defs = request.form.get("columns")
    if table_name and column_defs:
        try:
            with sqlite3.connect(DB_PATH) as conn:
                cur = conn.cursor()
                cur.execute(f"CREATE TABLE {table_name} ({column_defs})")
                conn.commit()
        except Exception as e:
            return f"<p style='color:red;'>Ошибка: {e}</p><a href='/'>Назад</a>"
    return redirect(url_for('index'))

@app.route('/download_db')
def download_db():
    return send_file(DB_PATH, as_attachment=True, download_name='database_copy.db')

def open_browser():
    webbrowser.open_new("http://127.0.0.1:5000")

if __name__ == '__main__':
    threading.Timer(1.25, open_browser).start()
    app.run(debug=True)
