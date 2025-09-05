// src/utils/voiceCommandParser.js

const API_BASE_URL = 'http://127.0.0.1:8000/api';

/**
 * Enhanced command parsing with natural language support
 */
export const parseVoiceCommand = (command) => {
  const normalized = command.toLowerCase().trim();
  
  // Clean up the command by removing filler words
  const cleanedCommand = normalized
    .replace(/\b(to|a|the|please|can you|would you|could you|i want to|i need to)\b/gi, '')
    .replace(/\s+/g, ' ')
    .trim();

  console.log('Parsing command:', { original: command, cleaned: cleanedCommand });

  // Enhanced task management with multiple patterns
  const taskMatch = cleanedCommand.match(/(?:add|create|new|make|set)(?:\s+(?:a|new))?\s+task(?:\s+for)?\s+(.+)/) ||
                   cleanedCommand.match(/(?:remind me to|i should|i must|remember to)\s+(.+)/);
  
  if (taskMatch && taskMatch[1]) {
    const taskText = taskMatch[1].trim();
    return {
      type: 'ADD_TASK',
      data: { content: taskText, title: taskText }, // Try multiple field names
      apiEndpoint: '/tasks',
      method: 'POST'
    };
  }
  
  // Enhanced system commands with multiple patterns
  const openMatch = cleanedCommand.match(/(?:open|launch|start|run)(?:\s+(?:the|my))?\s+(.+)/);
  if (openMatch && openMatch[1]) {
    const appName = openMatch[1].trim();
    return {
      type: 'OPEN_APP',
      data: { app_name: appName, application: appName }, // Try multiple field names
      apiEndpoint: '/system/open',
      method: 'POST'
    };
  }
  
  // Enhanced system stats with multiple patterns
  const statsMatch = cleanedCommand.match(/(?:cpu|usage|stats|statistics|system|performance|resource)/);
  if (statsMatch) {
    return {
      type: 'GET_STATS',
      data: null,
      apiEndpoint: '/system/stats',
      method: 'GET'
    };
  }
  
  // If no specific command matched, treat as regular chat
  return {
    type: 'CHAT',
    data: { message: command, text: command }, // Try multiple field names
    apiEndpoint: '/chat',
    method: 'POST'
  };
};

/**
 * Enhanced execution with better error handling and fallback
 */
export const executeVoiceCommand = async (command) => {
  try {
    const { apiEndpoint, method, data } = command;
    
    const options = {
      method,
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include'
    };
    
    if (method !== 'GET' && data) {
      options.body = JSON.stringify(data);
    }
    
    const response = await fetch(`${API_BASE_URL}${apiEndpoint}`, options);
    
    if (!response.ok) {
      // Try to get error details from response
      let errorMessage = `HTTP error! status: ${response.status}`;
      try {
        const errorData = await response.json();
        if (errorData.detail) {
          errorMessage = typeof errorData.detail === 'string' 
            ? errorData.detail 
            : JSON.stringify(errorData.detail);
        } else if (errorData.message) {
          errorMessage = errorData.message;
        }
      } catch (e) {
        // If we can't parse JSON error, use default message
      }
      throw new Error(errorMessage);
    }
    
    return await response.json();
    
  } catch (error) {
    console.error('Error executing voice command:', error);
    throw error;
  }
};

/**
 * Enhanced processVoiceCommand with better fallback handling
 */
export const processVoiceCommand = async (commandText) => {
  try {
    const parsedCommand = parseVoiceCommand(commandText);
    console.log('Parsed command:', parsedCommand);
    
    // For system commands, try to execute them
    if (parsedCommand.type !== 'CHAT') {
      try {
        const result = await executeVoiceCommand(parsedCommand);
        return {
          success: true,
          type: parsedCommand.type,
          data: result,
          message: getSuccessMessage(parsedCommand.type, result, commandText),
          tts_response: getTTSResponse(parsedCommand.type, result, commandText)
        };
      } catch (error) {
        console.error('Command execution error:', error);
        
        // If it's a 422 validation error, provide specific feedback
        if (error.message.includes('422') || error.message.includes('validation')) {
          return {
            success: false,
            type: 'VALIDATION_ERROR',
            message: `I understand your command, but the server needs different data. ${getValidationHelp(parsedCommand.type)}`,
            originalCommand: commandText,
            error: error.message
          };
        }
        
        // If it's a 404, the endpoint might not exist
        if (error.message.includes('404')) {
          return {
            success: false,
            type: 'ENDPOINT_NOT_FOUND',
            message: `The "${parsedCommand.type.replace('_', ' ')}" feature is not available right now.`,
            originalCommand: commandText,
            error: error.message
          };
        }
        
        return {
          success: false,
          type: 'COMMAND_FAILED',
          message: `I couldn't execute "${commandText}". ${getHelpfulSuggestion(parsedCommand.type)}`,
          originalCommand: commandText,
          error: error.message
        };
      }
    }
    
    // For regular chat, just return the chat intent
    return {
      success: true,
      type: 'CHAT',
      message: 'Processing as chat message',
      originalText: commandText
    };
    
  } catch (error) {
    console.error('Unexpected error in processVoiceCommand:', error);
    return {
      success: false,
      type: 'ERROR',
      message: 'Sorry, I encountered an unexpected error. Please try again.',
      originalCommand: commandText
    };
  }
};

