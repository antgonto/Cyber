import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

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

// Alerts
export const alertService = {
  getAlerts: (params) => api.get('/app/v1/cyber/alerts/', { params }),
  getAlert: (id) => api.get(`/app/v1/cyber/alerts/${id}`),
  createAlert: (alertData) => api.post('/app/v1/cyber/alerts/', alertData),
  updateAlert: (id, alertData) => api.put(`/app/v1/cyber/alerts/${id}`, alertData),
  deleteAlert: (id) => api.delete(`/app/v1/cyber/alerts/${id}`),
  assignIncidentToAlert: (alertId, incidentId) =>
      api.post(`/app/v1/cyber/alerts/${alertId}/assign-incident/${incidentId}`),
  removeIncidentFromAlert: (alertId) =>
      api.post(`/app/v1/cyber/alerts/${alertId}/remove-incident/`),
};

// Incidents
export const incidentService = {
  getIncidents: (filters) => api.get('/app/v1/cyber/incidents/', { params: filters }),
  getIncidentById: (id) => api.get(`/app/v1/cyber/incidents/${id}`),
  createIncident: (incidentData) => api.post('/app/v1/cyber/incidents/', incidentData),
  updateIncident: (id, incidentData) => api.put(`/app/v1/cyber/incidents/${id}`, incidentData),
  deleteIncident: (id) => api.delete(`/app/v1/cyber/incidents/${id}`),

  // Incident Assets
  getAssetsFromIncident: (incidentId) => api.get(`/app/v1/cyber/incidents/assets/${incidentId}`),
  addAssetToIncident: (data) => api.post('/app/v1/cyber/incidents/assets/', data),
  updateAssetInIncident: (data, originalIncidentId, originalAssetId) =>
    api.put(`/app/v1/cyber/incidents/assets/`, data, {
      params: { original_incident_id: originalIncidentId, original_asset_id: originalAssetId },
  }),
  removeAssetFromIncident: (incidentId, assetId) =>
    api.delete(`/app/v1/cyber/incidents/assets/${incidentId}/${assetId}/`),

  // Incident Threats
  getThreatsByIncident: (incidentId) => api.get(`/app/v1/cyber/incidents/threats/${incidentId}`),
  addThreatToIncident: (data) => api.post(`/app/v1/cyber/incidents/threats/`, data),
  updateIncidentThreat: (data, originalIncidentId, originalAssetId) =>
      api.put(`/app/v1/cyber/incidents/threats/`, data, {
        params: { original_incident_id: originalIncidentId, original_asset_id: originalAssetId },
  }),
  removeThreatFromIncident: (incidentId, threatId) =>
        api.delete(`/app/v1/cyber/incidents/threats/${incidentId}/${threatId}`),
};


// Threat Intelligence
export const threatsService = {
  getThreats: (filters) => api.get('/app/v1/cyber/threat_intelligence/', {params: filters}),
  getThreatById: (id) => api.get(`/app/v1/cyber/threat_intelligence/${id}`),
  createThreat: (data) => api.post('/app/v1/cyber/threat_intelligence/', data),
  updateThreat: (id, data) => api.put(`/app/v1/cyber/threat_intelligence/${id}`, data),
  deleteThreat: (id) => api.delete(`/app/v1/cyber/threat_intelligence/${id}`),


  // Threat Intelligence Associations
  // Threat Intelligence Assets
  getThreatAssets: (threatId) => api.get(`/app/v1/cyber/threat_intelligence/assets/${threatId}`),
  addAssetToThreat: (data) => api.post('/app/v1/cyber/threat_intelligence/assets/', data),
  updateThreatAsset: (data, originalThreatId, originalAssetId) =>
    api.put('/app/v1/cyber/threat_intelligence/assets/', data, {
      params: { original_threat_id: originalThreatId, original_asset_id: originalAssetId },
    }),
  deleteThreatAsset: (threatId, assetId) =>
    api.delete(`/app/v1/cyber/threat_intelligence/assets/${threatId}/${assetId}`),
  // Threat Intelligence Vulnerabilities
  getVulnerabilitiesFromThreat: (threatId) => api.get(`/app/v1/cyber/threat_intelligence/vulnerabilities/${threatId}`),
  addVulnerabilityToThreat: (data) => api.post(`/app/v1/cyber/threat_intelligence/vulnerabilities/`, data),
  updateThreatVulnerabilities: (data, originalThreatId, originalAssetId) =>
      api.put(`/app/v1/cyber/threat_intelligence/vulnerabilities/`, data, {
      params: { original_threat_id: originalThreatId, original_asset_id: originalAssetId },
    }),
  removeThreatVulnerability: (threatId, vulnerabilityId) =>
        api.delete(`/app/v1/cyber/threat_intelligence/vulnerabilities/${threatId}/${vulnerabilityId}`),
};


export default api;