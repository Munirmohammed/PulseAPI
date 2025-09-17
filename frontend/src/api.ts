import axios from 'axios';

const api = axios.create({
  baseURL: '/'
});

export function setToken(token: string | null) {
  if (token) {
    api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    localStorage.setItem('token', token);
  } else {
    delete api.defaults.headers.common['Authorization'];
    localStorage.removeItem('token');
  }
}

export function loadTokenFromStorage() {
  const t = localStorage.getItem('token');
  if (t) setToken(t);
}

export default api;


