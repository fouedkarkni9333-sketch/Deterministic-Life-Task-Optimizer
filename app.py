from datetime import datetime
import os
import smtplib
import sqlite3
from email.mime.text import MIMEText
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, flash, redirect, render_template, request, url_for

app = Flask(__name__)
app.secret_key = "super_secret_key_for_flash_messages"
DB_NAME = "tasks.db"


def get_db_connection():
  conn = sqlite3.connect(DB_NAME)
  conn.row_factory = sqlite3.Row
  return conn


def init_db():
  with get_db_connection() as conn:
    conn.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                due_date TEXT NOT NULL,
                priority TEXT NOT NULL,
                category TEXT NOT NULL,
                email TEXT NOT NULL,
                notified INTEGER DEFAULT 0
            )
        """)


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


# --- محرك التنبيهات البريدية الدوري ---
def check_and_send_alerts():
  today_str = datetime.now().strftime("%Y-%m-%d")
  with get_db_connection() as conn:
    # جلب المهام المستحقة اليوم والتي لم يُرسل لها تنبيه بعد
    tasks = conn.execute(
        "SELECT * FROM tasks WHERE due_date <= ? AND notified = 0", (today_str,)
    ).fetchall()

    for task in tasks:
      # هنا يمكنك ضبط إعدادات SMTP الخاصة بك للإرسال الحقيقي
      print(
          f"[ALERT] إرسال تنبيه للمهمة '{task['title']}' إلى البريد:"
          f" {task['email']}"
      )

      # تحديث حالة التنبيه لكي لا يتكرر
      conn.execute("UPDATE tasks SET notified = 1 WHERE id = ?", (task["id"],))


# تشغيل الفاحص الدوري كل ساعة (أو يومياً)
scheduler = BackgroundScheduler()
scheduler.add_job(func=check_and_send_alerts, trigger="interval", hours=1)
scheduler.start()


@app.route("/")
def home():
  user_lang = request.accept_languages.best_match(list(TRANSLATIONS.keys()))
  if not user_lang or user_lang not in TRANSLATIONS:
    user_lang = "en"

  t = TRANSLATIONS[user_lang]

  with get_db_connection() as conn:
    tasks = conn.execute("SELECT * FROM tasks ORDER BY id DESC").fetchall()

  total_count = len(tasks)
  # التحقق أصبح أسهل بعد توحيد القيمة إلى 'high'
  high_count = sum(1 for task in tasks if task["priority"] == "high")

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
  title = request.form.get("title", "").strip()
  due_date = request.form.get("due_date", "").strip()
  priority = request.form.get(
      "priority", "normal"
  )  # يُفضل أخذ 'high' أو 'normal' من الفورم
  category = request.form.get("category", "general")
  email = request.form.get("email", "").strip()

  if not (title and due_date and email):
    flash("جميع الحقول مطلوبة!")
    return redirect(url_for("home"))

  try:
    datetime.strptime(due_date, "%Y-%m-%d")
    with get_db_connection() as conn:
      conn.execute(
          "INSERT INTO tasks (title, due_date, priority, category, email)"
          " VALUES (?, ?, ?, ?, ?)",
          (title, due_date, priority, category, email),
      )
  except ValueError:
    flash("تاريخ غير صحيح!")

  return redirect(url_for("home"))


@app.route("/delete/<int:task_id>", methods=["POST"])
def delete_task(task_id):
  with get_db_connection() as conn:
    conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
  return redirect(url_for("home"))


if __name__ == "__main__":
  app.run(host="0.0.0.0", port=5000, debug=True)
