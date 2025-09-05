# 📁 modules/voice_io.py
import speech_recognition as sr
import pyttsx3
import re
import requests, time
import winsound
import random  # Add this import
from typing import Optional, Dict, Any

# Initialize engines
recognizer = sr.Recognizer()
tts_engine = pyttsx3.init()

# ==================== ANALYTICS SETUP ====================
# Add command analytics tracking
command_analytics = {
    "total_commands": 0,
    "successful_commands": 0,
    "failed_commands": 0,
    "command_types": {},
    "response_times": [],
    "last_command": None,
    "last_response_time": 0
}

def get_voice_analytics():
    """Return analytics data for API endpoint"""
    total = command_analytics["total_commands"]
    successful = command_analytics["successful_commands"]
    
    return {
        "total_commands": total,
        "success_rate": (successful / total * 100) if total > 0 else 0,
        "popular_commands": dict(
            sorted(command_analytics["command_types"].items(), 
                  key=lambda x: x[1], reverse=True)[:5]
        ),
        "avg_response_time": (
            sum(command_analytics["response_times"]) / 
            len(command_analytics["response_times"])
            if command_analytics["response_times"] else 0
        ),
        "last_command": command_analytics["last_command"],
        "last_response_time": command_analytics["last_response_time"]
    }
# ==================== END ANALYTICS ====================


# Configure TTS
def setup_tts():
    tts_engine.setProperty('rate', 180)
    voices = tts_engine.getProperty('voices')
    
    # Prefer female voice if available
    for voice in voices:
        if "female" in voice.name.lower() or "zira" in voice.name.lower():
            tts_engine.setProperty('voice', voice.id)
            break
    print("✅ TTS Engine configured")

# Voice personality settings
VOICE_PERSONALITY = {
    "professional": {"rate": 180, "assertive": True},
    "friendly": {"rate": 170, "assertive": False},
    "energetic": {"rate": 200, "assertive": True}
}

current_personality = "friendly"

def set_voice_personality(personality: str):
    """Change voice personality"""
    global current_personality
    if personality in VOICE_PERSONALITY:
        current_personality = personality
        setup_tts()  # Reapply settings



def speak(text: str, is_command_response: bool = False):
    """Speak with current personality"""
    personality = VOICE_PERSONALITY[current_personality]
    tts_engine.setProperty('rate', personality["rate"])
    
    if personality["assertive"] and is_command_response:
        text = text.upper() if random.random() > 0.7 else text
    
    print(f"🗣️ NeuroTrain ({current_personality}): {text}")
    tts_engine.say(text)
    tts_engine.runAndWait()

def listen(timeout: int = 5, phrase_time_limit: int = 10, listening_callback=None) -> Optional[str]:
    """Listen for voice input with visual feedback"""
    if listening_callback:
        listening_callback("start")  # UI: Show listening indicator
    
    with sr.Microphone() as source:
        print("🎤 Listening...")
        try:
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
            text = recognizer.recognize_google(audio)
            print("👤 User said:", text)
            
            if listening_callback:
                listening_callback("stop")  # UI: Hide listening indicator
                
            return text.lower()
        except sr.WaitTimeoutError:
            if listening_callback:
                listening_callback("timeout")  # UI: Show timeout indicator
            print("⏰ Listening timeout")
            return None
        except Exception as e:
            if listening_callback:
                listening_callback("error")  # UI: Show error indicator
            print(f"❌ Listening error: {e}")
            return None

def parse_voice_command(text: str) -> Dict[str, Any]:
    """Parse voice text and determine intent"""
    if not text:
        return {"intent": "unknown", "action": "none", "original_text": ""}
    
    text = text.lower().strip()
    
    # Task commands
    if re.match(r'(add|create|new).*task.*', text):
        task_match = re.search(r'(add|create|new).*task.*to (.+)', text) or re.search(r'(add|create|new).*task.*called (.+)', text)
        if task_match:
            return {
                "intent": "task", 
                "action": "add", 
                "title": task_match.group(2).strip(),
                "original_text": text
            }
    
    # System commands - FIXED REGEX
    elif re.match(r'.*(cpu|memory|ram|disk|system).*(usage|stats|status).*', text):
        return {"intent": "system", "action": "get_stats", "original_text": text}
    
    elif re.match(r'(open|launch|start).*(chrome|firefox|notepad|calculator|vscode|browser|app|application).*', text):
        app_match = re.search(r'(open|launch|start).*(chrome|firefox|notepad|calculator|vscode|browser)', text)
        if app_match:
            app_name = app_match.group(2)
            # Map browser to specific app
            if app_name == "browser":
                app_name = "chrome"
            return {
                "intent": "system", 
                "action": "open_app", 
                "app_name": app_name,
                "original_text": text
            }
    
    # Schedule commands
    elif re.match(r'(set|add|create).*(reminder|alarm|schedule).*', text):
        return {"intent": "schedule", "action": "add_reminder", "original_text": text}
    # Add to parse_voice_command function
    elif "and then" in text or "after that" in text:
        # Handle multi-step commands: "open chrome and then check cpu usage"
        parts = re.split(r'\b(?:and then|after that|then)\b', text)
        return {
            "intent": "multi",
            "actions": [parse_voice_command(part.strip()) for part in parts],
            "original_text": text
        }
    # Default to chat
    else:
        return {"intent": "chat", "action": "process_chat", "original_text": text}

