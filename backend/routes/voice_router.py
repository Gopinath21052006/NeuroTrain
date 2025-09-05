# backend/modules/voice_router.py
import re
import requests
from fastapi import APIRouter, HTTPException
from modules.voice import VoiceCommandRequest, ParsedCommandResponse, CommandExecutionResponse

router = APIRouter()

# Your backend base URL - FIXED: Use consistent URL format
BACKEND_BASE = "http://127.0.0.1:8000/api"

# Add debug logging
import logging,time
logger = logging.getLogger(__name__)

def parse_voice_command(text: str) -> ParsedCommandResponse:
    """
    Parse voice text and determine intent with confidence scoring
    """
    logger.debug(f"Parsing voice command: {text}")

    if not text or len(text.strip()) < 2:
        return ParsedCommandResponse(
            intent="unknown",
            action="none",
            parameters={},
            original_text=text or "",
            confidence=0.0
        )
    
    text_lower = text.lower().strip()
    parameters = {"original_text": text}
    
    # Task commands - high confidence patterns
    task_patterns = [
        (r'(add|create|new).*task.*to (.+)', "add_task"),
        (r'(add|create|new).*task.*called (.+)', "add_task"),
        (r'(add|create|new).*task.*to do (.+)', "add_task"),
        (r'(add|create|new).*remind me to (.+)', "add_task"),
        (r'delete.*task.*', "delete_task"),
        (r'remove.*task.*', "delete_task"),
        (r'clear.*task.*', "delete_task"),
        (r'show.*task.*', "get_tasks"),
        (r'list.*task.*', "get_tasks"),
        (r'what.*task.*', "get_tasks"),
    ]
    
    for pattern, action in task_patterns:
        match = re.search(pattern, text_lower)
        if match:
            if action == "add_task" and match.lastindex >= 2:
                parameters["title"] = match.group(2).strip()
            return ParsedCommandResponse(
                intent="task",
                action=action,
                parameters=parameters,
                original_text=text,
                confidence=0.9
            )
    
    # System commands
    system_patterns = [
    # System monitoring patterns
    (r'.*(cpu|processor).*(usage|load|percent).*', "system_stats"),
    (r'.*(memory|ram).*(usage|percent).*', "system_stats"),
    (r'.*(disk|storage).*(usage|percent).*', "system_stats"),
    (r'.*(system|computer).*(status|stats).*', "system_stats"),
    
    # Web browsers
    (r'(open|launch|start).*(chrome|browser).*', "open_app"),
    (r'(open|launch|start).*(firefox).*', "open_app"),
    (r'(open|launch|start).*(edge|microsoft edge).*', "open_app"),
    (r'(open|launch|start).*(safari).*', "open_app"),
    (r'(open|launch|start).*(opera).*', "open_app"),
    (r'(open|launch|start).*(brave).*', "open_app"),
    
    # Office and productivity
    (r'(open|launch|start).*(notepad|text editor).*', "open_app"),
    (r'(open|launch|start).*(word|microsoft word).*', "open_app"),
    (r'(open|launch|start).*(excel|microsoft excel).*', "open_app"),
    (r'(open|launch|start).*(powerpoint|microsoft powerpoint).*', "open_app"),
    (r'(open|launch|start).*(outlook).*', "open_app"),
    (r'(open|launch|start).*(calendar).*', "open_app"),
    (r'(open|launch|start).*(notes|stickies).*', "open_app"),
    
    # Development tools
    (r'(open|launch|start).*(vscode|code|visual studio).*', "open_app"),
    (r'(open|launch|start).*(pycharm).*', "open_app"),
    (r'(open|launch|start).*(intellij|idea).*', "open_app"),
    (r'(open|launch|start).*(eclipse).*', "open_app"),
    (r'(open|launch|start).*(sublime|sublime text).*', "open_app"),
    (r'(open|launch|start).*(atom).*', "open_app"),
    (r'(open|launch|start).*(terminal|command prompt|cmd).*', "open_app"),
    (r'(open|launch|start).*(powershell).*', "open_app"),
    
    # Media and entertainment
    (r'(open|launch|start).*(calculator).*', "open_app"),
    (r'(open|launch|start).*(spotify).*', "open_app"),
    (r'(open|launch|start).*(vlc|media player).*', "open_app"),
    (r'(open|launch|start).*(windows media player).*', "open_app"),
    (r'(open|launch|start).*(itunes).*', "open_app"),
    (r'(open|launch|start).*(netflix).*', "open_app"),
    (r'(open|launch|start).*(youtube).*', "open_app"),
    
    # Communication apps
    (r'(open|launch|start).*(slack).*', "open_app"),
    (r'(open|launch|start).*(discord).*', "open_app"),
    (r'(open|launch|start).*(teams|microsoft teams).*', "open_app"),
    (r'(open|launch|start).*(zoom).*', "open_app"),
    (r'(open|launch|start).*(skype).*', "open_app"),
    (r'(open|launch|start).*(whatsapp).*', "open_app"),
    
    # Graphics and design
    (r'(open|launch|start).*(photoshop).*', "open_app"),
    (r'(open|launch|start).*(illustrator).*', "open_app"),
    (r'(open|launch|start).*(paint).*', "open_app"),
    (r'(open|launch|start).*(gimp).*', "open_app"),
    (r'(open|launch|start).*(inkscape).*', "open_app"),
    
    # File management
    (r'(open|launch|start).*(file explorer|explorer|files).*', "open_app"),
    (r'(open|launch|start).*(finder).*', "open_app"),
    
    # System utilities
    (r'(open|launch|start).*(task manager).*', "open_app"),
    (r'(open|launch|start).*(control panel).*', "open_app"),
    (r'(open|launch|start).*(settings).*', "open_app"),
    
    # Games
    (r'(open|launch|start).*(steam).*', "open_app"),
    (r'(open|launch|start).*(epic games).*', "open_app"),
    (r'(open|launch|start).*(minecraft).*', "open_app"),
]
    
    for pattern, action in system_patterns:
        if re.search(pattern, text_lower):
            # Extract app name for open commands
            if action == "open_app":
                app_match = re.search(r'(open|launch|start).*(chrome|firefox|notepad|calculator|vscode|browser)', text_lower)
                if app_match and app_match.lastindex >= 2:
                    parameters["app_name"] = app_match.group(2)
            
            return ParsedCommandResponse(
                intent="system",
                action=action,
                parameters=parameters,
                original_text=text,
                confidence=0.85
            )
    
    # Schedule commands
    schedule_patterns = [
        (r'(set|add|create).*(reminder|alarm).*to (.+)', "add_reminder"),
        (r'(set|add|create).*(reminder|alarm).*for (.+)', "add_reminder"),
        (r'remind me to (.+)', "add_reminder"),
        (r'show.*(reminder|alarm).*', "get_schedule"),
        (r'list.*(reminder|alarm).*', "get_schedule"),
    ]
    
    for pattern, action in schedule_patterns:
        match = re.search(pattern, text_lower)
        if match:
            if action == "add_reminder" and match.lastindex >= 3:
                parameters["message"] = match.group(3).strip()
            return ParsedCommandResponse(
                intent="schedule",
                action=action,
                parameters=parameters,
                original_text=text,
                confidence=0.8
            )
    
    # Default to chat
    return ParsedCommandResponse(
        intent="chat",
        action="process_chat",
        parameters=parameters,
        original_text=text,
        confidence=0.7
    )

