# 🔥 SQLite DB Editor — Obsidian & Scarlet

[![MIT License](https://img.shields.io/badge/license-MIT-red.svg)](https://opensource.org/licenses/MIT)
[![Made with Flask](https://img.shields.io/badge/made%20with-Flask-black?logo=flask)](https://flask.palletsprojects.com/)
[![GitHub stars](https://img.shields.io/github/stars/dyeness/db_editor?style=social)](https://github.com/dyeness/db_editor/stargazers)
[![GitHub last commit](https://img.shields.io/github/last-commit/dyeness/db_editor?color=scarlet)](https://github.com/dyeness/db_editor/commits)

Интерактивный веб-интерфейс на Flask для редактирования SQLite-баз данных.  
Поддерживает загрузку, визуальное редактирование, выполнение SQL-запросов и автоматическое построение ER-диаграмм.

---

## 🚀 Возможности

- 📥 Загрузка `.db` файлов (перетаскиванием или кнопкой)
- 🧾 Просмотр и редактирование таблиц и данных
- ➕ Добавление и удаление строк
- 🧱 Создание новых таблиц
- 🧠 Выполнение SQL-запросов с терминалом вывода
- 📊 Автоматическая генерация ER-диаграммы (Mermaid.js)
- 💾 Скачивание базы обратно
- 🧠 Поддержка foreign keys в ER-схеме

---

## 📦 Установка

1. Установи зависимости:
```bash
pip install flask
````

2. Запусти приложение:

```bash
python app.py
```

3. Перейди в браузере:

```
http://127.0.0.1:5000/ | В app.py поставить свой ip
```

---
