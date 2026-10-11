from datetime import datetime
from flask import Flask, jsonify, request

app = Flask(__name__)

# قاعدة بيانات وهمية في الذاكرة (لتجربة النواة الأولى، يمكن استبدالها لاحقاً بـ SQLite)
TASKS_DATABASE = []


@app.route("/")
def home():
  return jsonify({
      "status": "online",
      "message": "Deterministic Life & Task Optimizer Core is Running 100%",
      "timestamp": datetime.now().isoformat(),
  })


# 1. محرك إضافة المهام بدقة تامة (Deterministic Task Adder)
@app.route("/api/add_task", methods=["POST"])
def add_task():
  data = request.get_json()

  title = data.get("title")
  due_date = data.get("due_date")   بصيغة YYYY-MM-DD
  priority = data.get("priority", "Normal")

  if not title or not due_date:
    return (
        jsonify({
            "error": "Missing required fields (title, due_date). 100% strict rule."
        }),
        400,
    )

  # التحقق الصارم من صحة تاريخ الإدخال
  try:
    parsed_date = datetime.strptime(due_date, "%Y-%m-%d")
  except ValueError:
    return (
        jsonify({
            "error": "Invalid date format. Must be YYYY-MM-DD strictly."
        }),
        400,
    )

  task = {
      "id": len(TASKS_DATABASE) + 1,
      "title": title,
      "due_date": due_date,
      "priority": priority,
      "status": "Pending",
      "created_at": datetime.now().isoformat(),
  }

  TASKS_DATABASE.append(task)

  return jsonify({
      "success": True,
      "message": "Task locked and scheduled deterministically.",
      "task": task,
  })


# 2. محرك جلب المهام والتحقق منها
@app.route("/api/tasks", methods=["GET"])
def get_tasks():
  return jsonify({"total_tasks": len(TASKS_DATABASE), "tasks": TASKS_DATABASE})


if __name__ == "__main__":
  app.run(host="0.0.0.0", port=5000, debug=True)
