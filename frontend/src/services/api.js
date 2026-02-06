import axios from 'axios';

const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export function login(email, password) {
  return api.post('/api/auth/login', { email, password });
}

export function register(email, password, name, role = 'STAKEHOLDER', inviteToken = null) {
  const body = { email, password, name };
  if (role && !inviteToken) {
    body.role = role;
  }
  if (inviteToken != null) body.invite_token = inviteToken;
  return api.post('/api/auth/register', body);
}

export function getInviteDetails(token) {
  return api.get(`/api/auth/invite/${token}`);
}

export function getMe() {
  return api.get('/api/auth/me');
}

export function getProjects() {
  return api.get('/api/projects');
}

export function createProject(data) {
  return api.post('/api/projects', data);
}

export function getProject(id) {
  return api.get(`/api/projects/${id}`);
}

export function getStakeholderDiscoveryResults(projectId, userId) {
  return api.get(`/api/projects/${projectId}/stakeholders/${userId}/discovery-results`);
}

export function addUserToProject(projectId, email, name) {
  return api.post(`/api/projects/${projectId}/users`, { email, name });
}

export function activateProjectUser(projectId, userId) {
  return api.post(`/api/projects/${projectId}/users/${userId}/activate`);
}

export function getProjectProgress(projectId) {
  return api.get(`/api/projects/${projectId}/progress`);
}

export function submitAssessment(responses) {
  return api.post('/api/session/assessment', { responses });
}

export function getSession() {
  return api.get('/api/session');
}

export function sendMessage(message) {
  return api.post('/api/session/message', { message });
}

export function approveSummary(action, feedback = null) {
  const body = { action };
  if (feedback != null) body.feedback = feedback;
  return api.post('/api/session/approve-summary', body);
}

export function getReport() {
  return api.get('/api/session/report');
}
