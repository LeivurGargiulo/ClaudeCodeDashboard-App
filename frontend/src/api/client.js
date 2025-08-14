/**
 * API client for communicating with the Claude Code Dashboard backend
 */

import axios from 'axios';

// Create axios instance with default configuration
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token if available
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized access
      localStorage.removeItem('auth_token');
      // Could redirect to login page here
    }
    return Promise.reject(error);
  }
);

// Instance management API
export const instancesApi = {
  // Get all instances
  getAll: () => api.get('/instances'),
  
  // Get specific instance
  get: (id) => api.get(`/instances/${id}`),
  
  // Create new instance
  create: (data) => api.post('/instances', data),
  
  // Update instance
  update: (id, data) => api.put(`/instances/${id}`, data),
  
  // Delete instance
  delete: (id) => api.delete(`/instances/${id}`),
  
  // Health check
  checkHealth: (id) => api.post(`/instances/${id}/health`),
  
  // Check all instances health
  checkAllHealth: () => api.post('/instances/health/all'),
  
  // Discover Docker instances
  discoverDocker: () => api.post('/instances/discover/docker'),
  
  // Refresh Docker instances
  refreshDocker: () => api.post('/instances/refresh/docker'),
  
  // Get instance statistics
  getStats: () => api.get('/instances/stats/summary'),
};

// Chat API
export const chatApi = {
  // Send message
  sendMessage: (data) => api.post('/chat/send', data),
  
  // Get chat history
  getHistory: (instanceId, limit) => {
    const params = limit ? { limit } : {};
    return api.get(`/chat/history/${instanceId}`, { params });
  },
  
  // Clear chat history
  clearHistory: (instanceId) => api.delete(`/chat/history/${instanceId}`),
  
  // Get recent messages
  getRecentMessages: (instanceId, count = 10) => 
    api.get(`/chat/messages/${instanceId}/recent`, { params: { count } }),
  
  // Search messages
  searchMessages: (instanceId, query) =>
    api.get(`/chat/messages/${instanceId}/search`, { params: { query } }),
  
  // Get chat statistics
  getStats: (instanceId) => api.get(`/chat/stats/${instanceId}`),
  
  // Export chat history
  exportHistory: (instanceId, format = 'json') =>
    api.get(`/chat/export/${instanceId}`, { 
      params: { format },
      responseType: 'blob'
    }),
};

// Docker API
export const dockerApi = {
  // Get Docker status
  getStatus: () => api.get('/docker/status'),
  
  // Reconnect to Docker daemon
  reconnect: () => api.post('/docker/reconnect'),
  
  // List all containers
  listContainers: () => api.get('/docker/containers'),
  
  // Discover Claude containers
  discoverClaude: () => api.get('/docker/containers/claude'),
  
  // Get container info
  getContainerInfo: (containerId) => api.get(`/docker/containers/${containerId}`),
  
  // Start container
  startContainer: (containerId) => api.post(`/docker/containers/${containerId}/start`),
  
  // Stop container
  stopContainer: (containerId) => api.post(`/docker/containers/${containerId}/stop`),
};

// Health check API
export const healthApi = {
  // Basic health check
  check: () => api.get('/health'),
  
  // Root endpoint
  getInfo: () => api.get('/'),
};

// Authentication API (if needed)
export const authApi = {
  // Login (placeholder - implement if authentication is enabled)
  login: (credentials) => api.post('/auth/login', credentials),
  
  // Logout
  logout: () => {
    localStorage.removeItem('auth_token');
    return Promise.resolve();
  },
  
  // Check if user is authenticated
  isAuthenticated: () => {
    const token = localStorage.getItem('auth_token');
    return Boolean(token);
  },
  
  // Set auth token
  setToken: (token) => {
    localStorage.setItem('auth_token', token);
  },
  
  // Get current token
  getToken: () => {
    return localStorage.getItem('auth_token');
  },
};

// Utility functions
export const apiUtils = {
  // Handle API errors
  handleError: (error) => {
    console.error('API Error:', error);
    
    if (error.response) {
      // Server responded with error status
      const message = error.response.data?.detail || 
                     error.response.data?.message || 
                     `HTTP ${error.response.status}: ${error.response.statusText}`;
      return new Error(message);
    } else if (error.request) {
      // Request was made but no response received
      return new Error('Network error: Unable to connect to server');
    } else {
      // Something else happened
      return new Error(error.message || 'An unexpected error occurred');
    }
  },
  
  // Format error message for display
  formatError: (error) => {
    const processedError = apiUtils.handleError(error);
    return processedError.message;
  },
  
  // Check if error is network-related
  isNetworkError: (error) => {
    return !error.response && error.request;
  },
  
  // Check if error is authentication-related
  isAuthError: (error) => {
    return error.response?.status === 401;
  },
};

export default api;