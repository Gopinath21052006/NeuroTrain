// components/StyledMessage.jsx
import { motion } from 'framer-motion';
import { styled } from '@emotion/styled';
import { Check, Clock, AlertCircle } from 'lucide-react';

const MessageContainer = styled(motion.div)`
  max-width: 85%;
  padding: 1.25rem;
  border-radius: 1.125rem;
  position: relative;
  line-height: 1.7;
  font-size: 1.05rem;
  box-shadow: 0 2px 12px rgba(0,0,0,0.08);
  
  ${({ sender }) => sender === 'ai' ? `
    background: rgba(255,255,255,0.03);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(255,255,255,0.1);
    align-self: flex-start;
    border-bottom-left-radius: 4px;
  ` : `
    background: linear-gradient(135deg, #6e8efb, #a777e3);
    color: white;
    align-self: flex-end;
    border-bottom-right-radius: 4px;
  `}
`;

const MessageContent = styled.div`
  p {
    margin-bottom: 1em;
    &:last-child { margin-bottom: 0; }
  }
  
  strong {
    font-weight: 650;
    background: linear-gradient(90deg, #ff8a00, #da1b60);
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
  }
  
  em {
    font-style: italic;
    position: relative;
    &::after {
      content: '';
      position: absolute;
      bottom: -2px;
      left: 0;
      width: 100%;
      height: 1px;
      background: currentColor;
      opacity: 0.3;
    }
  }
  
  ul, ol {
    padding-left: 1.75rem;
    margin: 0.8rem 0;
  }
  
  li {
    position: relative;
    margin-bottom: 0.5rem;
    &::marker {
      color: var(--accent-color);
    }
  }
  
  a {
    color: var(--link-color);
    text-decoration: none;
    position: relative;
    transition: all 0.3s ease;
    
    &::after {
      content: '';
      position: absolute;
      bottom: -2px;
      left: 0;
      width: 100%;
      height: 1px;
      background: currentColor;
      transform: scaleX(0);
      transform-origin: right;
      transition: transform 0.4s cubic-bezier(0.65, 0, 0.35, 1);
    }
    
    &:hover::after {
      transform: scaleX(1);
      transform-origin: left;
    }
  }
`;

const StatusIndicator = styled.div`
  position: absolute;
  bottom: -18px;
  right: 8px;
  font-size: 0.75rem;
  display: flex;
  align-items: center;
  gap: 4px;
  color: var(--text-tertiary);
`;

export const StyledMessage = ({ sender, content, timestamp, status }) => {
  return (
    <MessageContainer
      sender={sender}
      initial={{ opacity: 0, y: 20, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ 
        type: 'spring',
        damping: 25,
        stiffness: 300
      }}
    >
      <MessageContent dangerouslySetInnerHTML={{ __html: content }} />
      
      <div className="flex items-center justify-between mt-2">
        <span className="text-xs opacity-60">
          {new Date(timestamp).toLocaleTimeString([], { 
            hour: '2-digit', 
            minute: '2-digit' 
          })}
        </span>
        
        <StatusIndicator>
          {status === 'sending' && <Clock size={14} />}
          {status === 'delivered' && <Check size={14} />}
          {status === 'error' && <AlertCircle size={14} />}
        </StatusIndicator>
      </div>
    </MessageContainer>
  );
};