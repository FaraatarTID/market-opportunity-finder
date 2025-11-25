import axios from 'axios';

const API_URL = 'http://localhost:8000/api';

export const analyzeMarket = async (countryCode, countryName) => {
    try {
        const response = await axios.post(`${API_URL}/markets/analyze`, {
            country_code: countryCode,
            country_name: countryName
        });
        return response.data;
    } catch (error) {
        console.error("Error analyzing market:", error);
        throw error;
    }
};
