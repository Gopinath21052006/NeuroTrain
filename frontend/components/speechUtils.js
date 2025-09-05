// frontend/utils/speechUtils.js
export const cleanForSpeech = (text) => {
  if (!text) return '';
  
  return text
    .replace(/\*\*/g, '')       // Remove bold **
    .replace(/\*/g, '')        // Remove italics *
    .replace(/_/g, '')         // Remove underscores _
    .replace(/`/g, '')         // Remove code `
    .replace(/#/g, '')         // Remove headers #
    .replace(/~~/g, '')        // Remove strikethrough ~~
    .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1') // Remove links [text](url)
    .replace(/\n/g, ' ')       // Replace newlines with spaces
    .replace(/\s+/g, ' ');     // Collapse multiple spaces
};

export const speakMessage = (text, synth, voice) => {
  if (!synth || !text) return;
  
  const cleanText = cleanForSpeech(text);
  const utterance = new SpeechSynthesisUtterance(cleanText);
  utterance.voice = voice;
  utterance.rate = 0.95;
  utterance.pitch = 1;
  
  synth.cancel(); // Cancel any ongoing speech
  synth.speak(utterance);
  
  return utterance;
};