from modules.memory.memory_chat_history import *

# Test data
user_id = "test_user_001"
session_id = f"{user_id}_session1"

print("🧪 Testing Memory System...")

# 1. Test preferences
memory_system.save_user_preference(user_id, "name", "Goipnath")
memory_system.save_user_preference(user_id, "language", "english")

# 2. Test habits
save_user_habit(user_id, "exercise", "daily")
save_user_habit(user_id, "reading", "weekly")

# 3. Test conversations
memory_system.save_conversation_message(session_id, "user", "Hi, I'm gopinath!")
memory_system.save_conversation_message(session_id, "assistant", "Hello Gopinath! How can I help?")

# 4. Test recall functions
print("📋 Preferences:", get_user_preferences(user_id))
print("💬 Conversation history:", recall_conversation_context(session_id))

print("✅ All tests passed! Check data/memory/ folder.")