import axios from 'axios';

const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8080'
});

api.interceptors.response.use(
  response => response,
  error => {
    const message = error.response?.data?.message || 'An unexpected error occurred';
    
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }

    // Propagate the error message to be handled by components
    error.displayMessage = message;
    return Promise.reject(error);
  }
);

export default api; 