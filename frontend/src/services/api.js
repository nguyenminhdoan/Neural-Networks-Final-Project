import axios from 'axios';

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

const api = axios.create({
  baseURL: API_BASE,
  headers: { 'Content-Type': 'application/json' },
});

// ── Data endpoints ──────────────────────────────────────────────────
export const getDataSummary = () => api.get('/data/summary');
export const getStudents = (page = 1, perPage = 20, filters = {}) => {
  const params = { page, per_page: perPage, ...filters };
  return api.get('/data/students', { params });
};
export const getStudent = (id) => api.get(`/data/students/${id}`);
export const getCorrelation = () => api.get('/data/correlation');
export const getLabels = () => api.get('/data/labels');

// ── Prediction endpoints ───────────────────────────────────────────
export const predictPersistence = (data) => api.post('/predict/persistence', data);
export const predictGPA = (data) => api.post('/predict/gpa', data);
export const predictAtRisk = (data) => api.post('/predict/atrisk', data);
export const predictPipeline = (data) => api.post('/predict/pipeline', data);

// ── Model endpoints ────────────────────────────────────────────────
export const getModelMetrics = () => api.get('/models/metrics');
export const getModelFeatures = () => api.get('/models/features');
export const getModelStatus = () => api.get('/models/status');

// ── Admin endpoints ────────────────────────────────────────────────
export const retrainModels = () => api.post('/admin/retrain');
export const getPredictionHistory = (page = 1) =>
  api.get('/admin/predictions', { params: { page, per_page: 20 } });
export const reimportData = () => api.post('/admin/import-data');
export const healthCheck = () => api.get('/health');

export default api;
