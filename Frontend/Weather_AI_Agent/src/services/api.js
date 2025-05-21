import axios from 'axios';

const API_URL = 'https://weather-ai-agent-moxk.onrender.com/api/weather/query'; // Updated URL

export const sendMessage = async (message) => {
    try {
        const response = await axios.post(API_URL, { query: message });
        return response.data;
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
};