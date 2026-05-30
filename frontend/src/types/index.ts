export interface User {
  id: number;
  email?: string;
  username: string;
  first_name?: string;
  last_name?: string;
  full_name: string;
  avatar_url?: string;
  bio?: string;
  headline?: string;
  company?: string;
  location?: string;
  skills: string[];
  interests: string[];
  role: 'attendee' | 'organizer' | 'admin';
  is_verified: boolean;
  created_at?: string;
}

export interface Event {
  id: number;
  title: string;
  slug: string;
  description?: string;
  short_description?: string;
  banner_url?: string;
  event_type: string;
  status: string;
  venue?: string;
  is_virtual: boolean;
  virtual_url?: string;
  start_date: string;
  end_date: string;
  timezone: string;
  max_attendees?: number;
  ticket_price: number;
  currency: string;
  is_free: boolean;
  organizer_id: number;
  community_id?: number;
  tags?: string[];
  registration_count?: number;
  sessions?: Session[];
  created_at?: string;
}

export interface Session {
  id: number;
  event_id: number;
  title: string;
  description?: string;
  start_time: string;
  end_time: string;
  room?: string;
  track?: string;
  capacity?: number;
  is_live?: boolean;
  speakers?: Speaker[];
}

export interface Speaker {
  id: number;
  name: string;
  title?: string;
  company?: string;
  bio?: string;
  avatar_url?: string;
}

export interface Workshop {
  id: number;
  event_id: number;
  title: string;
  description?: string;
  instructor_name?: string;
  start_time: string;
  end_time: string;
  capacity?: number;
  price: number;
  is_free: boolean;
  status?: string;
  room?: string;
}

export interface Registration {
  id: number;
  user_id: number;
  event_id: number;
  workshop_id?: number;
  status: string;
  checked_in_at?: string;
  is_bookmarked: boolean;
  ticket_type: string;
  has_qr: boolean;
}

export interface Payment {
  id: number;
  amount: number;
  currency: string;
  status: string;
  invoice_number?: string;
  created_at?: string;
}

export interface Notification {
  id: number;
  type: string;
  title: string;
  message: string;
  link?: string;
  is_read: boolean;
  created_at?: string;
}

export interface Connection {
  id: number;
  requester_id: number;
  receiver_id: number;
  status: string;
  message?: string;
  networking_score?: number;
  match_reasons?: string[];
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  per_page: number;
  pages: number;
  has_next: boolean;
  has_prev: boolean;
}

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  user: User;
}

export interface MatchSuggestion {
  user: User;
  score: number;
  reasons: string[];
}

export interface Poll {
  id: number;
  question: string;
  options: string[];
  status: string;
  results?: Record<number, number>;
  total_votes?: number;
}
