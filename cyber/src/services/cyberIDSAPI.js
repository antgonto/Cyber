// API Service for Cyber IDS
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000/app/v1/cyber';

const cyberIDSAPI = {
  // Health check
  getHealth: async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/ml/health`);
      return response.data;
    } catch (error) {
      console.error('Health check failed:', error);
      throw error;
    }
  },

  // Get metrics
  getMetrics: async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/ml/metrics`);
      return response.data;
    } catch (error) {
      console.error('Failed to fetch metrics:', error);
      throw error;
    }
  },

  // Train model
  trainModel: async (trainingConfig) => {
    try {
      const response = await axios.post(`${API_BASE_URL}/ml/train`, trainingConfig);
      return response.data;
    } catch (error) {
      console.error('Training failed:', error);
      throw error;
    }
  },

  // Predict on flows
  predict: async (flows, threshold = 0.5) => {
    try {
      const response = await axios.post(`${API_BASE_URL}/ml/predict`, {
        flows,
        threshold,
      });
      return response.data;
    } catch (error) {
      console.error('Prediction failed:', error);
      throw error;
    }
  },
};

export default cyberIDSAPI;

