# backend/modules/simple_parser.py
import re
from typing import Dict, Any

def _clean_text(text: str) -> str:
    """Clean and normalize text for parsing"""
    return text.strip().lower()

def parse_command(text: str) -> Dict[str, Any]:
    """
    Parse a user text into an action dict.
    Returns something like:
    { "action": "task_add", "params": {"title": "buy milk"} }
    or { "action": "chat", "params": {"message": "..."} }
    """
    if not text or len(text.strip()) < 2:
        return {"action": "chat", "params": {"message": text}}
    
    t = _clean_text(text)

    # 1) Task add patterns
    m = re.search(r'(?:add|create|put)\s+(?:a\s+)?(?:task|reminder)\s+(?:to\s)?(.+)', t)
    if m:
        title = m.group(1).strip()
        return {"action": "task_add", "params": {"title": title}}

    m = re.search(r'remind me to (.+)', t)
    if m:
        title = m.group(1).strip()
        return {"action": "task_add", "params": {"title": title}}

    # 2) Mark task done / delete
    m = re.search(r'(?:done|complete|finish|remove|delete)\s+(?:task\s+)?(.+)', t)
    if m:
        title = m.group(1).strip()
        return {"action": "task_delete", "params": {"title": title}}

    # 3) List tasks
    if re.search(r'(?:show|list|what).*task', t):
        return {"action": "task_list", "params": {}}

    # 4) System stats
    if re.search(r'\b(cpu|ram|memory|disk|battery|usage|system status|stats)\b', t):
        return {"action": "system_stats", "params": {}}

    # 5) Open application
    m = re.search(r'open (?:the )?(.+)', t)
    if m:
        app_name = m.group(1).strip()
        app_name = re.sub(r' (please|now|app|application)$', '', app_name).strip()
        return {"action": "open_app", "params": {"app": app_name}}

    # 6) Schedule reminder
    m = re.search(r'(?:set|schedule)\s+(?:a\s+)?(?:reminder|alarm)\s+(?:for\s+)?(.+?)\s+(?:to|about)?\s*(.+)?', t)
    if m:
        time_part = m.group(1).strip()
        message_part = (m.group(2) or "").strip()
        return {"action": "schedule", "params": {"time": time_part, "message": message_part or "Reminder"}}

    # 7) Default to chat
    return {"action": "chat", "params": {"message": text}}