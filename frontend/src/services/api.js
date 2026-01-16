import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';
const API_TOKEN = process.env.REACT_APP_API_TOKEN || 'b1bf242b1c8a2b638e79f0b282599ffafea3faf3';

// Debug: Log token info
if (process.env.NODE_ENV === 'development') {
  console.log('[API] Base URL:', API_BASE_URL);
  console.log('[API] Token configured:', API_TOKEN ? 'YES' : 'NO');
}

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Token ${API_TOKEN}`,
  },
  timeout: 600000, // 600 second timeout (10 minutes) - matches backend for large content processing
});

// Add request interceptor for debugging
apiClient.interceptors.request.use(
  config => {
    if (process.env.NODE_ENV === 'development') {
      console.log('[API REQUEST]', config.method.toUpperCase(), config.url);
    }
    // Ensure token is always in headers
    if (API_TOKEN) {
      config.headers.Authorization = `Token ${API_TOKEN}`;
    }
    return config;
  },
  error => Promise.reject(error)
);

// Add response interceptor for better error handling
apiClient.interceptors.response.use(
  response => {
    if (process.env.NODE_ENV === 'development') {
      console.log('[API RESPONSE] Success -', response.status, response.statusText);
    }
    return response;
  },
  error => {
    console.error('[API ERROR]', {
      status: error.response?.status,
      url: error.config?.url,
      method: error.config?.method,
      data: error.response?.data
    });

    if (error.response?.status === 401) {
      console.error('[AUTH ERROR] 401 - Invalid or expired token');
    }
    if (error.response?.status === 403) {
      console.error('[PERM ERROR] 403 - Permission denied');
    }
    if (error.response?.status === 404) {
      console.error('[NOT FOUND] 404 - Resource not found');
    }
    if (error.response?.status === 400) {
      console.error('[VALIDATION ERROR]', error.response.data);
    }
    if (error.code === 'ECONNABORTED' || !error.response) {
      console.error('[CONNECTION ERROR] Cannot reach backend at', API_BASE_URL);
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
  generateScript: (id, data) => apiClient.post(`/presentations/${id}/generate_script/`, data),
  generateSingleSlideScript: (id, data) => apiClient.post(`/presentations/${id}/generate_single_slide_script/`, data),
};

export const slideService = {
  getAll: () => apiClient.get('/slides/'),
  getById: (id) => apiClient.get(`/slides/${id}/`),
  create: (data) => apiClient.post('/slides/', data),
  update: (id, data) => apiClient.put(`/slides/${id}/`, data),
  delete: (id) => apiClient.delete(`/slides/${id}/`),
};

export default apiClient;
