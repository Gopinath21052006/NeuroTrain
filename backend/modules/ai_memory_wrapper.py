# backend/modules/ai_memory_wrapper.py
from modules.ai_chat import chat_with_ai
from typing import List, Dict, Any, Optional

def chat_with_memory(user_input: str, context: Optional[List[Dict]] = None, preferences: Optional[Dict] = None) -> str:
    """
    Enhanced AI chat with memory context integration
    """
    try:
        # Build system prompt with user preferences
        system_prompt = "You are a helpful AI assistant. "
        
        # Add user preferences if available
        user_name = None
        if preferences and preferences.get('preferences'):
            user_prefs = preferences['preferences']
            if user_prefs.get('name'):
                user_name = user_prefs['name']
                system_prompt += f"The user's name is {user_name}. "
            
            # Add other preferences
            other_prefs = {k: v for k, v in user_prefs.items() if k != 'name'}
            if other_prefs:
                prefs_text = ", ".join([f"{k}: {v}" for k, v in other_prefs.items()])
                system_prompt += f"User preferences: {prefs_text}. "
        
        # Build conversation history
        conversation_history = ""
        if context:
            # Filter to last 5 messages for context
            recent_messages = context[-5:]
            for msg in recent_messages:
                role = "User" if msg.get('role') == 'user' else "Assistant"
                content = msg.get('content', '')
                if content.strip():
                    conversation_history += f"{role}: {content}\n"
        
        # Construct the final prompt
        if conversation_history.strip():
            final_prompt = f"""{system_prompt}

Here is the recent conversation history:
{conversation_history.strip()}

Current user message: {user_input}

Please respond naturally while considering the conversation history and user information."""
        else:
            final_prompt = f"""{system_prompt}

User says: {user_input}

Please respond helpfully."""
        
        # Add personalization if we know the user's name
        if user_name and user_name.lower() not in user_input.lower():
            final_prompt += f" Remember to address the user as {user_name} if appropriate."
        
        print(f"🧠 Memory Context Enabled")
        print(f"📋 User: {user_name or 'Unknown'}")
        print(f"💬 Context messages: {len(context) if context else 0}")
        print(f"📝 Final prompt length: {len(final_prompt)} characters")
        
        # Call the original AI function with enhanced prompt
        return chat_with_ai(final_prompt)
        
    except Exception as e:
        print(f"❌ Memory wrapper error: {e}")
        # Fallback to basic AI if memory fails
        return chat_with_ai(user_input)


# Alternative simpler version if the above doesn't work
def chat_with_memory_simple(user_input: str, context: Optional[List[Dict]] = None, preferences: Optional[Dict] = None) -> str:
    """
    Simple memory integration for testing
    """
    try:
        enhanced_prompt = user_input
        
        # Add user name if available
        if preferences and preferences.get('preferences', {}).get('name'):
            name = preferences['preferences']['name']
            if name.lower() not in user_input.lower():
                enhanced_prompt = f"User {name} says: {user_input}"
        
        # Add recent context (last 2 exchanges)
        if context and len(context) >= 2:
            last_exchange = context[-2:]  # Get last user + assistant pair
            context_text = "\n".join([f"{msg.get('role', 'unknown')}: {msg.get('content', '')}" 
                                    for msg in last_exchange])
            enhanced_prompt = f"Previous: {context_text}\n\nCurrent: {enhanced_prompt}"
        
        print(f"🧠 Simple memory - Enhanced prompt: {enhanced_prompt}")
        return chat_with_ai(enhanced_prompt)
        
    except Exception as e:
        print(f"❌ Simple memory error: {e}")
        return chat_with_ai(user_input)


# For testing and debugging
def debug_memory_context(user_input: str, context: Optional[List[Dict]] = None, preferences: Optional[Dict] = None):
    """
    Debug function to see what memory context contains
    """
    print("=" * 50)
    print("🧠 MEMORY DEBUG INFO")
    print("=" * 50)
    
    print(f"📝 User input: {user_input}")
    print(f"📋 Preferences: {preferences}")
    print(f"💬 Context messages: {len(context) if context else 0}")
    
    if context:
        print("\n📜 Conversation context:")
        for i, msg in enumerate(context[-5:]):  # Show last 5 messages
            print(f"  {i+1}. {msg.get('role', 'unknown')}: {msg.get('content', '')[:100]}...")
    
    print("=" * 50)
    
    # Test both approaches
    result1 = chat_with_memory(user_input, context, preferences)
    print(f"🧠 Enhanced result: {result1[:100]}...")
    
    result2 = chat_with_memory_simple(user_input, context, preferences)
    print(f"🔧 Simple result: {result2[:100]}...")
    
    return result1  # Return enhanced version by default


# For backward compatibility
def simple_chat_with_ai(user_input: str) -> str:
    """Original function signature for compatibility"""
    return chat_with_ai(user_input)


# Test function
if __name__ == "__main__":
    # Test the memory wrapper
    test_context = [
        {"role": "user", "content": "Hello, my name is Gopika"},
        {"role": "assistant", "content": "Nice to meet you Gopika!"}
    ]
    
    test_preferences = {
        "preferences": {
            "name": "Gopika",
            "language": "english"
        }
    }
    
    test_input = "What is my name?"
    
    print("Testing memory wrapper...")
    result = chat_with_memory(test_input, test_context, test_preferences)
    print(f"Result: {result}")