import json
import os
import uuid
from datetime import datetime
from fastapi import APIRouter, HTTPException
from modules.task import TaskCreate, TaskUpdate, TaskResponse

router = APIRouter()

# Define the storage directory and file path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STORAGE_DIR = os.path.join(BASE_DIR,"modules","stored")
TASKS_FILE = os.path.join(STORAGE_DIR, "tasks.json")

# Load tasks from JSON file
def load_tasks():
    if os.path.exists(TASKS_FILE):
        try:
            with open(TASKS_FILE, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []
    return []

# Save tasks to JSON file
def save_tasks(tasks_list):
    with open(TASKS_FILE, 'w') as f:
        json.dump(tasks_list, f, indent=2)

# Initialize tasks from file
tasks = load_tasks()

@router.get("/tasks")
def get_tasks():
    return {"tasks": tasks}

@router.post("/tasks", response_model=TaskResponse)
def add_task(task: TaskCreate):
    new_task = {
        "id": str(uuid.uuid4()),
        "title": task.title,
        "completed": False,
        "created_at": datetime.now().isoformat(),
        "updated_at": None
    }
    tasks.append(new_task)
    save_tasks(tasks)
    return new_task

@router.put("/tasks/{task_id}", response_model=TaskResponse)
def update_task(task_id: str, updated_task: TaskUpdate):
    for task in tasks:
        if task["id"] == task_id:
            if updated_task.title is not None:
                task["title"] = updated_task.title
            if updated_task.completed is not None:
                task["completed"] = updated_task.completed
            task["updated_at"] = datetime.now().isoformat()
            save_tasks(tasks)
            return task
    raise HTTPException(status_code=404, detail="Task not found")

@router.delete("/tasks/{task_id}")
def delete_task(task_id: str):
    global tasks
    initial_length = len(tasks)
    tasks = [t for t in tasks if t["id"] != task_id]
    
    if len(tasks) == initial_length:
        raise HTTPException(status_code=404, detail="Task not found")
    
    save_tasks(tasks)
    return {"message": "Task deleted", "id": task_id}