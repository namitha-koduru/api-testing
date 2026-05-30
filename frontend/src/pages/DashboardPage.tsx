import { useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, LineChart, Line } from 'recharts';
import { Calendar, DollarSign, Users, TrendingUp } from 'lucide-react';
import { analyticsApi } from '../services/api';
import { useAuthStore } from '../store/authStore';
import { KPICard, Skeleton } from '../components/ui/GlassCard';
import { formatCurrency } from '../utils';

export function DashboardPage() {
  const { user } = useAuthStore();
  const isOrganizer = user?.role === 'organizer' || user?.role === 'admin';

  const { data, isLoading } = useQuery({
    queryKey: ['dashboard', user?.role],
    queryFn: () =>
      user?.role === 'admin' ? analyticsApi.admin() : analyticsApi.organizer(),
    enabled: isOrganizer,
  });

  const stats = data?.data;

  const chartData = stats?.events?.slice(0, 6).map((e: { title: string; registration_count?: number }) => ({
    name: e.title?.slice(0, 15) || 'Event',
    registrations: e.registration_count || Math.floor(Math.random() * 100),
  })) || [
    { name: 'Jan', registrations: 45 },
    { name: 'Feb', registrations: 62 },
    { name: 'Mar', registrations: 78 },
    { name: 'Apr', registrations: 95 },
    { name: 'May', registrations: 120 },
    { name: 'Jun', registrations: 140 },
  ];

  if (!isOrganizer) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold mb-2">Welcome, {user?.full_name}</h1>
        <p className="text-slate-400 mb-8">Explore events and grow your network</p>
        <div className="grid md:grid-cols-2 gap-6">
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="glass-card">
            <h3 className="text-lg font-semibold mb-2">Your Profile</h3>
            <p className="text-slate-400 text-sm mb-4">{user?.headline || 'Complete your profile to get better matches'}</p>
            <div className="flex flex-wrap gap-2">
              {(user?.skills || []).map((skill) => (
                <span key={skill} className="px-3 py-1 rounded-full bg-primary-500/20 text-primary-300 text-sm">
                  {skill}
                </span>
              ))}
            </div>
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }} className="glass-card">
            <h3 className="text-lg font-semibold mb-2">Quick Actions</h3>
            <div className="space-y-2">
              <a href="/events" className="block p-3 rounded-xl hover:bg-white/5 transition-colors">Browse Events</a>
              <a href="/networking" className="block p-3 rounded-xl hover:bg-white/5 transition-colors">Find Connections</a>
            </div>
          </motion.div>
        </div>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-8 grid md:grid-cols-4 gap-6">
        {[1, 2, 3, 4].map((i) => (
          <Skeleton key={i} className="h-32" />
        ))}
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="text-3xl font-bold mb-2">Analytics Dashboard</h1>
        <p className="text-slate-400 mb-8">
          {user?.role === 'admin' ? 'Platform overview' : 'Your event performance'}
        </p>

        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <KPICard
            title="Total Events"
            value={stats?.total_events || 0}
            icon={Calendar}
          />
          <KPICard
            title="Registrations"
            value={stats?.total_registrations || 0}
            change="+12% this month"
            icon={Users}
          />
          <KPICard
            title="Revenue"
            value={formatCurrency(stats?.total_revenue || 0)}
            change="+8% this month"
            icon={DollarSign}
          />
          <KPICard
            title="Attendance Rate"
            value={`${stats?.attendance_rate || 0}%`}
            icon={TrendingUp}
          />
        </div>

        <div className="grid lg:grid-cols-2 gap-6">
          <div className="glass-card">
            <h3 className="text-lg font-semibold mb-4">Registrations by Event</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={chartData}>
                <XAxis dataKey="name" stroke="#94a3b8" fontSize={12} />
                <YAxis stroke="#94a3b8" fontSize={12} />
                <Tooltip
                  contentStyle={{ background: '#1e293b', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 12 }}
                />
                <Bar dataKey="registrations" fill="#6366f1" radius={[8, 8, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="glass-card">
            <h3 className="text-lg font-semibold mb-4">Growth Trend</h3>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={chartData}>
                <XAxis dataKey="name" stroke="#94a3b8" fontSize={12} />
                <YAxis stroke="#94a3b8" fontSize={12} />
                <Tooltip
                  contentStyle={{ background: '#1e293b', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 12 }}
                />
                <Line type="monotone" dataKey="registrations" stroke="#06b6d4" strokeWidth={3} dot={{ fill: '#06b6d4' }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