/**
 * Generates appropriate success messages for different command types
 */
const getSuccessMessage = (commandType, result, originalCommand) => {
  switch (commandType) {
    case 'ADD_TASK':
      const taskText = extractTaskText(originalCommand);
      return `✅ Task added: "${taskText}"`;
    
    case 'OPEN_APP':
      const appName = extractAppName(originalCommand);
      return `🚀 Opening ${appName}...`;
    
    case 'GET_STATS':
      // Display actual system statistics data
      if (result && typeof result === 'object') {
        const stats = formatSystemStats(result);
        return `📊 System Statistics:\n${stats}`;
      }
      return `📊 System statistics retrieved`;
    
    default:
      return `Command executed successfully`;
  }
};




/**
 * Format system statistics for display
 */
const formatSystemStats = (stats) => {
  const lines = [];
  
  if (stats.cpu_percent !== undefined) {
    lines.push(`\n CPU Usage: ${stats.cpu_percent}%`);
  }
  
  if (stats.memory_percent !== undefined) {
    lines.push(`\nMemory Usage: ${stats.memory_percent}%`);
  }
  
  if (stats.memory_used !== undefined && stats.memory_total !== undefined) {
    lines.push(`\nMemory: ${formatBytes(stats.memory_used)} / ${formatBytes(stats.memory_total)}`);
  }
  
  if (stats.disk_usage !== undefined) {
    lines.push(`\nDisk Usage: ${stats.disk_usage}%`);
  }
  
  if (stats.uptime !== undefined) {
    lines.push(`\nUptime: ${formatUptime(stats.uptime)}`);
  }
  
  if (stats.process_count !== undefined) {
    lines.push(`\nProcesses: ${stats.process_count}`);
  }
  
  // If no specific stats found, show raw data
  if (lines.length === 0) {
    return JSON.stringify(stats, null, 2);
  }
  
  return lines.join('\n');
};

/**
 * Format system statistics for speech (TTS)
 */
const formatStatsForSpeech = (stats) => {
  const parts = [];
  
  if (stats.cpu_percent !== undefined) {
    parts.push(`CPU usage is ${stats.cpu_percent} percent`);
  }
  
  if (stats.memory_percent !== undefined) {
    parts.push(`memory usage is ${stats.memory_percent} percent`);
  }
  
  if (stats.disk_usage !== undefined) {
    parts.push(`disk usage is ${stats.disk_usage} percent`);
  }
  
  if (stats.uptime !== undefined) {
    parts.push(`system uptime is ${formatUptimeSpeech(stats.uptime)}`);
  }
  
  if (parts.length === 0) {
    return "System statistics retrieved";
  }
  
  return `Current system status: ${parts.join(', ')}`;
};

/**
 * Helper to format bytes for display
 */
