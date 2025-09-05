from pydantic import BaseModel
from typing import Optional, Dict, Any

class VoiceCommandRequest(BaseModel):
    text: str
    session_id: Optional[str] = None

class ParsedCommandResponse(BaseModel):
    intent: str
    action: str
    parameters: Dict[str, Any]
    original_text: str
    confidence: float = 1.0

class CommandExecutionResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    tts_response: str