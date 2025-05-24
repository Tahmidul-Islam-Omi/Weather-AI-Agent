import axios from 'axios';

const API_URL = 'https://weather-ai-agent-moxk.onrender.com/api/weather/query';
const CLEAR_CHAT_URL = 'https://weather-ai-agent-moxk.onrender.com/api/weather/clear-chat';

// Generate a unique session ID for each user session
const generateSessionId = () => {
    return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
};

// Get or create session ID
const getSessionId = () => {
    let sessionId = localStorage.getItem('weather_chat_session_id');
    if (!sessionId) {
        sessionId = generateSessionId();
        localStorage.setItem('weather_chat_session_id', sessionId);
    }
    return sessionId;
};

export const sendMessage = async (message) => {
    try {
        const sessionId = getSessionId();
        const response = await axios.post(API_URL, 
            { query: message },
            {
                headers: {
                    'X-Session-ID': sessionId
                }
            }
        );
        return response.data;
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
};

export const clearChatHistory = async () => {
    try {
        const sessionId = getSessionId();
        await axios.delete(CLEAR_CHAT_URL, {
            headers: {
                'X-Session-ID': sessionId
            }
        });
        
        // Remove old session ID and generate a new one immediately
        localStorage.removeItem('weather_chat_session_id');
        const newSessionId = generateSessionId();
        localStorage.setItem('weather_chat_session_id', newSessionId);
        
        console.log(`Chat cleared. New session ID: ${newSessionId}`);
        return true;
    } catch (error) {
        console.error('Error clearing chat history:', error);
        // Still generate new session ID even if API call fails
        localStorage.removeItem('weather_chat_session_id');
        const newSessionId = generateSessionId();
        localStorage.setItem('weather_chat_session_id', newSessionId);
        throw error;
    }
};