from datetime import datetime
import os
import sqlite3
from flask import Flask, redirect, render_template, request

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
            priority TEXT NOT NULL,
            category TEXT NOT NULL
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
        "btn": "تثبيت وإضافة المهمة",
        "list_title": "المهام الموثقة:",
        "due": "الموعد:",
        "empty": "لا توجد مهام مسجلة حالياً.",
        "delete": "إنجاز وحذف",
        "analytics": "لوحة تحليلات والإحصائيات الإنتاجية",
        "total_tasks": "إجمالي المهام:",
        "high_priority": "المهام ذات الأولوية العالية:",
        "dark_mode": "الوضع الداكن",
        "light_mode": "الوضع المضيء",
        "dir": "rtl",
    },
    "zh": {
        "title": "全球智能生活与任务优化器",
        "placeholder": "任务标题或目标...",
        "priority_normal": "普通优先级",
        "priority_high": "高优先级",
        "cat_work": "工作",
        "cat_personal": "个人",
        "cat_study": "学习",
        "cat_health": "健康",
        "btn": "确认并添加任务",
        "list_title": "已验证的任务：",
        "due": "截止日期：",
        "empty": "暂无记录的任务。",
        "delete": "完成并删除",
        "analytics": "生产力分析面板",
        "total_tasks": "总任务数：",
        "high_priority": "高优先级任务：",
        "dark_mode": "深色模式",
        "light_mode": "浅色模式",
        "dir": "ltr",
    },
    "de": {
        "title": "Globaler Intelligenz- und Aufgaben-Optimizer",
        "placeholder": "Aufgabentitel oder Ziel...",
        "priority_normal": "Normale Priorität",
        "priority_high": "Hohe Priorität",
        "cat_work": "Arbeit",
        "cat_personal": "Persönlich",
        "cat_study": "Studium",
        "cat_health": "Gesundheit",
        "btn": "Aufgabe hinzufügen",
        "list_title": "Verifizierte Aufgaben:",
        "due": "Fälligkeitsdatum:",
        "empty": "Noch keine Aufgaben registriert.",
        "delete": "Erledigen & Löschen",
        "analytics": "Produktivitäts-Analyse-Dashboard",
        "total_tasks": "Gesamtaufgaben:",
        "high_priority": "Hohe Priorität:",
        "dark_mode": "Dunkelmodus",
        "light_mode": "Hellmodus",
        "dir": "ltr",
    },
    "fr": {
        "title": "Optimiseur Intelligent de Vie et de Tâches",
        "placeholder": "Titre de la tâche ou objectif...",
        "priority_normal": "Priorité normale",
        "priority_high": "Haute priorité",
        "cat_work": "Travail",
        "cat_personal": "Personnel",
        "cat_study": "Études",
        "cat_health": "Santé",
        "btn": "Confirmer et ajouter",
        "list_title": "Tâches vérifiées :",
        "due": "Date d'échéance :",
        "empty": "Aucune tâche enregistrée pour le moment.",
        "delete": "Terminer & Supprimer",
        "analytics": "Tableau de bord analytique",
        "total_tasks": "Total des tâches :",
        "high_priority": "Priorité haute :",
        "dark_mode": "Mode sombre",
        "light_mode": "Mode clair",
        "dir": "ltr",
    },
    "es": {
        "title": "Optimizador Global de Vida y Tareas",
        "placeholder": "Título de la tarea u objetivo...",
        "priority_normal": "Prioridad normal",
        "priority_high": "Alta prioridad",
        "cat_work": "Trabajo",
        "cat_personal": "Personal",
        "cat_study": "Estudio",
        "cat_health": "Salud",
        "btn": "Confirmar y añadir tarea",
        "list_title": "Tareas verificadas:",
        "due": "Fecha límite:",
        "empty": "No hay tareas registradas aún.",
        "delete": "Completar y borrar",
        "analytics": "Panel de análisis de productividad",
        "total_tasks": "Tareas totales:",
        "high_priority": "Prioridad alta:",
        "dark_mode": "Modo oscuro",
        "light_mode": "Modo claro",
        "dir": "ltr",
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
        "btn": "Confirm & Add Task",
        "list_title": "Verified Tasks:",
        "due": "Due Date:",
        "empty": "No tasks registered yet.",
        "delete": "Complete & Delete",
        "analytics": "Productivity Analytics Dashboard",
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
      1
      for task in tasks
      if task[3]
      in [
          "High Priority",
          "أولوية عالية جداً",
          "高优先级",
          "Hohe Priorität",
          "Haute priorité",
          "Alta prioridad",
      ]
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

  if title and due_date:
    try:
      datetime.strptime(due_date, "%Y-%m-%d")
      conn = sqlite3.connect(DB_NAME)
      cursor = conn.cursor()
      cursor.execute(
          "INSERT INTO tasks (title, due_date, priority, category) VALUES (?, ?,"
          " ?, ?)",
          (title, due_date, priority, category),
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