async def execute_command(parsed_command: ParsedCommandResponse) -> CommandExecutionResponse:
    """
    Execute the parsed command by calling appropriate endpoints
    """
    logger.debug(f"Executing command: {parsed_command.intent}.{parsed_command.action}")
    logger.debug(f"Parameters: {parsed_command.parameters}")
    
    start_time = time.time()
    try:
        intent = parsed_command.intent
        action = parsed_command.action
        params = parsed_command.parameters
        
        if intent == "task":
            if action == "add_task" and "title" in params:
                logger.debug(f"Calling {BACKEND_BASE}/tasks with title: {params['title']}")
                task_start = time.time()
                response = requests.post(
                    f"{BACKEND_BASE}/tasks",
                    json={"title": params["title"]},
                    timeout=10
                )
                task_time = time.time() - task_start
                logger.debug(f"Tasks call completed in {task_time:.2f}s - Status: {response.status_code}")
                
                if response.status_code == 200:
                    return CommandExecutionResponse(
                        success=True,
                        message="Task added successfully",
                        data=response.json(),
                        tts_response=f"Task '{params['title']}' added successfully"
                    )
                else:
                    return CommandExecutionResponse(
                        success=False,
                        message="Failed to add task",
                        tts_response="Sorry, I couldn't add the task"
                    )
            
            elif action == "get_tasks":
                logger.debug(f"Calling {BACKEND_BASE}/tasks")
                task_start = time.time()
                response = requests.get(f"{BACKEND_BASE}/tasks", timeout=10)
                task_time = time.time() - task_start
                logger.debug(f"Get tasks call completed in {task_time:.2f}s - Status: {response.status_code}")
                
                if response.status_code == 200:
                    tasks = response.json().get("tasks", [])
                    return CommandExecutionResponse(
                        success=True,
                        message=f"Found {len(tasks)} tasks",
                        data={"tasks": tasks},
                        tts_response=f"You have {len(tasks)} tasks in your list"
                    )
                else:
                    return CommandExecutionResponse(
                        success=False,
                        message="Failed to get tasks",
                        tts_response="Sorry, I couldn't retrieve your tasks"
                    )
            
            elif action == "get_tasks":
                response = requests.get(f"{BACKEND_BASE}/tasks")
                if response.status_code == 200:
                    tasks = response.json().get("tasks", [])
                    return CommandExecutionResponse(
                        success=True,
                        message=f"Found {len(tasks)} tasks",
                        data={"tasks": tasks},
                        tts_response=f"You have {len(tasks)} tasks in your list"
                    )
                else:
                    return CommandExecutionResponse(
                        success=False,
                        message="Failed to get tasks",
                        tts_response="Sorry, I couldn't retrieve your tasks"
                    )
        
        elif intent == "system":
            if action == "system_stats":
                logger.debug(f"Calling {BACKEND_BASE}/system/stats")
                response = requests.get(f"{BACKEND_BASE}/system/stats", timeout=5)
                if response.status_code == 200:
                    stats = response.json()
                    return CommandExecutionResponse(
                        success=True,
                        message="System stats retrieved",
                        data=stats,
                        tts_response=f"CPU is at {stats.get('cpu_percent', 0)} percent, Memory at {stats.get('memory_percent', 0)} percent"
                    )
                else:
                    return CommandExecutionResponse(
                        success=False,
                        message="Failed to get system stats",
                        tts_response="Sorry, I couldn't retrieve system information"
                    )
            
            elif action == "open_app" and "app_name" in params:
                logger.debug(f"Calling {BACKEND_BASE}/system/open")
                response = requests.post(
                    f"{BACKEND_BASE}/system/open",
                    json={"app_name": params["app_name"]},
                    timeout=5
                )
                if response.status_code == 200:
                    return CommandExecutionResponse(
                        success=True,
                        message=f"Opening {params['app_name']}",
                        data=response.json(),
                        tts_response=f"Opening {params['app_name']}"
                    )
                else:
                    return CommandExecutionResponse(
                        success=False,
                        message=f"Failed to open {params['app_name']}",
                        tts_response=f"Sorry, I couldn't open {params['app_name']}"
                    )
        
        elif intent == "schedule":
            if action == "add_reminder" and "message" in params:
                logger.debug(f"Calling {BACKEND_BASE}/schedule")
                # For now, use a default time - you can enhance this later
                reminder_data = {
                    "time": "2024-01-15 12:00:00",  # Default time
                    "message": params["message"]
                }
                response = requests.post(
                    f"{BACKEND_BASE}/schedule",
                    json=reminder_data,
                    timeout=5
                )
                if response.status_code == 200:
                    return CommandExecutionResponse(
                        success=True,
                        message="Reminder added",
                        data=response.json(),
                        tts_response=f"Reminder set for {params['message']}"
                    )
                else:
                    return CommandExecutionResponse(
                        success=False,
                        message="Failed to add reminder",
                        tts_response="Sorry, I couldn't set the reminder"
                    )
        
        # Default: send to chat endpoint
        logger.debug("Calling default chat endpoint")
        chat_start = time.time()
        response = requests.post(
            "http://127.0.0.1:8000/chat",
            json={"user_input": parsed_command.original_text},
            timeout=10
        )
        chat_time = time.time() - chat_start
        logger.debug(f"Chat call completed in {chat_time:.2f}s - Status: {response.status_code}")
        if response.status_code == 200:
            chat_response = response.json().get("response", "I didn't understand that")
            return CommandExecutionResponse(
                success=True,
                message="Chat response",
                data=response.json(),
                tts_response=chat_response
            )
        else:
            return CommandExecutionResponse(
                success=False,
                message="Chat service unavailable",
                tts_response="I'm having trouble connecting to the chat service"
            )
             
    except requests.exceptions.Timeout:
        logger.error("Request timed out")
        return CommandExecutionResponse(
            success=False,
            message="Request timeout - backend service not responding",
            tts_response="Sorry, the service is taking too long to respond"
        )
    except requests.RequestException as e:
        logger.error(f"Network error: {e}")
        return CommandExecutionResponse(
            success=False,
            message=f"Network error: {e}",
            tts_response="Network error - please check if all services are running"
        )
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return CommandExecutionResponse(
            success=False,
            message=f"Unexpected error: {e}",
            tts_response="Sorry, I encountered an error processing your request"
        )
    finally:
        end_time = time.time()
        logger.debug(f"Execution took {end_time - start_time:.2f} seconds")

@router.post("/parse", response_model=ParsedCommandResponse)
async def parse_command(request: VoiceCommandRequest):
    """
    Parse a voice command and return the interpreted intent
    """
    parsed_command = parse_voice_command(request.text)
    return parsed_command

@router.post("/execute", response_model=CommandExecutionResponse)
async def execute_voice_command(request: VoiceCommandRequest):
    """
    Parse and execute a voice command in one step
    """
    # Parse the command
    parsed_command = parse_voice_command(request.text)
    
    # Execute the command
    result = await execute_command(parsed_command)
    
    return result

@router.post("/full-process", response_model=dict)
async def full_voice_process(request: VoiceCommandRequest):
    """
    Complete voice processing: parse + execute + return all details
    """
    parsed_command = parse_voice_command(request.text)
    execution_result = await execute_command(parsed_command)
    
    return {
        "original_text": request.text,
        "parsed_command": parsed_command.dict(),
        "execution_result": execution_result.dict(),
        "session_id": request.session_id
    }

# Add this to your voice_router.py
@router.get("/test")
async def test_endpoint():
    return {"message": "Voice router is working!"}