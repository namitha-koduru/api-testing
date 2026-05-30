import axios from 'axios';
import { useAuthStore } from '../store/authStore';

const API_URL = import.meta.env.VITE_API_URL || '/api';

export const api = axios.create({
  baseURL: API_URL,
  headers: { 'Content-Type': 'application/json' },
});

api.interceptors.request.use((config) => {
  const token = useAuthStore.getState().accessToken;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config;
    if (error.response?.status === 401 && !original._retry) {
      original._retry = true;
      const refreshToken = useAuthStore.getState().refreshToken;
      if (refreshToken) {
        try {
          const { data } = await axios.post(`${API_URL}/auth/refresh`, null, {
            headers: { Authorization: `Bearer ${refreshToken}` },
          });
          useAuthStore.getState().setTokens(data.access_token, data.refresh_token);
          original.headers.Authorization = `Bearer ${data.access_token}`;
          return api(original);
        } catch {
          useAuthStore.getState().logout();
        }
      }
    }
    return Promise.reject(error);
  }
);

export const authApi = {
  register: (data: Record<string, string>) => api.post('/auth/register', data),
  login: (email: string, password: string) => api.post('/auth/login', { email, password }),
  me: () => api.get('/auth/me'),
  refresh: () => api.post('/auth/refresh'),
};

export const eventsApi = {
  list: (params?: Record<string, string | number>) => api.get('/events', { params }),
  get: (id: number) => api.get(`/events/${id}`),
  getBySlug: (slug: string) => api.get(`/events/slug/${slug}`),
  create: (data: Record<string, unknown>) => api.post('/events', data),
  update: (id: number, data: Record<string, unknown>) => api.put(`/events/${id}`, data),
  publish: (id: number) => api.post(`/events/${id}/publish`),
  register: (id: number, data?: Record<string, unknown>) => api.post(`/events/${id}/register`, data),
};

export const paymentsApi = {
  createOrder: (registrationId: number, amount: number) =>
    api.post('/payments/create-order', { registration_id: registrationId, amount }),
  verify: (data: Record<string, string>) => api.post('/payments/verify', data),
  get: (id: number) => api.get(`/payments/${id}`),
};

export const networkingApi = {
  connect: (receiverId: number, message?: string) =>
    api.post('/networking/connect', { receiver_id: receiverId, message }),
  connections: () => api.get('/networking/connections'),
  suggestions: () => api.get('/networking/suggestions'),
  sendMessage: (receiverId: number, content: string) =>
    api.post('/networking/messages', { receiver_id: receiverId, content }),
  conversation: (userId: number) => api.get(`/networking/messages/${userId}`),
};

export const aiApi = {
  chat: (message: string, context?: string) => api.post('/ai/chat', { message, context }),
  summarize: (eventId: number) => api.get(`/ai/summarize/${eventId}`),
  matchmaking: () => api.get('/ai/matchmaking'),
  profileAnalyze: () => api.get('/ai/profile-analyze'),
};

export const analyticsApi = {
  organizer: () => api.get('/analytics/organizer'),
  admin: () => api.get('/analytics/admin'),
  event: (eventId: number) => api.get(`/analytics/event/${eventId}`),
};

export const notificationsApi = {
  list: (unread?: boolean) => api.get('/notifications', { params: { unread } }),
  markRead: (id: number) => api.post(`/notifications/${id}/read`),
};

export const workshopsApi = {
  byEvent: (eventId: number) => api.get(`/workshops/event/${eventId}`),
};

export const sessionsApi = {
  byEvent: (eventId: number) => api.get(`/sessions/event/${eventId}`),
};

export const pollsApi = {
  byEvent: (eventId: number) => api.get(`/polls/event/${eventId}`),
  vote: (pollId: number, selectedOptions: number[]) =>
    api.post(`/polls/${pollId}/vote`, { selected_options: selectedOptions }),
};
