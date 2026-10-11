from datetime import datetime
import sqlite3
from flask import Flask, jsonify, redirect, render_template_string, request

app = Flask(__name__)

DB_NAME = "tasks.db"


# دته لتهيئة قاعدة البيانات وإنشاء الجدول إذا لم يكن موجوداً
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


# تشغيل تهيئة قاعدة البيانات عند بدء التشغيل
init_db()

# تصميم واجهة المستخدم الأنيقة
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Deterministic Life Optimizer</title>
    <style>
        body { font-family: Tahoma, sans-serif; background-color: #f4f6f9; margin: 0; padding: 20px; direction: rtl; }
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
        <h1>منظم الحياة والمهام الصارم 100%</h1>
        <form action="/add" method="POST">
            <input type="text" name="title" placeholder="عنوان المهمة أو الهدف..." required>
            <input type="date" name="due_date" required>
            <select name="priority">
                <option value="عادية">أولوية عادية</option>
                <option value="عالية">أولوية عالية جداً</option>
            </select>
            <button type="submit">تثبيت وإضافة المهمة</button>
        </form>
        
        <h2>المهام الموثقة بقاعدة البيانات:</h2>
        <ul>
            {% for task in tasks %}
            <li>
                <div class="task-info">
                    <strong>{{ task[1] }}</strong>
                    <small>الموعد: {{ task[2] }}</small>
                </div>
                <span class="badge">{{ task[3] }}</span>
            </li>
            {% else %}
            <p style="text-align: center; color: #7f8c8d;">لا توجد مهام مسجلة حالياً.</p>
            {% endfor %}
        </ul>
    </div>
</body>
</html>
"""


@app.route("/")
def home():
  conn = sqlite3.connect(DB_NAME)
  cursor = conn.cursor()
  cursor.execute("SELECT * FROM tasks ORDER BY id DESC")
  tasks = cursor.fetchall()
  conn.close()
  return render_template_string(HTML_TEMPLATE, tasks=tasks)


# محرك إضافة المهام بدقة وحفظها في SQLite
@app.route("/add", methods=["POST"])
def add_task_web():
  title = request.form.get("title")
  due_date = request.form.get("due_date")
  priority = request.form.get("priority", "عادية")

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
  app.run(host="0.0.0.0", port=5000, debug=True)
