from flask import Flask, render_template, request, jsonify
import json, os

app = Flask(__name__)
TASKS_FILE = "tasks.json"

def load_tasks():
    if not os.path.exists(TASKS_FILE):
        save_tasks([])
        return []
    try:
        with open(TASKS_FILE, "r") as f:
            content = f.read().strip()
            if not content:
                save_tasks([])
                return []
            return json.loads(content)
    except (json.JSONDecodeError, ValueError):
        save_tasks([])
        return []

def save_tasks(tasks):
    with open(TASKS_FILE, "w") as f:
        json.dump(tasks, f, indent=2, ensure_ascii=False)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/tasks", methods=["GET"])
def get_tasks():
    return jsonify(load_tasks())

@app.route("/tasks", methods=["POST"])
def add_task():
    data = request.json
    tasks = load_tasks()
    new_task = {
        "id": int(tasks[-1]["id"]) + 1 if tasks else 1,
        "title": data["title"],
        "done": False,
        "category": data.get("category", "outro"),
        "due_date": data.get("due_date", "")
    }
    tasks.append(new_task)
    save_tasks(tasks)
    return jsonify(new_task), 201

@app.route("/tasks/<int:task_id>", methods=["PUT"])
def toggle_task(task_id):
    tasks = load_tasks()
    for task in tasks:
        if task["id"] == task_id:
            task["done"] = not task["done"]
            save_tasks(tasks)
            return jsonify(task)
    return jsonify({"error": "Not found"}), 404

@app.route("/tasks/<int:task_id>", methods=["PATCH"])
def edit_task(task_id):
    data = request.json
    tasks = load_tasks()
    for task in tasks:
        if task["id"] == task_id:
            if "title" in data:
                task["title"] = data["title"]
            save_tasks(tasks)
            return jsonify(task)
    return jsonify({"error": "Not found"}), 404

@app.route("/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    tasks = load_tasks()
    tasks = [t for t in tasks if t["id"] != task_id]
    save_tasks(tasks)
    return jsonify({"message": "Deleted"})

if __name__ == "__main__":
    app.run(debug=True)