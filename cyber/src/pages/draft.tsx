import axios, { AxiosRequestConfig } from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
const API_BASE_PATH = '/app/v1/cyber';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const userService = {
  getUsers: () => api.get(`${API_BASE_PATH}/users/`),
  getUser: (id: string | number) => api.get(`${API_BASE_PATH}/users/${id}`),
  createUser: (userData: any) => api.post(`${API_BASE_PATH}/users/`, userData),
  updateUser: (id: string | number, userData: any) => api.put(`${API_BASE_PATH}/users/${id}`, userData),
  deleteUser: (id: string | number) => api.delete(`${API_BASE_PATH}/users/${id}`),
};

export const assetService = {
  getAssets: () => api.get(`${API_BASE_PATH}/assets/`),
  getAsset: (id: string | number) => api.get(`${API_BASE_PATH}/assets/${id}`),
  createAsset: (assetData: any) => api.post(`${API_BASE_PATH}/assets/`, assetData),
  updateAsset: (id: string | number, assetData: any) => api.put(`${API_BASE_PATH}/assets/${id}`, assetData),
  deleteAsset: (id: string | number) => api.delete(`${API_BASE_PATH}/assets/${id}`),
};

export const vulnerabilityService = {
  getVulnerabilities: () => api.get(`${API_BASE_PATH}/vulnerabilities/`),
  getVulnerability: (id: string | number) => api.get(`${API_BASE_PATH}/vulnerabilities/${id}`),
  createVulnerability: (vulnerabilityData: any) => api.post(`${API_BASE_PATH}/vulnerabilities/`, vulnerabilityData),
  updateVulnerability: (id: string | number, vulnerabilityData: any) => api.put(`${API_BASE_PATH}/vulnerabilities/${id}`, vulnerabilityData),
  deleteVulnerability: (id: string | number) => api.delete(`${API_BASE_PATH}/vulnerabilities/${id}`),
};

// Alerts
export const alertService = {
  getAlerts: (params?: any) => api.get(`${API_BASE_PATH}/alerts/`, { params }),
  getAlert: (id: string | number) => api.get(`${API_BASE_PATH}/alerts/${id}`),
  createAlert: (alertData: any) => api.post(`${API_BASE_PATH}/alerts/`, alertData),
  updateAlert: (id: string | number, alertData: any) => api.put(`${API_BASE_PATH}/alerts/${id}`, alertData),
  deleteAlert: (id: string | number) => api.delete(`${API_BASE_PATH}/alerts/${id}`),
  assignIncidentToAlert: (alertId: string | number, incidentId: string | number) =>
    api.post(`${API_BASE_PATH}/alerts/${alertId}/assign-incident/${incidentId}`),
  removeIncidentFromAlert: (alertId: string | number) =>
    api.post(`${API_BASE_PATH}/alerts/${alertId}/remove-incident/`),
};

// Incidents
export const incidentService = {
  getIncidents: (filters?: any) => api.get(`${API_BASE_PATH}/incidents/`, { params: filters }),
  getIncidentById: (id: string | number) => api.get(`${API_BASE_PATH}/incidents/${id}`),
  createIncident: (incidentData: any) => api.post(`${API_BASE_PATH}/incidents/`, incidentData),
  updateIncident: (id: string | number, incidentData: any) => api.put(`${API_BASE_PATH}/incidents/${id}`, incidentData),
  deleteIncident: (id: string | number) => api.delete(`${API_BASE_PATH}/incidents/${id}`),

  // Incident Assets
  getAssetsFromIncident: (incidentId: string | number) => api.get(`${API_BASE_PATH}/incidents/assets/${incidentId}`),
  addAssetToIncident: (data: any) => api.post(`${API_BASE_PATH}/incidents/assets/`, data),
  updateAssetInIncident: (data: any, originalIncidentId: string | number, originalAssetId: string | number) =>
    api.put(`${API_BASE_PATH}/incidents/assets/`, data, {
      params: { original_incident_id: originalIncidentId, original_asset_id: originalAssetId },
    }),
  removeAssetFromIncident: (incidentId: string | number, assetId: string | number) =>
    api.delete(`${API_BASE_PATH}/incidents/assets/${incidentId}/${assetId}/`),

  // Incident Threats
  getThreatsByIncident: (incidentId: string | number) => api.get(`${API_BASE_PATH}/incidents/threats/${incidentId}`),
  addThreatToIncident: (data: any) => api.post(`${API_BASE_PATH}/incidents/threats/`, data),
  updateIncidentThreat: (data: any, originalIncidentId: string | number, originalAssetId: string | number) =>
    api.put(`${API_BASE_PATH}/incidents/threats/`, data, {
      params: { original_incident_id: originalIncidentId, original_asset_id: originalAssetId },
    }),
  removeThreatFromIncident: (incidentId: string | number, threatId: string | number) =>
    api.delete(`${API_BASE_PATH}/incidents/threats/${incidentId}/${threatId}`),
};

// Threat Intelligence
export const threatsService = {
  getThreats: (filters?: any) => api.get(`${API_BASE_PATH}/threat_intelligence/`, { params: filters }),
  getThreatById: (id: string | number) => api.get(`${API_BASE_PATH}/threat_intelligence/${id}`),
  createThreat: (data: any) => api.post(`${API_BASE_PATH}/threat_intelligence/`, data),
  updateThreat: (id: string | number, data: any) => api.put(`${API_BASE_PATH}/threat_intelligence/${id}`, data),
  deleteThreat: (id: string | number) => api.delete(`${API_BASE_PATH}/threat_intelligence/${id}`),

  // Threat Intelligence Associations
  // Threat Intelligence Assets
  getThreatAssets: (threatId: string | number) => api.get(`${API_BASE_PATH}/threat_intelligence/assets/${threatId}`),
  addAssetToThreat: (data: any) => api.post(`${API_BASE_PATH}/threat_intelligence/assets/`, data),
  updateThreatAsset: (data: any, originalThreatId: string | number, originalAssetId: string | number) =>
    api.put(`${API_BASE_PATH}/threat_intelligence/assets/`, data, {
      params: { original_threat_id: originalThreatId, original_asset_id: originalAssetId },
    }),
  deleteThreatAsset: (threatId: string | number, assetId: string | number) =>
    api.delete(`${API_BASE_PATH}/threat_intelligence/assets/${threatId}/${assetId}`),

  // Threat Intelligence Vulnerabilities
  getVulnerabilitiesFromThreat: (threatId: string | number) => api.get(`${API_BASE_PATH}/threat_intelligence/vulnerabilities/${threatId}`),
  addVulnerabilityToThreat: (data: any) => api.post(`${API_BASE_PATH}/threat_intelligence/vulnerabilities/`, data),
  updateThreatVulnerabilities: (data: any, originalThreatId: string | number, originalAssetId: string | number) =>
    api.put(`${API_BASE_PATH}/threat_intelligence/vulnerabilities/`, data, {
      params: { original_threat_id: originalThreatId, original_asset_id: originalAssetId },
    }),
  removeThreatVulnerability: (threatId: string | number, vulnerabilityId: string | number) =>
    api.delete(`${API_BASE_PATH}/threat_intelligence/vulnerabilities/${threatId}/${vulnerabilityId}`),
};

// dashboard
export const dashboardService = {
  getDashboard: () => api.get(`${API_BASE_PATH}/dashboard/`),
};

export default api;