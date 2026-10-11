from datetime import datetime
import os
import sqlite3
from flask import Flask, redirect, render_template, request

app = Flask(__name__)

DB_NAME = "tasks.db"


def init_db():
  conn = sqlite3.connect(DB_NAME)
  cursor = conn.cursor()
  # تحديث جدول المهام ليشمل البريد الإلكتروني للتنبيهات
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            due_date TEXT NOT NULL,
            priority TEXT NOT NULL,
            category TEXT NOT NULL,
            email TEXT NOT NULL
        )
    """)
  conn.commit()
  conn.close()


init_db()

TRANSLATIONS = {
    "ar": {
        "title": "منظم الحياة والمهام الذكي العالمي",
        "placeholder": "عنوان المهمة أو الهدف...",
        "priority_normal": "أولوية عادية",
        "priority_high": "أولوية عالية جداً",
        "cat_work": "عمل",
        "cat_personal": "شخصي",
        "cat_study": "دراسة",
        "cat_health": "صحة",
        "btn": "تثبيت وتفعيل التنبيه",
        "list_title": "المهام الموثقة مع التنبيهات:",
        "due": "الموعد:",
        "empty": "لا توجد مهام مسجلة حالياً.",
        "delete": "إنجاز وحذف",
        "analytics": "لوحة تحليلات وإحصائيات الإنتاجية والتنبيهات",
        "total_tasks": "إجمالي المهام:",
        "high_priority": "المهام ذات الأولوية العالية:",
        "dark_mode": "الوضع الداكن",
        "light_mode": "الوضع المضيء",
        "dir": "rtl",
    },
    "en": {
        "title": "Global Deterministic Life & Task Optimizer",
        "placeholder": "Task title or goal...",
        "priority_normal": "Normal Priority",
        "priority_high": "High Priority",
        "cat_work": "Work",
        "cat_personal": "Personal",
        "cat_study": "Study",
        "cat_health": "Health",
        "btn": "Confirm & Set Alert",
        "list_title": "Verified Tasks with Alerts:",
        "due": "Due Date:",
        "empty": "No tasks registered yet.",
        "delete": "Complete & Delete",
        "analytics": "Productivity & Alerts Dashboard",
        "total_tasks": "Total Tasks:",
        "high_priority": "High Priority Tasks:",
        "dark_mode": "Dark Mode",
        "light_mode": "Light Mode",
        "dir": "ltr",
    },
}


@app.route("/")
def home():
  user_lang = request.accept_languages.best_match(list(TRANSLATIONS.keys()))
  if not user_lang or user_lang not in TRANSLATIONS:
    user_lang = "en"

  t = TRANSLATIONS[user_lang]

  conn = sqlite3.connect(DB_NAME)
  cursor = conn.cursor()
  cursor.execute("SELECT * FROM tasks ORDER BY id DESC")
  tasks = cursor.fetchall()

  total_count = len(tasks)
  high_count = sum(
      1 for task in tasks if task[3] in ["High Priority", "أولوية عالية جداً"]
  )

  conn.close()

  return render_template(
      "index.html",
      t=t,
      lang=user_lang,
      tasks=tasks,
      total_count=total_count,
      high_count=high_count,
  )


@app.route("/add", methods=["POST"])
def add_task_web():
  title = request.form.get("title")
  due_date = request.form.get("due_date")
  priority = request.form.get("priority", "Normal")
  category = request.form.get("category", "General")
  email = request.form.get("email", "fouedkarkni9333@gmail.com")

  if title and due_date:
    try:
      datetime.strptime(due_date, "%Y-%m-%d")
      conn = sqlite3.connect(DB_NAME)
      cursor = conn.cursor()
      cursor.execute(
          "INSERT INTO tasks (title, due_date, priority, category, email)"
          " VALUES (?, ?, ?, ?, ?)",
          (title, due_date, priority, category, email),
      )
      conn.commit()
      conn.close()
    except ValueError:
      pass

  return redirect("/")


@app.route("/delete/<int:task_id>")
def delete_task(task_id):
  conn = sqlite3.connect(DB_NAME)
  cursor = conn.cursor()
  cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
  conn.commit()
  conn.close()
  return redirect("/")


if __name__ == "__main__":
  app.run(host="0.0.0.0", port=5000, debug=True)