def execute_voice_command(command: Dict[str, Any]) -> str:
    """Execute the parsed command and return response"""
    start_time = time.time()
    
    # Track command type
    command_analytics["total_commands"] += 1
    command_analytics["command_types"][command["intent"]] = \
        command_analytics["command_types"].get(command["intent"], 0) + 1

    try:
        if command["intent"] == "task" and command["action"] == "add":
            # Call your tasks API
            response = requests.post(
                "http://127.0.0.1:8000/api/tasks",
                json={"title": command["title"]}
            )
            if response.status_code == 200:
                play_sound("success")
                result = f"✅ Task '{command['title']}' has been added to your list!"
                command_analytics["successful_commands"] += 1
            else:
                play_sound("error")
                result = "❌ I couldn't add that task. Please try again."
                command_analytics["failed_commands"] += 1
        
        elif command["intent"] == "system" and command["action"] == "get_stats":
            response = requests.get("http://127.0.0.1:8000/api/system/stats")
            if response.status_code == 200:
                stats = response.json()
                play_sound("success")
                result = f"📊 CPU: {stats['cpu_percent']}%, Memory: {stats['memory_percent']}%"
                command_analytics["successful_commands"] += 1
            else:
                play_sound("error")
                result = "❌ Couldn't retrieve system statistics."
                command_analytics["failed_commands"] += 1
        
        elif command["intent"] == "system" and command["action"] == "open_app":
            response = requests.post(
                "http://127.0.0.1:8000/api/system/open", 
                json={"app_name": command["app_name"]}
            )
            if response.status_code == 200:
                result_data = response.json()
                if result_data.get("success"):
                    result = f"🚀 Opening {command['app_name']}"
                    command_analytics["successful_commands"] += 1
                    play_sound("success")
                else:
                    result = f"❌ Failed to open {command['app_name']}"
                    command_analytics["failed_commands"] += 1
                    play_sound("error")
            else:
                result = f"❌ Failed to open {command['app_name']}"
                command_analytics["failed_commands"] += 1
                play_sound("error")
        
        elif command["intent"] == "chat":
            try:
                response = requests.post(
                    "http://127.0.0.1:8000/chat",
                    json={"text": command["original_text"]},
                    timeout=15
                )
                
                if response.status_code == 200:
                    result_data = response.json()
                    reply = result_data.get("reply", "")
                    if reply.startswith("AI: "):
                        reply = reply[4:]
                    result = reply or "💬 I'm here to help!"
                    command_analytics["successful_commands"] += 1
                else:
                    result = "❌ Chat service returned an error"
                    command_analytics["failed_commands"] += 1
                    
            except requests.exceptions.Timeout:
                result = "⏳ The AI is thinking... please try again"
                command_analytics["failed_commands"] += 1
            except Exception as e:
                result = f"❌ Chat error: {str(e)}"
                command_analytics["failed_commands"] += 1
        
        else:
            result = "❌ Command not implemented yet"
            command_analytics["failed_commands"] += 1
            
    except Exception as e:
        result = f"⚠️ Sorry, I encountered an error: {str(e)}"
        command_analytics["failed_commands"] += 1
        play_sound("error")
    
    # Calculate response time and store analytics
    end_time = time.time()
    response_time = end_time - start_time
    command_analytics["response_times"].append(response_time)
    command_analytics["last_response_time"] = response_time
    command_analytics["last_command"] = {
        "command": command,
        "response": result,
        "timestamp": time.time(),
        "response_time": response_time
    }
    
    return result


def continuous_listen(callback, wake_word: str = "hey neurotrain"):
    """Continuous listening mode with wake word detection"""
    print(f"🔊 Continuous listening started. Say '{wake_word}' to activate.")
    
    while True:
        try:
            text = listen(timeout=10, phrase_time_limit=5)
            
            if text and wake_word.lower() in text:
                print(f"✅ Wake word detected: {wake_word}")
                speak("Yes, I'm listening", is_command_response=True)
                
                # Listen for actual command
                command_text = listen(timeout=8, phrase_time_limit=15)
                if command_text:
                    # Parse and execute command
                    command = parse_voice_command(command_text)
                    response = execute_voice_command(command)
                    
                    # Speak response
                    speak(response, is_command_response=True)
                    
                    # Call callback if provided (for UI updates)
                    if callback:
                        callback(command_text, response)
            
        except KeyboardInterrupt:
            print("🛑 Continuous listening stopped")
            break
        except Exception as e:
            print(f"❌ Error in continuous listening: {e}")
            continue

def play_sound(effect: str):
    """Play different sound effects"""
    try:
        if effect == "start_listening":
            winsound.Beep(1000, 200)  # Start beep
        elif effect == "stop_listening":
            winsound.Beep(800, 200)   # Stop beep
        elif effect == "success":
            winsound.Beep(1200, 300)  # Success beep
        elif effect == "error":
            winsound.Beep(500, 500)   # Error beep
    except:
        pass  # Silently fail if sound not available






# Initialize on import
setup_tts()