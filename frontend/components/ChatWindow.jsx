// components/ChatWindow.jsx
import { useState, useRef, useEffect } from 'react';
import { StyledMessage } from './StyledMessage';
import { motion, AnimatePresence } from 'framer-motion';

export const ChatWindow = () => {
  const [messages, setMessages] = useState([]);
  const endRef = useRef(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  return (
    <div className="chat-window">
      <AnimatePresence initial={false}>
        {messages.map((msg) => (
          <StyledMessage
            key={msg.id}
            sender={msg.sender}
            content={msg.content}
            timestamp={msg.timestamp}
            status={msg.status}
          />
        ))}
      </AnimatePresence>
      
      {/* Typing indicator */}
      {typing && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="typing-indicator"
        >
          <div className="dot-flashing" />
        </motion.div>
      )}
      
      <div ref={endRef} />
    </div>
  );
};