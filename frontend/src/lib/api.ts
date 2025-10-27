// API client for Buddy Fox backend

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const api = {
  // Query endpoint
  query: (query: string, sessionId?: string) => {
    return `${API_BASE_URL}/api/query`;
  },

  // Session endpoints
  getSession: (sessionId: string) =>
    fetch(`${API_BASE_URL}/api/session/${sessionId}`).then(res => res.json()),

  deleteSession: (sessionId: string) =>
    fetch(`${API_BASE_URL}/api/session/${sessionId}`, { method: 'DELETE' }).then(res => res.json()),

  getSessions: () =>
    fetch(`${API_BASE_URL}/api/sessions`).then(res => res.json()),

  // Stats endpoints
  getStats: () =>
    fetch(`${API_BASE_URL}/api/stats`).then(res => res.json()),

  getCacheStats: () =>
    fetch(`${API_BASE_URL}/api/stats/cache`).then(res => res.json()),

  getMetrics: () =>
    fetch(`${API_BASE_URL}/api/stats/metrics`).then(res => res.json()),

  // Health check
  health: () =>
    fetch(`${API_BASE_URL}/api/health`).then(res => res.json()),
};

export default api;
