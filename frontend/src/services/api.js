import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';
const API_TOKEN = process.env.REACT_APP_API_TOKEN || 'b1bf242b1c8a2b638e79f0b282599ffafea3faf3';

// Debug: Log token info (remove in production)
console.log('[API] Base URL:', API_BASE_URL);
console.log('[API] Token configured:', API_TOKEN ? 'YES' : 'NO');
console.log('[API] Token length:', API_TOKEN.length);

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Token ${API_TOKEN}`,
  },
});

// Add request interceptor for debugging
apiClient.interceptors.request.use(
  config => {
    console.log('[API REQUEST]', config.method.toUpperCase(), config.url);
    console.log('[API HEADERS]', config.headers);
    return config;
  },
  error => Promise.reject(error)
);

// Add response interceptor for better error handling
apiClient.interceptors.response.use(
  response => {
    console.log('[API RESPONSE]', response.status, response.statusText);
    return response;
  },
  error => {
    if (error.response?.status === 401) {
      console.error('[AUTH ERROR] 401 Unauthorized - Invalid token');
      console.error('[AUTH] Token being sent:', API_TOKEN.substring(0, 20) + '...');
    }
    if (error.response?.status === 403) {
      console.error('[AUTH ERROR] 403 Forbidden - User does not have permission');
    }
    if (error.response?.status === 400) {
      console.error('[VALIDATION ERROR] 400 Bad Request');
      console.error('[VALIDATION ERRORS]', error.response.data);
      // Print each validation error clearly
      if (typeof error.response.data === 'object') {
        Object.entries(error.response.data).forEach(([key, value]) => {
          console.error(`  - ${key}:`, Array.isArray(value) ? value.join(', ') : value);
        });
      }
    }
    console.error('[API ERROR] Status:', error.response?.status, 'URL:', error.config?.url);
    if (error.response?.data) {
      console.error('[BACKEND RESPONSE]', JSON.stringify(error.response.data, null, 2));
    }
    return Promise.reject(error);
  }
);

export const presentationService = {
  getAll: () => apiClient.get('/presentations/'),
  getById: (id) => apiClient.get(`/presentations/${id}/`),
  create: (data) => apiClient.post('/presentations/', data),
  update: (id, data) => apiClient.put(`/presentations/${id}/`, data),
  delete: (id) => apiClient.delete(`/presentations/${id}/`),
  publish: (id) => apiClient.post(`/presentations/${id}/publish/`),
  unpublish: (id) => apiClient.post(`/presentations/${id}/unpublish/`),
  generate: (data) => apiClient.post('/presentations/generate/', data),
  getJsonStructure: (id) => apiClient.get(`/presentations/${id}/json_structure/`),
};

export const slideService = {
  getAll: () => apiClient.get('/slides/'),
  getById: (id) => apiClient.get(`/slides/${id}/`),
  create: (data) => apiClient.post('/slides/', data),
  update: (id, data) => apiClient.put(`/slides/${id}/`, data),
  delete: (id) => apiClient.delete(`/slides/${id}/`),
};

export default apiClient;
