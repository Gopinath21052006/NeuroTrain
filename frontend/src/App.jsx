import React, { useState, useEffect, useRef } from 'react';
import { FiSend, FiMic, FiSun, FiMoon, FiUser, FiArchive, FiMessageSquare, FiX, FiRefreshCw } from 'react-icons/fi';
import { FaRobot } from 'react-icons/fa';
import { cleanForSpeech } from '../components/speechUtils';
import MarkdownRenderer from '../components/MessageBubble';
import './App.css';
import VoiceSettings from '../components/VoiceSettings';
import { processVoiceCommand } from './modules/voiceCommandParser';

function App() {
  // State declarations
  const [messages, setMessages] = useState([
    {
      id: 1,
      text: "Hello! I'm NeuroTrain AI. How can I help you today?",
      sender: 'ai',
      timestamp: Date.now()
    }
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [darkMode, setDarkMode] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [availableVoices, setAvailableVoices] = useState([]);
  const [selectedVoice, setSelectedVoice] = useState(null);
  const [currentlySpeakingId, setCurrentlySpeakingId] = useState(null);
  const [isAlwaysListening, setIsAlwaysListening] = useState(false);
  const [hotkey, setHotkey] = useState('Space'); // Default hotkey
  const [showMemoryPanel, setShowMemoryPanel] = useState(false);
  const [userMemory, setUserMemory] = useState({
    name: '',
    habits: [],
    conversations: []
  });
  const [memoryLoading, setMemoryLoading] = useState(false);
  const [memoryError, setMemoryError] = useState('');

  // Refs
  const synthRef = useRef(null);
  const messagesEndRef = useRef(null);
  const recognitionRef = useRef(null);

  // Effects
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    document.body.className = darkMode ? 'dark' : 'light';
  }, [messages, darkMode]);

  useEffect(() => {
    const handleKeyDown = (event) => {
      if (event.code === hotkey && !isSpeaking && !loading) {
        setIsAlwaysListening(prev => !prev);
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [hotkey, isSpeaking, loading]);

  useEffect(() => {
    synthRef.current = window.speechSynthesis;
    
    const loadVoices = () => {
      const voices = synthRef.current.getVoices();
      const englishVoices = voices.filter(v => v.lang.includes('en'));
      setAvailableVoices(englishVoices);
      
      if (!selectedVoice && englishVoices.length > 0) {
        setSelectedVoice(englishVoices[0]);
      }
    };

    const timeout = setTimeout(() => {
      loadVoices();
      synthRef.current.onvoiceschanged = loadVoices;
    }, 500);

    return () => {
      clearTimeout(timeout);
      if (synthRef.current) {
        synthRef.current.onvoiceschanged = null;
        synthRef.current.cancel();
      }
    };
  }, []);

  // Fetch user memory
  const fetchUserMemory = async () => {
    setMemoryLoading(true);
    setMemoryError('');
    try {
      const response = await fetch("http://127.0.0.1:8000/get_memory");
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      setUserMemory(data);
    } catch (error) {
      console.error("Error fetching user memory:", error);
      setMemoryError("Failed to load memory. Make sure the backend is running.");
      
      // Set some sample data for testing if backend is not available
      setUserMemory({
        name: 'Gopinath',
        habits: ['Likes photography', 'Enjoys creative projects', 'Interested in art'],
        conversations: [
          'User asked about photo inspiration and artistic passions',
          'Discussed photography techniques and creative ideas',
          'Talked about different art styles and preferences'
        ]
      });
    } finally {
      setMemoryLoading(false);
    }
  };

  useEffect(() => {
    if (showMemoryPanel) {
      fetchUserMemory();
    }
  }, [showMemoryPanel, messages]); // Refresh memory when panel is opened or messages change

  // Format conversation for display
  const formatConversation = (conversation) => {
    if (typeof conversation === 'string') {
      return conversation;
    } else if (Array.isArray(conversation)) {
      return conversation.map(msg => 
        `${msg.sender === 'user' ? 'You' : 'AI'}: ${msg.text}`
      ).join('\n');
    } else if (conversation && typeof conversation === 'object') {
      // Handle object format
      return Object.entries(conversation)
        .map(([key, value]) => `${key}: ${value}`)
        .join('\n');
    }
    
    return 'No conversation data';
  };

  // Speech functions
  const speak = (text, messageId) => {
    if (!synthRef.current || !text) return;
    
    // Cancel any current speech
    synthRef.current.cancel();
    
    const cleanText = cleanForSpeech(text);
    // Create new utterance
    const utterance = new SpeechSynthesisUtterance(cleanText);
    utterance.voice = selectedVoice || synthRef.current.getVoices().find(v => v.lang.includes('en'));
    utterance.rate = 0.95;
    utterance.pitch = 1;

    // Set speaking states
    setCurrentlySpeakingId(messageId);
    setIsSpeaking(true);

    // Cleanup when done
    utterance.onend = utterance.onerror = () => {
      setCurrentlySpeakingId(null);
      setIsSpeaking(false);
    };
    
    synthRef.current.speak(utterance);
  };

  const startListening = () => {
    if (!('webkitSpeechRecognition' in window)) {
      alert('Voice input requires Chrome or Edge');
      return;
    }

    // Stop any existing recognition
    if (recognitionRef.current) {
      recognitionRef.current.stop();
    }

    const recognition = new window.webkitSpeechRecognition();
    recognition.continuous = isAlwaysListening;
    recognition.interimResults = false;
    recognition.lang = 'en-US';

    recognition.onstart = () => {
      setIsListening(true);
      if (!isAlwaysListening) {
      setInput("Listening...");
      }
    };

    recognition.onresult = (e) => {
      const transcript = e.results[e.results.length - 1][0].transcript;

      if (!isAlwaysListening) {
      setIsListening(false);
      setInput("");
      }
      
      processInput(transcript, true);
    };

    recognition.onerror = (e) => {
      console.error('Speech recognition error', e.error);
      if (!isAlwaysListening) {
      setIsListening(false);
      setInput("");
      }
    };

    recognition.onend = () => {
      if (isAlwaysListening && !isSpeaking && !loading) {
        // Auto-restart in continuous mode
        setTimeout(() => recognition.start(), 500);
      } else {
      setIsListening(false);
      setInput("");
      }
    };

    recognitionRef.current = recognition;
    recognition.start();
  };

  // Message processing
  const processInput = async (text, isVoice = false) => {
    if (!text.trim() || loading) return;
    
    // Add user message
    const userMessage = {
      id: Date.now(),
      text: text,
      sender: 'user',
      timestamp: Date.now(),
      isVoiceInput: isVoice
    };

    setMessages(prev => [...prev, userMessage]);
    if (!isVoice) setInput('');
    setLoading(true);

    try {
      if (isVoice) {
        try {
          const commandResult = await processVoiceCommand(text);
          
          if (commandResult.type !== 'CHAT') {
            // Command was successfully executed
            const aiMessage = {
              id: Date.now() + 1,
              text: commandResult.message,
              sender: "ai",
              timestamp: Date.now(),
              shouldSpeak: isVoice,
              isCommand: true
            };
            
            setMessages(prev => [...prev, aiMessage]);
            
            if (isVoice && commandResult.tts_response) {
              speak(commandResult.tts_response, aiMessage.id);
            }
            
            setLoading(false);
            return;
          }
        } catch (error) {
          console.log('Voice command processing failed, falling back to chat:', error);
          // Continue to regular chat processing
        }
      }

      // Fall back to regular chat processing
      const response = await fetch("http://127.0.0.1:8000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: text }),
      });

      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);

      const data = await response.json();
      const aiReply = data.reply;

      const aiMessage = {
        id: Date.now(),
        text: aiReply,
        sender: 'ai',
        timestamp: Date.now(),
        shouldSpeak: isVoice
      };

      setMessages(prev => [...prev, aiMessage]);

      if (isVoice) {
        speak(aiReply, aiMessage.id);
      }

    } catch (err) {
      const errorMessage = err.name === 'AbortError' 
        ? "Request timed out" 
        : `Error: ${err.message}`;
      
      setMessages(prev => [...prev, {
        id: Date.now(),
        text: errorMessage,
        sender: 'ai',
        timestamp: Date.now(),
        isError: true
      }]);
    } finally {
      setLoading(false);
    }
  };

  const sendMessage = async () => {
    await processInput(input, false);
  };

  return (
    <div className={`app ${darkMode ? 'dark' : 'light'}`}>
      <header>
        <div className='header-content'>
          <FaRobot className='header-icon' />
          <h1>NeuroTrain</h1>
        </div>
        <div className="header-controls">
          <button 
            onClick={() => setShowMemoryPanel(!showMemoryPanel)}
            className={`memory-button ${showMemoryPanel ? 'active' : ''}`}
            title="Show Memory"
          >
            <FiArchive />
          </button>
          <select 
            onChange={(e) => {
              const index = parseInt(e.target.value);
              if (index >= 0 && index < availableVoices.length) {
                setSelectedVoice(availableVoices[index]);
              } else {
                setSelectedVoice(null);
              }
            }}
            value={availableVoices.findIndex(v => v === selectedVoice)}
            disabled={isSpeaking}
            className="voice-selector"
          >
            <option value={-1}>Default Voice</option>
            {availableVoices.map((voice, index) => (
              <option key={index} value={index}>
                {voice.name} ({voice.lang})
              </option>
            ))}
          </select>
          <button 
            onClick={() => setDarkMode(!darkMode)}
            className="theme-toggle"
            aria-label="Toggle dark mode"
          >
            {darkMode ? <FiSun /> : <FiMoon />}
          </button>
            <button 
            onClick={() => setIsAlwaysListening(!isAlwaysListening)}
            className={`continuous-button ${isAlwaysListening ? 'active' : ''}`}
            disabled={isSpeaking}
            >
            {isAlwaysListening ? '🔴 Always On' : '⚪ Always Off'}
            </button>
          <VoiceSettings 
            isAlwaysListening={isAlwaysListening}
            setIsAlwaysListening={setIsAlwaysListening}
            hotkey={hotkey}
            setHotkey={setHotkey}
            availableVoices={availableVoices}
            selectedVoice={selectedVoice}
            setSelectedVoice={setSelectedVoice}
          />
        </div>
      </header>

      <div className="main-content">
        {/* Memory Panel */}
        {showMemoryPanel && (
          <div className="memory-panel">
            <div className="memory-header">
              <h2>User Memory</h2>
              <div className="memory-controls">
                <button 
                  onClick={fetchUserMemory}
                  className="refresh-memory"
                  title="Refresh Memory"
                  disabled={memoryLoading}
                >
                  <FiRefreshCw className={memoryLoading ? 'spinning' : ''} />
                </button>
                <button 
                  onClick={() => setShowMemoryPanel(false)}
                  className="close-panel"
                >
                  <FiX />
                </button>
              </div>
            </div>
            
            {memoryError && (
              <div className="memory-error">
                {memoryError}
              </div>
            )}
            
            {memoryLoading ? (
              <div className="memory-loading">Loading memory...</div>
            ) : (
              <>
                <div className="memory-section">
                  <div className="section-header">
                    <FiUser className="section-icon" />
                    <h3>Basic Info</h3>
                  </div>
                  <div className="memory-item">
                    <span className="memory-label">Name:</span>
                    <span className="memory-value">{userMemory.name || 'Not specified'}</span>
                  </div>
                </div>
                
                <div className="memory-section">
                  <div className="section-header">
                    <FiArchive className="section-icon" />
                    <h3>Habits & Preferences</h3>
                  </div>
                  {userMemory.habits && userMemory.habits.length > 0 ? (
                    <ul className="habits-list">
                      {userMemory.habits.map((habit, index) => (
                        <li key={index} className="habit-item">{habit}</li>
                      ))}
                    </ul>
                  ) : (
                    <p className="no-data">No habits recorded yet</p>
                  )}
                </div>
                
                <div className="memory-section">
                  <div className="section-header">
                    <FiMessageSquare className="section-icon" />
                    <h3>Recent Conversations</h3>
                  </div>
                  {userMemory.conversations && userMemory.conversations.length > 0 ? (
                    <div className="conversations-list">
                      {userMemory.conversations.slice(0, 5).map((conv, index) => {
                        const formattedConv = formatConversation(conv);
                        return (
                          <div key={index} className="conversation-item">
                            <div className="conversation-header">
                              <span className="conversation-number">Conversation #{index + 1}</span>
                            </div>
                            <p className="conversation-preview">
                              {formattedConv.length > 100 
                                ? `${formattedConv.substring(0, 100)}...` 
                                : formattedConv
                              }
                            </p>
                          </div>
                        );
                      })}
                    </div>
                  ) : (
                    <p className="no-data">No conversation history yet</p>
                  )}
                </div>
              </>
            )}
          </div>
        )}

        <div className={`chat-window ${showMemoryPanel ? 'with-memory-panel' : ''}`}>
          <div className='messages'>
            {messages.map((msg) => (
              <div key={msg.id} className={`message ${msg.sender} ${msg.isError ? 'error' : ''}`}>
                <div className="message-avatar">
                  {msg.sender === 'ai' ? (
                    <FaRobot className="ai-avatar" />
                  ) : (
                    <div className="user-avatar">U</div>
                  )}
                </div>
                <div className="message-content">
                  {msg.isVoiceInput && (
                    <div className="voice-indicator">🎤 Voice</div>
                  )}
                  <div className="message-text">
                    <MarkdownRenderer content={msg.text} />
                  </div>
                  {msg.sender === 'ai' && currentlySpeakingId === msg.id && (
                    <button 
                      onClick={() => {
                        synthRef.current.cancel();
                        setCurrentlySpeakingId(null);
                        setIsSpeaking(false);
                      }}
                      className="stop-speech-button"
                      aria-label="Stop speech playback"
                    >
                      ⏹️ Stop
                    </button>
                  )}
                  <div className="message-timestamp">
                    {new Date(msg.timestamp).toLocaleTimeString([], {
                      hour: '2-digit',
                      minute: '2-digit'
                    })}
                  </div>
                </div>
              </div>
            ))}
            
            {loading && (
              <div className="message ai">
                <div className="message-avatar">
                  <FaRobot className="ai-avatar" />
                </div>
                <div className="message-content">
                  <div className="typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          <div className="input-area">
            <form onSubmit={(e) => { e.preventDefault(); sendMessage(); }}>
              <button 
                type="button"
                onClick={startListening}
                className={`mic-button ${isListening ? 'listening' : ''}`}
                disabled={isSpeaking || loading}
              >
                <FiMic />
              </button>
              <input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder={isListening ? "Listening..." : "Type or speak..."}
                disabled={loading || isSpeaking}
              />
              <button
                type="submit"
                disabled={loading || !input.trim() || isSpeaking}
              >
                <FiSend />
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;