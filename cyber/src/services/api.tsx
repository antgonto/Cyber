import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const userService = {
  getUsers: () => api.get('/app/v1/cyber/users/'),
  getUser: (id) => api.get(`/app/v1/cyber/users/${id}`),
  createUser: (userData) => api.post('/app/v1/cyber/users/', userData),
  updateUser: (id, userData) => api.put(`/app/v1/cyber/users/${id}`, userData),
  deleteUser: (id) => api.delete(`/app/v1/cyber/users/${id}`),
};

export const assetService = {
  getAssets: () => api.get('/app/v1/cyber/assets/'),
  getAsset: (id) => api.get(`/app/v1/cyber/assets/${id}`),
  createAsset: (assetData) => api.post('/app/v1/cyber/assets/', assetData),
  updateAsset: (id, assetData) => api.put(`/app/v1/cyber/assets/${id}`, assetData),
  deleteAsset: (id) => api.delete(`/app/v1/cyber/assets/${id}`),
};

export const vulnerabilityService = {
  getVulnerabilities: () => api.get('/app/v1/cyber/vulnerabilities/'),
  getVulnerability: (id) => api.get(`/app/v1/cyber/vulnerabilities/${id}`),
  createVulnerability: (vulnerabilityData) => api.post('/app/v1/cyber/vulnerabilities/', vulnerabilityData),
  updateVulnerability: (id, vulnerabilityData) => api.put(`/app/v1/cyber/vulnerabilities/${id}`, vulnerabilityData),
  deleteVulnerability: (id) => api.delete(`/app/v1/cyber/vulnerabilities/${id}`),
};

// Additional services can be added here as new endpoints are created

export default api;