import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional

class MemoryChatHistory:
    def __init__(self, storage_path: str = "data/memory"):
        """
        Initialize memory system with JSON storage
        """
        self.storage_path = storage_path
        self.users_file = os.path.join(storage_path, "users.json")
        self.habits_file = os.path.join(storage_path, "habits.json")
        self.conversations_file = os.path.join(storage_path, "conversations.json")
        
        # Create storage directory if it doesn't exist
        os.makedirs(storage_path, exist_ok=True)
        
        # Initialize JSON files if they don't exist
        self._initialize_json_files()
    
    def _initialize_json_files(self):
        """Initialize empty JSON files if they don't exist"""
        files = {
            self.users_file: {},
            self.habits_file: {},
            self.conversations_file: {}
        }
        
        for file_path, default_data in files.items():
            if not os.path.exists(file_path):
                with open(file_path, 'w') as f:
                    json.dump(default_data, f, indent=2)
    
    def _read_json(self, file_path: str) -> Dict:
        """Read JSON file safely"""
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def _write_json(self, file_path: str, data: Dict):
        """Write to JSON file safely"""
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def get_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """
        Return stored preferences for a user
        
        Args:
            user_id: Unique identifier for the user
            
        Returns:
            Dictionary containing user preferences
        """
        users_data = self._read_json(self.users_file)
        return users_data.get(user_id, {})
    
    def save_user_preference(self, user_id: str, preference_type: str, value: Any):
        """
        Save user preference into memory
        
        Args:
            user_id: Unique identifier for the user
            preference_type: Type of preference (e.g., 'name', 'favorite_color')
            value: Value of the preference
        """
        users_data = self._read_json(self.users_file)
        
        if user_id not in users_data:
            users_data[user_id] = {
                'preferences': {},
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
        
        users_data[user_id]['preferences'][preference_type] = value
        users_data[user_id]['updated_at'] = datetime.now().isoformat()
        
        self._write_json(self.users_file, users_data)
    
    def save_user_habit(self, user_id: str, habit: str, frequency: str):
        """
        Save user habit into memory
        
        Args:
            user_id: Unique identifier for the user
            habit: The habit to save (e.g., 'exercise', 'reading')
            frequency: Frequency of the habit (e.g., 'daily', 'weekly')
        """
        habits_data = self._read_json(self.habits_file)
        
        if user_id not in habits_data:
            habits_data[user_id] = {}
        
        habits_data[user_id][habit] = {
            'frequency': frequency,
            'last_updated': datetime.now().isoformat()
        }
        
        self._write_json(self.habits_file, habits_data)
    
    def get_user_habits(self, user_id: str) -> Dict[str, Any]:
        """
        Get all habits for a user
        
        Args:
            user_id: Unique identifier for the user
            
        Returns:
            Dictionary of user habits
        """
        habits_data = self._read_json(self.habits_file)
        return habits_data.get(user_id, {})
    
    def save_conversation_message(self, session_id: str, message: Dict[str, Any]):
        """
        Save a conversation message
        
        Args:
            session_id: Unique session identifier
            message: Dictionary containing message data with keys like:
                    'role' (user/assistant), 'content', 'timestamp'
        """
        conversations_data = self._read_json(self.conversations_file)
        
        if session_id not in conversations_data:
            conversations_data[session_id] = {
                'messages': [],
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
        
        # Add timestamp if not provided
        if 'timestamp' not in message:
            message['timestamp'] = datetime.now().isoformat()
        
        conversations_data[session_id]['messages'].append(message)
        conversations_data[session_id]['updated_at'] = datetime.now().isoformat()
        
        # Keep only last 50 messages to prevent file from growing too large
        if len(conversations_data[session_id]['messages']) > 50:
            conversations_data[session_id]['messages'] = conversations_data[session_id]['messages'][-50:]
        
        self._write_json(self.conversations_file, conversations_data)
    
    def recall_conversation_context(self, session_id: str, max_messages: int = 10) -> List[Dict[str, Any]]:
        """
        Return previous chat messages for a session
        
        Args:
            session_id: Unique session identifier
            max_messages: Maximum number of messages to return
            
        Returns:
            List of previous chat messages
        """
        conversations_data = self._read_json(self.conversations_file)
        
        if session_id not in conversations_data:
            return []
        
        messages = conversations_data[session_id]['messages']
        return messages[-max_messages:]
    
    def get_user_name(self, user_id: str) -> Optional[str]:
        """
        Helper function to get user's name from preferences
        
        Args:
            user_id: Unique identifier for the user
            
        Returns:
            User's name or None if not found
        """
        preferences = self.get_user_preferences(user_id)
        return preferences.get('preferences', {}).get('name')
    
    def get_all_user_data(self, user_id: str) -> Dict[str, Any]:
        """
        Get all stored data for a user (preferences, habits, conversation summaries)
        
        Args:
            user_id: Unique identifier for the user
            
        Returns:
            Dictionary containing all user data
        """
        return {
            'preferences': self.get_user_preferences(user_id),
            'habits': self.get_user_habits(user_id),
            'recent_conversations': self.get_recent_sessions(user_id)
        }
    
    def get_recent_sessions(self, user_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get recent conversation sessions for a user
        
        Args:
            user_id: User identifier
            limit: Number of recent sessions to return
            
        Returns:
            List of recent session summaries
        """
        conversations_data = self._read_json(self.conversations_file)
        user_sessions = []
        
        for session_id, session_data in conversations_data.items():
            if session_id.startswith(f"{user_id}_"):
                user_sessions.append({
                    'session_id': session_id,
                    'last_updated': session_data.get('updated_at'),
                    'message_count': len(session_data.get('messages', []))
                })
        
        # Sort by most recent and limit results
        user_sessions.sort(key=lambda x: x.get('last_updated', ''), reverse=True)
        return user_sessions[:limit]


# Global instance for easy import
memory_system = MemoryChatHistory()

# Convenience functions using the global instance
def get_user_preferences(user_id: str) -> Dict[str, Any]:
    """Return stored preferences for a user"""
    return memory_system.get_user_preferences(user_id)

def save_user_habit(user_id: str, habit: str, frequency: str):
    """Save user habit into memory"""
    memory_system.save_user_habit(user_id, habit, frequency)

def recall_conversation_context(session_id: str, max_messages: int = 10) -> List[Dict[str, Any]]:
    """Return previous chat messages for a session"""
    return memory_system.recall_conversation_context(session_id, max_messages)

def save_conversation_message(session_id: str, message: Dict[str, Any]):
    """Save a conversation message"""
    memory_system.save_conversation_message(session_id, message)

def save_user_preference(user_id: str, preference_type: str, value: Any):
    """Save user preference"""
    memory_system.save_user_preference(user_id, preference_type, value)
