import psutil
import subprocess
import platform
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

## for json body approach
class AppRequest(BaseModel):
    app_name:str

@router.get("/stats")
def get_system_stats():
    return {
        "cpu_percent": psutil.cpu_percent(),
        "memory_percent": psutil.virtual_memory().percent,
        "memory_used": psutil.virtual_memory().used,
        "memory_total": psutil.virtual_memory().total,
        "disk_usage": psutil.disk_usage('/').percent
    }


@router.post("/open")
def open_application(app_request: AppRequest):
    app_name = app_request.app_name.lower()
    app_commands = {
        "chrome": ["google-chrome", "chrome", "google-chrome-stable"],
        "firefox": ["firefox"],
        "notepad": ["notepad.exe", "gedit", "textedit"],
        "calculator": ["calc.exe", "gnome-calculator"],
        "vscode": ["code", "visual-studio-code"],
        "terminal": ["cmd.exe", "gnome-terminal", "terminal"],
        "explorer": ["explorer.exe", "nautilus", "dolphin"],
        "browser": ["chrome.exe", "google-chrome", "firefox"] 
    }
    
    if app_name not in app_commands:
        return {"error": f"Application '{app_name}' not supported. Available: {list(app_commands.keys())}"}
    
    system = platform.system().lower()
    command = app_commands[app_name]
    
    try:
        if system == "windows":
            subprocess.Popen(command[0], shell=True)
        else:
            for cmd in command:
                try:
                    subprocess.Popen(cmd)
                    break
                except:
                    continue
        return {"message": f"Opening {app_name}", "success": True}
    except Exception as e:
        return {"error": str(e), "success": False}
