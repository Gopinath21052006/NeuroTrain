#Imports 
'''
FastAPI        :  The web Framework for building APIs. 
HTTPException  :  Used to return HTTP error responses (eg., 404 not Found)
CORSMiddleware :  Allows cross - origin requeste (Frontend ⛓️‍💥 Backend communication )
BaseModel      :  Used for data vaildation 
'''


# backend/main.py
from fastapi import FastAPI , HTTPException   
from fastapi.middleware.cors import CORSMiddleware  
from pydantic import BaseModel
from modules.ai_chat import chat_with_ai
from routes import tasks,system,scheduler,voice_router  # import the tasks router 
from modules import voice_interface
from modules.simple_parser import parse_command
from modules.voice_io import get_voice_analytics
from modules.memory.memory_chat_history import ( 
    get_user_preferences,
    save_user_habit,
    recall_conversation_context,
    memory_system,
    save_user_preference
    )
from modules.ai_memory_wrapper import chat_with_memory
import uuid 

#FastAPI App Setup
app=FastAPI()


#CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Frontend URL (Vite default) 
    allow_credentials=True,                   # Allow cookies/ auth
    allow_methods=["*"],                      # Allows all HTTP Methods (GET, POST , etc.)
    allow_headers=["*"],                      # Allows request headers ["Content-Type"] 
)

#Include the task router 
app.include_router(tasks.router , prefix="/api",tags=["tasks"])
app.include_router(system.router,prefix="/api/system",tags=["system"])
app.include_router(scheduler.router,prefix="/api",tags=["scheduler"])
app.include_router(voice_router.router, prefix="/api/voice", tags=["voice"])

#Define the Expected Input 
class ChatRequest(BaseModel):  
    text: str 
    user_id: str = "default_user" # Add user_id field with default

# Add this model (if not already defined)
class SimpleParseRequest(BaseModel):
    text: str


# Add this after your FastAPI app setup
class SessionManager:
    def __init__(self):
        self.sessions = {}
    
    def get_session_id(self, user_id: str):  # ✅ CORRECT METHOD NAME
        if user_id not in self.sessions:
            self.sessions[user_id] = f"{user_id}_{uuid.uuid4().hex[:8]}"
        return self.sessions[user_id]

session_manager = SessionManager()



# Add this endpoint
@app.post("/voice/simple-parse")
async def voice_simple_parse(req: SimpleParseRequest):
    """
    Simple parser endpoint for testing voice command parsing
    """
    result = parse_command(req.text)
    return {"parsed": result}


#Test Route (Check if Backend is Working)
@app.get("/")
def read_root():
    return {"message":"Backend running!"}


#AI Chat Endpoind ( POST (/chat) )
@app.post("/chat")
async def chat(message: ChatRequest):
    try:
        print(f"User {message.user_id}: {message.text}")
        
        # Get session and save message ✅ FIXED
        session_id = session_manager.get_session_id(message.user_id)
        memory_system.save_conversation_message(session_id, {
            "role": "user", 
            "content": message.text
        })
        
        # SIMPLE INFO EXTRACTION
        message_lower = message.text.lower()
        if "my name is" in message_lower:
            name = message.text.split("my name is")[1].strip()
            if name:
                save_user_preference(message.user_id, "name", name.title())
                print(f"Saved name: {name.title()}")
        
        # Get memory context
        context = recall_conversation_context(session_id)
        preferences = get_user_preferences(message.user_id)
        
        
        print(f"📋 Context: {len(context)} messages")
        print(f"💾 Preferences: {preferences}")
        
        
        # Use the memory-enhanced AI
        ai_response = chat_with_memory(message.text, context, preferences)
        
        # Save AI response ✅ FIXED
        memory_system.save_conversation_message(session_id, {
            "role": "assistant", 
            "content": ai_response
        })
        
        print(f"AI Response: {ai_response}")
        return {"reply": ai_response}
   
    except Exception as e:
        print(f"ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Add voice control endpoints
@app.post("/api/voice/start-listening")
def start_voice_listening():
    voice_interface.start_continuous_listening()
    return {"message": "Continuous listening started"}

@app.post("/api/voice/stop-listening")
def stop_voice_listening():
    voice_interface.stop_continuous_listening()
    return {"message": "Continuous listening stopped"}

@app.post("/api/voice/command")
def process_voice_command(command: dict):
    from modules.voice_io import parse_voice_command, execute_voice_command
    
    parsed_command = parse_voice_command(command.get("text", ""))
    response = execute_voice_command(parsed_command)
    
    return {
        "original_command": command.get("text"),
        "parsed_command": parsed_command,
        "response": response
    }

@app.post("/api/voice/speak")
def text_to_speech(text: dict):
    from modules.voice_io import speak
    speak(text.get("text", ""))
    return {"message": "Text spoken"}

# Add this endpoint to your main.py
@app.get("/api/voice/analytics")
def get_voice_analytics_endpoint():
    """Get voice command analytics"""
    return get_voice_analytics()

@app.get("/api/voice/stats")
def get_voice_stats():
    """Get quick voice statistics"""
    analytics = get_voice_analytics()
    return {
        "total_commands": analytics["total_commands"],
        "success_rate": f"{analytics['success_rate']:.1f}%",
        "most_popular_command": list(analytics["popular_commands"].keys())[0] if analytics["popular_commands"] else "None"
    }

# ❌ DELETE this entire function since it's not used:
def extract_user_info(user_id: str, message: str):
    """Simple info extraction without async"""
    message_lower = message.lower()
    
    # Extract name
    name_phrases = ["my name is", "i am ", "i'm called "]
    for phrase in name_phrases:
        if phrase in message_lower:
            name = message_lower.split(phrase)[1].split('.')[0].split('!')[0].strip().title()
            save_user_preference(user_id, "name", name)
            break
    
    # Extract habits
    habits = {
        "exercise": ["exercise", "workout", "gym"],
        "reading": ["read", "book"],
        "coding": ["code", "programming"]
    }
    
    for habit, keywords in habits.items():
        if any(keyword in message_lower for keyword in keywords):
            save_user_habit(user_id, habit, "regular")  # ✅ Fixed syntax