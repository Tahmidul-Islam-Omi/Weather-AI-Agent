import axios from 'axios';

const API_URL = 'http://localhost:8080/api/weather/query';

export const sendMessage = async (message) => {
    try {
        const response = await axios.post(API_URL, { query: message });
        return response.data;
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
};