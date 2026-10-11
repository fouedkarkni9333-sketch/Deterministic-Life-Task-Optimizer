from flask import Flask, render_template_string, request, redirect
import sqlite3
from datetime import datetime

app = Flask(__name__)

DB_NAME = "tasks.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            due_date TEXT NOT NULL,
            priority TEXT NOT NULL,
            category TEXT NOT NULL
        )
    ''')
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
        "dir": "rtl"
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
        "dir": "ltr"
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
        "dir": "ltr"
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
        "dir": "ltr"
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
        "dir": "ltr"
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
        "dir": "ltr"
    }
}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="{{ lang }}" dir="{{ t.dir }}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ t.title }}</title>
    <style>
        :root {
            --bg-color: #f4f6f9;
            --container-bg: #ffffff;
            --text-color: #2c3e50;
            --input-bg: #ffffff;
            --input-border: #ccc;
            --li-bg: #ecf0f1;
            --btn-color: #27ae60;
            --btn-hover: #219653;
        }
        [data-theme="dark"] {
            --bg-color: #121212;
            --container-bg: #1e1e1e;
            --text-color: #e0e0e0;
            --input-bg: #2d2d2d;
            --input-border: #444;
            --li-bg: #2a2a2a;
            --btn-color: #2ecc71;
            --btn-hover: #27ae60;
        }
        body { font-family: Tahoma, sans-serif; background-color: var(--bg-color); color: var(--text-color); margin: 0; padding: 20px; direction: {{ t.dir }}; transition: background 0.3s, color 0.3s; }
        .container { max-width: 650px; margin: auto; background: var(--container-bg); padding: 20px; border-radius: 10px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }
        .header-bar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; }
        h1 { color: var(--text-color); font-size: 20px; text-align: center; flex-grow: 1; margin: 0; }
        .theme-toggle { background: #34495e; color: white; border: none; padding: 8px 12px; border-radius: 5px; cursor: pointer; font-size: 14px; }
        form { display: flex; flex-direction: column; gap: 10px; margin-bottom: 20px; }
        input, select, button { padding: 10px; font-size: 16px; border: 1px solid var(--input-border); border-radius: 5px; background: var(--input-bg); color: var(--text-color); }
        button.submit-btn { background-color: var(--btn-color); color: white; border: none; cursor: pointer; font-weight: bold; }
        button.submit-btn:hover { background-color: var(--btn-hover); }
        .analytics-box { background: var(--li-bg); padding: 12px; border-radius: 8px; margin-bottom: 20px; font-size: 14px; }
        .analytics-box h3 { margin: 0 0 8px 0; font-size: 16px; }
        ul { list-style: none; padding: 0; }
        li { background: var(--li-bg); margin-bottom: 8px; padding: 10px; border-radius: 5px; display: flex; justify-content: space-between; align-items: center; }
        .task-info { display: flex; flex-direction: column; gap: 3px; }
        .meta { display: flex; gap: 8px; align-items: center; flex-wrap: wrap; }
        .badge { background: #e74c3c; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px; }
        .cat-badge { background: #2980b9; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px; }
        .delete-btn { background-color: #c0392b; color: white; padding: 5px 8px; border-radius: 4px; text-decoration: none; font-size: 13px; font-weight: bold; }
    </style>
</head>
<body data-theme="light">
    <div class="container">
        <div class="header-bar">
            <h1>{{ t.title }}</h1>
            <button class="theme-toggle" onclick="toggleTheme()" id="themeBtn">🌙 {{ t.dark_mode }}</button>
        </div>

        <div class="analytics-box">
            <h3>📊 {{ t.analytics }}</h3>
            <p>📌 {{ t.total_tasks }} <strong>{{ total_count }}</strong> | 🔥 {{ t.high_priority }} <strong>{{ high_count }}</strong></p>
        </div>

        <form action="/add" method="POST">
