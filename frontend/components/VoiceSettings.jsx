import React, { useState } from 'react';

const VoiceSettings = ({ 
  isAlwaysListening, 
  setIsAlwaysListening, 
  hotkey, 
  setHotkey,
  availableVoices,
  selectedVoice,
  setSelectedVoice,
  startTraining
}) => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="voice-settings">
      <button 
        onClick={() => setIsOpen(!isOpen)}
        className="settings-toggle"
      >
        ⚙️ Voice Settings
      </button>
      
      {isOpen && (
        <div className="settings-panel">
          <h3>Voice Settings</h3>
          
          <div className="setting-group">
            <label>
              <input 
                type="checkbox" 
                checked={isAlwaysListening} 
                onChange={(e) => setIsAlwaysListening(e.target.checked)} 
              />
              Enable Always Listening Mode
            </label>
          </div>
          
          <div className="setting-group">
            <label>Hotkey</label>
            <input 
              type="text" 
              value={hotkey} 
              readOnly
              onKeyDown={(e) => {
                e.preventDefault();
                setHotkey(e.code);
              }}
              className="hotkey-input"
            />
            <small>Press any key to set as hotkey</small>
          </div>
          
          <div className="setting-group">
            <label>Voice</label>
            <select 
              value={availableVoices.findIndex(v => v === selectedVoice)} 
              onChange={(e) => setSelectedVoice(availableVoices[e.target.value])}
            >
              {availableVoices.map((voice, index) => (
                <option key={index} value={index}>
                  {voice.name} ({voice.lang})
                </option>
              ))}
            </select>
          </div>
          
          <div className="setting-group">
            <button onClick={startTraining} className="training-button">
              Start Voice Training
            </button>
          </div>
          
          <button onClick={() => setIsOpen(false)}>Close</button>
        </div>
      )}
    </div>
  );
};

export default VoiceSettings;