const formatBytes = (bytes) => {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

/**
 * Helper to format uptime for display
 */
const formatUptime = (seconds) => {
  const days = Math.floor(seconds / 86400);
  const hours = Math.floor((seconds % 86400) / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  
  const parts = [];
  if (days > 0) parts.push(`${days}d`);
  if (hours > 0) parts.push(`${hours}h`);
  if (minutes > 0) parts.push(`${minutes}m`);
  
  return parts.join(' ') || `${seconds}s`;
};

/**
 * Helper to format uptime for speech
 */
const formatUptimeSpeech = (seconds) => {
  const days = Math.floor(seconds / 86400);
  const hours = Math.floor((seconds % 86400) / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  
  const parts = [];
  if (days > 0) parts.push(`${days} day${days !== 1 ? 's' : ''}`);
  if (hours > 0) parts.push(`${hours} hour${hours !== 1 ? 's' : ''}`);
  if (minutes > 0) parts.push(`${minutes} minute${minutes !== 1 ? 's' : ''}`);
  
  return parts.join(' and ') || 'a few seconds';
};











/**
 * Generates appropriate TTS responses for different command types
 * (This was the missing function!)
 */
const getTTSResponse = (commandType, result, originalCommand) => {
  switch (commandType) {
    case 'ADD_TASK':
      const taskText = extractTaskText(originalCommand);
      return `Task added: ${taskText}`;
    
    case 'OPEN_APP':
      const appName = extractAppName(originalCommand);
      return `Opening ${appName}`;
    
    case 'GET_STATS':
      // Create spoken response for system stats
      if (result && typeof result === 'object') {
        return formatStatsForSpeech(result);
      }
      return `System statistics retrieved`;
    
    default:
      return `Command executed successfully`;
  }
};

/**
 * Generates helpful suggestions when commands fail
 */
const getHelpfulSuggestion = (commandType) => {
  switch (commandType) {
    case 'ADD_TASK':
      return 'Try saying "add task [your task]" or "remind me to [do something]"';
    
    case 'OPEN_APP':
      return 'Try saying "open [application name]" or "launch [app]"';
    
    case 'GET_STATS':
      return 'Try saying "system stats" or "CPU usage"';
    
    default:
      return 'Please try rephrasing your command.';
  }
};

/**
 * Provides validation-specific help
 */
const getValidationHelp = (commandType) => {
  switch (commandType) {
    case 'ADD_TASK':
      return 'The server might expect a different field name for tasks.';
    
    case 'OPEN_APP':
      return 'The server might expect a different field name for applications.';
    
    default:
      return 'The server validation requirements might have changed.';
  }
};

/**
 * Helper to extract task text from various command patterns
 */
const extractTaskText = (command) => {
  const patterns = [
    /(?:add|create|new|make|set)(?:\s+(?:a|new))?\s+task(?:\s+for)?\s+(.+)/,
    /(?:remind me to|i should|i must|remember to)\s+(.+)/,
    /task\s+(?:to|for)?\s+(.+)/
  ];
  
  for (const pattern of patterns) {
    const match = command.toLowerCase().match(pattern);
    if (match && match[1]) {
      return match[1].trim();
    }
  }
  
  // Fallback: remove common prefixes
  return command
    .replace(/^(add|create|new|make|set)\s+(?:task|reminder)?/i, '')
    .replace(/^(remind me to|i should|i must|remember to)/i, '')
    .trim();
};

/**
 * Helper to extract application name
 */
const extractAppName = (command) => {
  const match = command.toLowerCase().match(/(?:open|launch|start|run)(?:\s+(?:the|my))?\s+(.+)/);
  return match && match[1] ? match[1].trim() : command.replace(/^(open|launch|start|run)/i, '').trim();
};

// Optional: Predefined wake words or command prefixes
export const WAKE_WORDS = ['hey neurotrain', 'neurotrain', 'assistant', 'computer'];
export const COMMAND_PREFIXES = [
  'add task', 'create task', 'new task', 'make task', 'set task',
  'open', 'launch', 'start', 'run',
  'what\'s', 'how\'s', 'show me', 'check', 'display',
  'remind me', 'remember to', 'i should', 'i need to'
];

/**
 * New function to check if text contains a voice command
 */
export const isVoiceCommand = (text) => {
  const normalized = text.toLowerCase().trim();
  return COMMAND_PREFIXES.some(prefix => normalized.startsWith(prefix)) ||
         WAKE_WORDS.some(wakeWord => normalized.includes(wakeWord));
};

/**
 * New function to remove wake words from command
 */
export const cleanCommandText = (text) => {
  let cleaned = text.toLowerCase().trim();
  
  // Remove wake words
  WAKE_WORDS.forEach(wakeWord => {
    cleaned = cleaned.replace(wakeWord, '').trim();
  });
  
  // Remove filler words
  cleaned = cleaned
    .replace(/\b(to|a|the|please|can you|would you|could you)\b/gi, '')
    .replace(/\s+/g, ' ')
    .trim();
  
  return cleaned;
};

/**
 * Debug function to test command parsing
 */
export const debugCommandParsing = (commandText) => {
  const parsed = parseVoiceCommand(commandText);
  console.log('Debug parsing:', {
    input: commandText,
    parsed: parsed,
    cleaned: cleanCommandText(commandText),
    isCommand: isVoiceCommand(commandText)
  });
  return parsed;
};

/**
 * Test function to check what field names your backend expects
 */
export const testBackendExpectations = async () => {
  const testCommands = [
    'add task test task',
    'open notepad'
  ];
  
  for (const command of testCommands) {
    console.log(`Testing: "${command}"`);
    const parsed = parseVoiceCommand(command);
    console.log('Would send:', parsed.data);
    
    try {
      const result = await executeVoiceCommand(parsed);
      console.log('Success:', result);
    } catch (error) {
      console.log('Error:', error.message);
    }
  }
};