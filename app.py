from datetime import datetime
import sqlite3
from flask import Flask, redirect, render_template_string, request

app = Flask(__name__)

DB_NAME = "tasks.db"


def init_db():
  conn = sqlite3.connect(DB_NAME)
  cursor = conn.cursor()
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            due_date TEXT NOT NULL,
            priority TEXT NOT NULL
        )
    """)
  conn.commit()
  conn.close()


init_db()

# قاموس الترجمات الشامل للغات العالم الرئيسية (يمكن إضافة أي لغة بسهولة)
TRANSLATIONS = {
    "ar": {
        "title": "منظم الحياة والمهام الذكي العالمي",
        "placeholder": "عنوان المهمة أو الهدف...",
        "priority_normal": "أولوية عادية",
        "priority_high": "أولوية عالية جداً",
        "btn": "تثبيت وإضافة المهمة",
        "list_title": "المهام الموثقة:",
        "due": "الموعد:",
        "empty": "لا توجد مهام مسجلة حالياً.",
        "dir": "rtl",
    },
    "zh": {
        "title": "全球智能生活与任务优化器",
        "placeholder": "任务标题或目标...",
        "priority_normal": "普通优先级",
        "priority_high": "高优先级",
        "btn": "确认并添加任务",
        "list_title": "已验证的任务：",
        "due": "截止日期：",
        "empty": "暂无记录的任务。",
        "dir": "ltr",
    },
    "de": {
        "title": "Globaler Intelligenz- und Aufgaben-Optimizer",
        "placeholder": "Aufgabentitel oder Ziel...",
        "priority_normal": "Normale Priorität",
        "priority_high": "Hohe Priorität",
        "btn": "Aufgabe hinzufügen",
        "list_title": "Verifizierte Aufgaben:",
        "due": "Fälligkeitsdatum:",
        "empty": "Noch keine Aufgaben registriert.",
        "dir": "ltr",
    },
    "fr": {
        "title": "Optimiseur Intelligent de Vie et de Tâches",
        "placeholder": "Titre de la tâche ou objectif...",
        "priority_normal": "Priorité normale",
        "priority_high": "Haute priorité",
        "btn": "Confirmer et ajouter",
        "list_title": "Tâches vérifiées :",
        "due": "Date d'échéance :",
        "empty": "Aucune tâche enregistrée pour le moment.",
        "dir": "ltr",
    },
    "es": {
        "title": "Optimizador Global de Vida y Tareas",
        "placeholder": "Título de la tarea u objetivo...",
        "priority_normal": "Prioridad normal",
        "priority_high": "Alta prioridad",
        "btn": "Confirmar y añadir tarea",
        "list_title": "Tareas verificadas:",
        "due": "Fecha límite:",
        "empty": "No hay tareas registradas aún.",
        "dir": "ltr",
    },
    "en": {
        "title": "Global Deterministic Life & Task Optimizer",
        "placeholder": "Task title or goal...",
        "priority_normal": "Normal Priority",
        "priority_high": "High Priority",
        "btn": "Confirm & Add Task",
        "list_title": "Verified Tasks:",
        "due": "Due Date:",
        "empty": "No tasks registered yet.",
        "dir": "ltr",
    },
}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="{{ lang }}" dir="{{ t.dir }}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ t.title }}</title>
    <style>
        body { font-family: Tahoma, sans-serif; background-color: #f4f6f9; margin: 0; padding: 20px; direction: {{ t.dir }}; }
        .container { max-width: 600px; margin: auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }
        h1 { color: #2c3e50; text-align: center; font-size: 22px; }
        form { display: flex; flex-direction: column; gap: 10px; margin-bottom: 20px; }
        input, select, button { padding: 10px; font-size: 16px; border: 1px solid #ccc; border-radius: 5px; }
        button { background-color: #27ae60; color: white; border: none; cursor: pointer; font-weight: bold; }
        button:hover { background-color: #219653; }
        ul { list-style: none; padding: 0; }
        li { background: #ecf0f1; margin-bottom: 8px; padding: 10px; border-radius: 5px; display: flex; justify-content: space-between; align-items: center; }
        .task-info { display: flex; flex-direction: column; gap: 3px; }
        .badge { background: #e74c3c; color: white; padding: 2px 6px; border-radius: 3px; font-size: 12px; width: fit-content; }
    </style>
</head>
<body>
    <div class="container">
        <h1>{{ t.title }}</h1>
        <form action="/add" method="POST">
            <input type="text" name="title" placeholder="{{ t.placeholder }}" required>
            <input type="date" name="due_date" required>
            <select name="priority">
                <option value="{{ t.priority_normal }}">{{ t.priority_normal }}</option>
                <option value="{{ t.priority_high }}">{{ t.priority_high }}</option>
            </select>
            <button type="submit">{{ t.btn }}</button>
        </form>
        
        <h2>{{ t.list_title }}</h2>
        <ul>
            {% for task in tasks %}
            <li>
                <div class="task-info">
                    <strong>{{ task[1] }}</strong>
                    <small>{{ t.due }} {{ task[2] }}</small>
                </div>
                <span class="badge">{{ task[3] }}</span>
            </li>
            {% else %}
            <p style="text-align: center; color: #7f8c8d;">{{ t.empty }}</p>
            {% endfor %}
        </ul>
    </div>
</body>
</html>
"""


@app.route("/")
def home():
  # الكشف التلقائي عن لغة متصفح المستخدم في أي مكان في العالم
  user_lang = request.accept_languages.best_match(list(TRANSLATIONS.keys()))
  if not user_lang or user_lang not in TRANSLATIONS:
    user_lang = "en"  # اللغة الافتراضية إذا لم يتم التعرف على اللغة

  t = TRANSLATIONS[user_lang]

  conn = sqlite3.connect(DB_NAME)
  cursor = conn.cursor()
  cursor.execute("SELECT * FROM tasks ORDER BY id DESC")
  tasks = cursor.fetchall()
  conn.close()

  return render_template_string(HTML_TEMPLATE, t=t, lang=user_lang, tasks=tasks)


@app.route("/add", methods=["POST"])
def add_task_web():
  title = request.form.get("title")
  due_date = request.form.get("due_date")
  priority = request.form.get("priority", "Normal")

  if title and due_date:
    try:
      datetime.strptime(due_date, "%Y-%m-%d")
      conn = sqlite3.connect(DB_NAME)
      cursor = conn.cursor()
      cursor.execute(
          "INSERT INTO tasks (title, due_date, priority) VALUES (?, ?, ?)",
          (title, due_date, priority),
      )
      conn.commit()
      conn.close()
    except ValueError:
      pass

  return redirect("/")


if __name__ == "__main__":
  app.run(host="0.0.0.0", port5000, debug=True)
