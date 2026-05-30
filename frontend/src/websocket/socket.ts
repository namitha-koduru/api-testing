import { io, Socket } from 'socket.io-client';
import { useAuthStore } from '../store/authStore';
import { useNotificationStore } from '../store/authStore';

let socket: Socket | null = null;

export function getSocket(): Socket {
  if (!socket) {
    const url = import.meta.env.VITE_WS_URL || 'http://localhost:5000';
    socket = io(url, { transports: ['websocket', 'polling'], autoConnect: false });
  }
  return socket;
}

export function connectSocket() {
  const token = useAuthStore.getState().accessToken;
  const s = getSocket();
  if (!token) return s;

  if (!s.connected) {
    s.connect();
    s.emit('authenticate', { token: `Bearer ${token}` });
  }

  s.off('notification');
  s.on('notification', (data) => {
    useNotificationStore.getState().addNotification(data);
  });

  return s;
}

export function disconnectSocket() {
  if (socket?.connected) {
    socket.disconnect();
  }
}

export function joinEventRoom(eventId: number, userId: number, sessionId?: number) {
  const s = getSocket();
  s.emit('join_event', { event_id: eventId, session_id: sessionId, user_id: userId });
}

export function leaveEventRoom(eventId: number, userId: number, sessionId?: number) {
  const s = getSocket();
  s.emit('leave_event', { event_id: eventId, session_id: sessionId, user_id: userId });
}
