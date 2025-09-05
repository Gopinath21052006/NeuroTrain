import { useEffect, useRef } from 'react';

const useWakeWordDetector = (onWakeWord, isEnabled = true) => {
  const recognitionRef = useRef(null);

  useEffect(() => {
    if (!isEnabled) {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
      return;
    }

    if (!('webkitSpeechRecognition' in window)) {
      console.log('Wake word detection requires Chrome or Edge');
      return;
    }

    const recognition = new window.webkitSpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = 'en-US';

    recognition.onresult = (event) => {
      let transcript = '';
      for (let i = event.resultIndex; i < event.results.length; i++) {
        transcript += event.results[i][0].transcript;
      }
      
      if (transcript.toLowerCase().includes('hey neurotrain')) {
        onWakeWord();
        recognition.stop();
      }
    };

    recognition.onerror = (event) => {
      console.error('Wake word recognition error:', event.error);
    };

    recognition.onend = () => {
      if (isEnabled) {
        setTimeout(() => recognition.start(), 500);
      }
    };

    recognitionRef.current = recognition;
    recognition.start();

    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
    };
  }, [isEnabled, onWakeWord]);

  return null;
};

export default useWakeWordDetector;