// frontend/components/markdownUtils.js

/**
 * Cleans markdown for speech synthesis
 */
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