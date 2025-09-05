# backend/modules/action_executor.py
import requests
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

# Your backend base URL
BACKEND_BASE = "http://127.0.0.1:8000/api"

def execute_action(action_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute an action based on the parsed command
    Returns: {"success": bool, "message": str, "data": Any}
    """
    action = action_data.get("action")
    params = action_data.get("params", {})
    
    logger.debug(f"Executing action: {action} with params: {params}")
    
    try:
        if action == "task_add" and "title" in params:
            # Call tasks endpoint to add a task
            response = requests.post(
                f"{BACKEND_BASE}/tasks",
                json={"title": params["title"]},
                timeout=5
            )
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "message": f"Task '{params['title']}' added successfully",
                    "data": response.json()
                }
            else:
                return {
                    "success": False,
                    "message": "Failed to add task",
                    "data": None
                }
                
        elif action == "task_list":
            # Call tasks endpoint to get all tasks
            response = requests.get(f"{BACKEND_BASE}/tasks", timeout=5)
            
            if response.status_code == 200:
                tasks = response.json().get("tasks", [])
                return {
                    "success": True,
                    "message": f"Found {len(tasks)} tasks",
                    "data": {"tasks": tasks}
                }
            else:
                return {
                    "success": False,
                    "message": "Failed to get tasks",
                    "data": None
                }
                
        elif action == "task_delete" and "title" in params:
            # For now, we'll just return a message since we need task ID to delete
            # In a real implementation, you'd need to find the task by title first
            return {
                "success": True,
                "message": f"Would delete task: {params['title']}",
                "data": None
            }
            
        elif action == "system_stats":
            # Call system stats endpoint
            response = requests.get(f"{BACKEND_BASE}/system/stats", timeout=5)
            
            if response.status_code == 200:
                stats = response.json()
                return {
                    "success": True,
                    "message": "System stats retrieved",
                    "data": stats
                }
            else:
                return {
                    "success": False,
                    "message": "Failed to get system stats",
                    "data": None
                }
                
        elif action == "open_app" and "app" in params:
            # Call open app endpoint
            response = requests.post(
                f"{BACKEND_BASE}/system/open",
                json={"app_name": params["app"]},
                timeout=5
            )
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "message": f"Opening {params['app']}",
                    "data": response.json()
                }
            else:
                return {
                    "success": False,
                    "message": f"Failed to open {params['app']}",
                    "data": None
                }
                
        elif action == "schedule":
            # Call schedule endpoint
            reminder_data = {
                "time": params.get("time", "now"),
                "message": params.get("message", "Reminder")
            }
            
            response = requests.post(
                f"{BACKEND_BASE}/schedule",
                json=reminder_data,
                timeout=5
            )
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "message": f"Reminder set for {params.get('message')}",
                    "data": response.json()
                }
            else:
                return {
                    "success": False,
                    "message": "Failed to set reminder",
                    "data": None
                }
                
        elif action == "chat":
            # Call chat endpoint
            response = requests.post(
                "http://127.0.0.1:8000/chat",
                json={"text": params.get("message", "")},
                timeout=10
            )
            
            if response.status_code == 200:
                chat_response = response.json().get("response", "I didn't understand that")
                return {
                    "success": True,
                    "message": "Chat response",
                    "data": response.json(),
                    "tts_response": chat_response
                }
            else:
                return {
                    "success": False,
                    "message": "Chat service unavailable",
                    "data": None
                }
                
        else:
            return {
                "success": False,
                "message": f"Unknown action: {action}",
                "data": None
            }
            
    except requests.exceptions.Timeout:
        return {
            "success": False,
            "message": "Request timeout - service not responding",
            "data": None
        }
    except requests.RequestException as e:
        return {
            "success": False,
            "message": f"Network error: {e}",
            "data": None
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Unexpected error: {e}",
            "data": None
        }
