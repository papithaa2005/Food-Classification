import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const createUser = (username, email) => {
  return api.post('/users', { username, email });
};

export const saveUserMetrics = (userId, metrics) => {
  return api.post(`/users/${userId}/metrics`, metrics);
};

export const classifyFood = (formData) => {
  return api.post('/classify-food', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
};

export const getUserHistory = (userId) => {
  return api.get(`/users/${userId}/history`);
};

export default api;