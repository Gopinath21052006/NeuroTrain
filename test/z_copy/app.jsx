// frontend\src\App.jsx
import React, { useEffect, useState, useRef } from 'react';
import { FiSend, FiMic, FiSun, FiMoon } from 'react-icons/fi';
import {FaRobot } from 'react-icons/fa';
import './App.css';
// import FormattedMessage from '../components/StyledMessage';
// import { StyledMessage } from '../components/StyledMessage';

function App() {
  const [messages, setMessages] = useState([
    {
      id: 1,
      text: "Hello! I'm NeuroTrain AI. How can I help you today?",
      sender: 'ai',
      timestamp: Date.now()
    }
  ]);  // Chat history 

  const [input, setInput] = useState("");           // User input field 
  const [loading, setLoading] = useState(false);    // API call status 
  const [darkMode, setDarkMode] = useState(false);  // Theme
  const [isListening, setIsListening] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [availableVoices, setAvailableVoices] = useState([]);
  const [selectedVoice, setSelectedVoice] = useState(null);
  const synthRef = useRef(null);
  const messagesEndRef = useRef(null);              // For auto - scrolling 
  const recognitionRef = useRef(null); 


  // Auto-scroll and Theme Effect 
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    document.body.className = darkMode ? 'dark' : 'light';
  }, [messages, darkMode]);

  // speech 
  useEffect(() => {
  synthRef.current = window.speechSynthesis;
  
  const loadVoices = () => {
    const voices = synthRef.current.getVoices();
    const englishVoices = voices.filter(v => v.lang.includes('en'));
    setAvailableVoices(englishVoices);
    
    // Auto-select first English voice if none selected
    if (!selectedVoice && englishVoices.length > 0) {
      setSelectedVoice(englishVoices[0]);
    }
  };

  // Chrome needs this timeout
  const timeout = setTimeout(() => {
    loadVoices();
    synthRef.current.onvoiceschanged = loadVoices;
  }, 500);

  return () => {
    clearTimeout(timeout);
    synthRef.current.onvoiceschanged = null;
    synthRef.current.cancel();
  };
  },[]);

  //voice Function 
  const speak = (text) =>{
  if (!synthRef.current || !text) return;

  synthRef.current.cancel(); // Stop any ongoing speech

  const utterance = new SpeechSynthesisUtterance(text);
  utterance.voice = selectedVoice || synthRef.current.getVoices().find(v => v.lang.includes('en'));
  utterance.rate = 0.95;
  utterance.pitch = 1;

  setIsSpeaking(true);
  utterance.onend = utterance.onerror = () => setIsSpeaking(false);
  
    synthRef.current.speak(utterance);
  };

   const startListening = () => {
    if (!('webkitSpeechRecognition' in window)) {
      alert('Voice input requires Chrome or Edge');
      return;
    }

    const recognition = new window.webkitSpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = 'en-US';

    recognition.onstart = () => {
      setIsListening(true);
      setInput("Listening....")
    };
    
    recognition.onresult = async (e) => {
      const transcript = e.results[0][0].transcript;
      setInput(transcript);
      await processVoiceInput(transcript);
    };


    recognition.onerror = (e) => {
      console.error('Speech recognition error', e.error);
      setIsListening(false);
    };

    recognition.onend = () => setIsListening(false);

    recognitionRef.current = recognition;
    recognition.start();
  };
  
  const processVoiceInput = async (transcript) =>{
    const newMessage = {
      id: Date.now(),
      text : transcript,
      sender : 'user',
      timestamp : Date.now(),
      isVoiceInput : true // mark as voice input

    }
    setMessages(prev => [...prev, newMessage]);
  };


  // Sending Messsages  
  const sendMessage = async () => {
    if (!input.trim() || loading) return; // Prevent empty/duplicate sends
    
    // Add user message
    const newMessage = { 
      id: Date.now(),
      text: input,
      sender: 'user',
      timestamp: Date.now()
    };

    // 1) Add user message immediately 
    setMessages(prev => [...prev, newMessage]);
    setInput('');
    setLoading(true);

    try {

      // 2) Call backend API with timeout 
      // it can be detele if it make slow 
      const controller = new AbortController();
      const timeoutID = setTimeout(()=> controller.abort(), 10000) 

      const response = await fetch("http://localhost:8000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: input }),
        // signal : controller.signal only works if you call controller.abort() manually
      });

      clearTimeout(timeoutID);

      if(!response.ok){
        throw new Error(`HTTP error! status : ${response.status}`);
      }

      // 3) Process successful response
      const data = await response.json();
      const aiReply = data.reply; 

       //TEST frontend get the result 
        console.log("data from Backend : ", data.reply)


      setMessages(prev => [...prev, {
        text: "",
        sender: 'ai',
        timestamp: data.timestamp || Date.now() ,
        status : 'delivered'
      }]);
      setLoading(false)
      // Typing animation
      let displayedText = "";
      
   
      for (let i = 0; i < aiReply.length; i++) {
        displayedText += aiReply[i];
        await new Promise(resolve => setTimeout(resolve, 20)); // speed (ms per char)
        setMessages(prev => {
          const newMessages = [...prev];
          newMessages[newMessages.length - 1] = {
            ...newMessages[newMessages.length - 1],
            text: displayedText
          };
          return newMessages;
        })}
        
           speak(data.reply)
       




    } catch (err) {
      // 4) Enhanced error handling
    let errorMessage = "Connection error. Please try again.";
    
    if (err.name === 'AbortError') {
      errorMessage = "Request timed out. Please try again.";
    } else if (err.message.includes('HTTP error')) {
      errorMessage = `Server error: ${err.message}`;
    }

    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={`app ${darkMode ? 'dark' : 'light'}`}>
      {/* Header with Theme Toggle */}
      <header>
        <div className='header-content'>
          <FaRobot className='header-icon' />
        <h1>NeuroTrain</h1>
        </div>
        <button 
          onClick={() => setDarkMode(!darkMode)}
          className="theme-toggle"
          aria-label="Toggle dark mode"
        >
          {darkMode ? <FiSun /> : <FiMoon />}
        </button>

        {/* Add inside your <header> */}
<select 
  onChange={(e) => setSelectedVoice(availableVoices[e.target.value] || null)}
  value={availableVoices.findIndex(v => v === selectedVoice)}
  disabled={isSpeaking}
  className="voice-selector"
>
  <option value="-1">Default Voice</option>
  {availableVoices.map((voice, index) => (
    <option key={index} value={index}>
      {voice.name} ({voice.lang})
    </option>
  ))}
</select>


      </header>

      {/* Chat Window */}

      <div className="chat-window">
        <div className='messages'>
          {messages.map((msg) => (
          <div 
            key={msg.id} 
            className={`message ${msg.sender}`}
          >
            {/*it can be detele */}
              <div className="message-avatar">
                {msg.sender === 'ai' ? (
                  <FaRobot className="ai-avatar" />
                ) : (
                  <div className="user-avatar">U</div>
                )}
              </div>


              <div className="message-content">
                <div className="message-text">{msg.text}</div>
                <div className="message-timestamp">
                  {new Date(msg.timestamp).toLocaleTimeString([], {
                    hour: '2-digit',
                    minute: '2-digit'
                  })}
                </div>
              </div>
            </div>
          ))}

        {/* Loading indicator */}
          
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

        {/* Input Area */}

        <div className="input-area">
          <form onSubmit={(e) => { e.preventDefault(); sendMessage(); }}>
  <button
    type="button"
                        onClick={startListening}
                        className={`mic-button ${isListening ? 'listening' : ''}`}
                        disabled={isSpeaking}
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
  );
}

export default App;