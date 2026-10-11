from datetime import datetime
from flask import Flask, jsonify, redirect, render_template_string, request

app = Flask(__name__)

# استخدام قائمة في الذاكرة لتخزين المهام بشكل دائم أثناء التشغيل (أو قاعدة بيانات بسيطة)
# سنطورها لاحقاً لترتبط بـ SQLite بشكل كامل
TASKS_DATABASE = []

# تصميم واجهة مستخدم (HTML/CSS) أنيقة وسريعة مباشرة من السيرفر
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
        
        <h2>المهام الموثقة:</h2>
        <ul>
            {% for task in tasks %}
            <li>
                <div class="task-info">
                    <strong>{{ task.title }}</strong>
                    <small>الموعد: {{ task.due_date }}</small>
                </div>
                <span class="badge">{{ task.priority }}</span>
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
  return render_template_string(HTML_TEMPLATE, tasks=TASKS_DATABASE)


# محرك إضافة المهام عبر الواجهة أو الـ API بصرامة تامة
@app.route("/add", methods=["POST"])
def add_task_web():
  title = request.form.get("title")
  due_date = request.form.get("due_date")
  priority = request.form.get("priority", "عادية")

  if title and due_date:
    # تحقق صارم من التاريخ
    try:
      datetime.strptime(due_date, "%Y-%m-%d")
      task = {
          "id": len(TASKS_DATABASE) + 1,
          "title": title,
          "due_date": due_date,
          "priority": priority,
      }
      TASKS_DATABASE.append(task)
    except ValueError:
      pass

  return redirect("/")


if __name__ == "__main__":
  app.run(host="0.0.0.0", port=5000, debug=True)
