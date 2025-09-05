# 📁 modules/voice_interface.py
from modules.voice_io import continuous_listen, speak, listen, parse_voice_command, execute_voice_command
import threading

class VoiceInterface:
    def __init__(self):
        self.is_listening = False
        self.listening_thread = None
        self.callback = None
    
    def start_continuous_listening(self, callback=None):
        """Start continuous listening in a separate thread"""
        if self.is_listening:
            print("Already listening")
            return
        
        self.is_listening = True
        self.callback = callback
        self.listening_thread = threading.Thread(
            target=self._listening_loop,
            daemon=True
        )
        self.listening_thread.start()
        print("✅ Continuous listening started")
    
    def _listening_loop(self):
        """Main listening loop"""
        while self.is_listening:
            try:
                text = listen(timeout=10, phrase_time_limit=5)
                
                if text and "hey neurotrain" in text.lower():
                    print("✅ Wake word detected")
                    speak("Yes, I'm listening", is_command_response=True)
                    
                    # Listen for command
                    command_text = listen(timeout=8, phrase_time_limit=15)
                    if command_text:
                        command = parse_voice_command(command_text)
                        response = execute_voice_command(command)
                        
                        speak(response, is_command_response=True)
                        
                        if self.callback:
                            self.callback(command_text, response)
                            
            except Exception as e:
                print(f"Listening error: {e}")
                continue
    
    def stop_continuous_listening(self):
        """Stop continuous listening"""
        self.is_listening = False
        print("🛑 Continuous listening stopped")
    
    def process_single_command(self):
        """Listen for and process a single command"""
        print("🎤 Say your command...")
        text = listen(timeout=10, phrase_time_limit=15)
        if text:
            command = parse_voice_command(text)
            response = execute_voice_command(command)
            speak(response, is_command_response=True)
            return response
        return None

# Global instance
voice_interface = VoiceInterface()