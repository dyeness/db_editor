from flask import Flask, render_template, request, redirect, url_for, send_file
import sqlite3, os, threading, webbrowser, shutil
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = './'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
DB_PATH = 'database.db'

# Получение списка таблиц
def get_tables():
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        return [row[0] for row in cur.fetchall()]

# Главная страница со списком таблиц
@app.route('/')
def index():
    tables = get_tables()
    return render_template('index.html', tables=tables, db_name=DB_PATH)

# Просмотр содержимого таблицы
@app.route('/table/<name>')
def view_table(name):
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute(f"PRAGMA table_info({name})")
        columns = [col[1] for col in cur.fetchall()]
        cur.execute(f"SELECT rowid, * FROM {name}")
        rows = cur.fetchall()
    return render_template('table.html', table=name, columns=columns, rows=rows)

# Добавление строки
@app.route('/add/<table>', methods=['POST'])
def add_row(table):
    values = tuple(request.form.get(col) for col in request.form)
    placeholders = ','.join('?' * len(values))
    columns = ','.join(request.form.keys())
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute(f"INSERT INTO {table} ({columns}) VALUES ({placeholders})", values)
    return redirect(url_for('view_table', name=table))

# Удаление строки
@app.route('/delete/<table>/<int:rowid>')
def delete_row(table, rowid):
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute(f"DELETE FROM {table} WHERE rowid = ?", (rowid,))
    return redirect(url_for('view_table', name=table))

# Обновление строки (редактирование ячеек)
@app.route('/update/<table>/<int:rowid>', methods=['POST'])
def update_row(table, rowid):
    columns = request.form.keys()
    values = [request.form[col] for col in columns]
    assignments = ", ".join(f"{col}=?" for col in columns)
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute(f"UPDATE {table} SET {assignments} WHERE rowid=?", (*values, rowid))
    return redirect(url_for('view_table', name=table))

# Выполнение пользовательского SQL-запроса
@app.route('/query', methods=['GET', 'POST'])
def custom_query():
    result = None
    error = None
    if request.method == 'POST':
        query = request.form['query']
        try:
            with sqlite3.connect(DB_PATH) as conn:
                cur = conn.cursor()
                cur.execute(query)
                if query.strip().upper().startswith("SELECT"):
                    result = cur.fetchall()
                else:
                    conn.commit()
        except Exception as e:
            error = str(e)
    return render_template('query_tool.html', result=result, error=error)

# Загрузка новой базы данных
@app.route('/load_db', methods=['POST'])
def load_db():
    global DB_PATH
    if 'file' not in request.files:
        return redirect(url_for('index'))
    file = request.files['file']
    if file.filename == '':
        return redirect(url_for('index'))
    if file and file.filename.endswith('.db'):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        DB_PATH = filename
    return redirect(url_for('index'))

# Сохранение базы данных под другим именем
@app.route('/save_db', methods=['POST'])
def save_db():
    path = request.form.get('path')
    if path:
        shutil.copy(DB_PATH, path)
    return redirect(url_for('index'))

# Автоматическое открытие браузера
def open_browser():
    webbrowser.open_new("http://127.0.0.1:5000")

if __name__ == '__main__':
    threading.Timer(1.25, open_browser).start()
    app.run(debug=True)
