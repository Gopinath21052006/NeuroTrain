// 🎤 Voice Input & Output (frontend version)

export const speak = (text) => {
  if (!window.speechSynthesis) {
    console.error("Speech synthesis not supported in this browser.");
    return;
  }

  const utterance = new SpeechSynthesisUtterance(text);
  utterance.lang = "en-US";
  utterance.rate = 1; // speed
  utterance.pitch = 1; // tone

  // Pick a female voice if available
  const voices = window.speechSynthesis.getVoices();
  const femaleVoice = voices.find(v => v.name.toLowerCase().includes("female") || v.name.includes("Zira"));
  if (femaleVoice) utterance.voice = femaleVoice;

  console.log("🗣️ NeuroTrain:", text);
  window.speechSynthesis.speak(utterance);
};

export const listen = () => {
  return new Promise((resolve, reject) => {
    if (!("webkitSpeechRecognition" in window)) {
      reject("Speech Recognition not supported in this browser.");
      return;
    }

    const recognition = new webkitSpeechRecognition();
    recognition.lang = "en-US";
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;

    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      console.log("🎤 Heard:", transcript);
      resolve(transcript);
    };

    recognition.onerror = (err) => {
      reject(`Voice input error: ${err.error}`);
    };

    recognition.start();
  });
};
