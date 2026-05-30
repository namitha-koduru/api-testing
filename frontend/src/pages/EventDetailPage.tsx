import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { Calendar, MapPin, Users, Clock, Sparkles, Ticket } from 'lucide-react';
import { eventsApi, workshopsApi, sessionsApi, aiApi, paymentsApi } from '../services/api';
import { GlassCard, Skeleton } from '../components/ui/GlassCard';
import { formatDate, formatCurrency, loadRazorpay } from '../utils';
import { useAuthStore } from '../store/authStore';
import type { Registration } from '../types';

export function EventDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { isAuthenticated, user } = useAuthStore();

  const { data: eventData, isLoading } = useQuery({
    queryKey: ['event', id],
    queryFn: () => eventsApi.get(Number(id)),
    enabled: !!id,
  });

  const { data: workshopsData } = useQuery({
    queryKey: ['workshops', id],
    queryFn: () => workshopsApi.byEvent(Number(id)),
    enabled: !!id,
  });

  const { data: sessionsData } = useQuery({
    queryKey: ['sessions', id],
    queryFn: () => sessionsApi.byEvent(Number(id)),
    enabled: !!id,
  });

  const { data: summaryData } = useQuery({
    queryKey: ['ai-summary', id],
    queryFn: () => aiApi.summarize(Number(id)),
    enabled: !!id && isAuthenticated,
  });

  const registerMutation = useMutation({
    mutationFn: async (workshopId?: number) => {
      const res = await eventsApi.register(Number(id), { workshop_id: workshopId });
      const registration: Registration = res.data;

      const event = eventData?.data;
      const workshop = workshopsData?.data?.find((w: { id: number }) => w.id === workshopId);
      const amount = workshop ? workshop.price : event?.ticket_price || 0;

      if (amount > 0) {
        const orderRes = await paymentsApi.createOrder(registration.id, amount);
        if (orderRes.data.free) return registration;

        const loaded = await loadRazorpay();
        if (!loaded) throw new Error('Failed to load payment gateway');

        return new Promise<Registration>((resolve, reject) => {
          const options = {
            key: orderRes.data.key_id,
            amount: orderRes.data.amount * 100,
            currency: orderRes.data.currency,
            order_id: orderRes.data.order_id,
            name: 'EventNet',
            description: event?.title,
            handler: async (response: Record<string, string>) => {
              await paymentsApi.verify({
                razorpay_order_id: response.razorpay_order_id,
                razorpay_payment_id: response.razorpay_payment_id,
                razorpay_signature: response.razorpay_signature,
              });
              resolve(registration);
            },
            prefill: { email: user?.email, name: user?.full_name },
            theme: { color: '#6366f1' },
          };
          const rzp = new window.Razorpay(options);
          rzp.on('payment.failed', () => reject(new Error('Payment failed')));
          rzp.open();
        });
      }
      return registration;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['event', id] });
      navigate('/payment/success');
    },
  });

  const event = eventData?.data;
  const workshops = workshopsData?.data || [];
  const sessions = sessionsData?.data || [];

  if (isLoading) {
    return (
      <div className="max-w-5xl mx-auto px-4 py-8">
        <Skeleton className="h-64 mb-8" />
        <Skeleton className="h-40" />
      </div>
    );
  }

  if (!event) {
    return <div className="text-center py-20">Event not found</div>;
  }

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
        <div className="h-64 rounded-2xl bg-gradient-to-br from-primary-600/40 to-accent/30 mb-8 flex items-end p-8 relative overflow-hidden">
          {event.banner_url && (
            <img src={event.banner_url} alt="" className="absolute inset-0 w-full h-full object-cover opacity-50" />
          )}
          <div className="relative z-10">
            <div className="flex gap-2 mb-3">
              {(event.tags || []).map((tag: string) => (
                <span key={tag} className="text-xs px-3 py-1 rounded-full bg-white/20 backdrop-blur">
                  {tag}
                </span>
              ))}
            </div>
            <h1 className="text-4xl font-bold">{event.title}</h1>
          </div>
        </div>

        <div className="grid lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2 space-y-6">
            <GlassCard>
              <h2 className="text-xl font-semibold mb-4">About</h2>
              <p className="text-slate-300 leading-relaxed">{event.description}</p>
            </GlassCard>

            {summaryData?.data?.summary && (
              <GlassCard>
                <div className="flex items-center gap-2 mb-4">
                  <Sparkles className="w-5 h-5 text-primary-400" />
                  <h2 className="text-xl font-semibold">AI Summary</h2>
                </div>
                <p className="text-slate-300 whitespace-pre-line">{summaryData.data.summary}</p>
              </GlassCard>
            )}

            {sessions.length > 0 && (
              <GlassCard>
                <h2 className="text-xl font-semibold mb-4">Schedule</h2>
                <div className="space-y-4">
                  {sessions.map((session: { id: number; title: string; start_time: string; room?: string; speakers?: { name: string }[] }) => (
                    <div key={session.id} className="p-4 rounded-xl bg-white/5">
                      <h3 className="font-medium">{session.title}</h3>
                      <div className="flex items-center gap-4 text-sm text-slate-400 mt-2">
                        <span className="flex items-center gap-1">
                          <Clock className="w-4 h-4" />
                          {formatDate(session.start_time)}
                        </span>
                        {session.room && <span>{session.room}</span>}
                      </div>
                      {session.speakers && session.speakers.length > 0 && (
                        <p className="text-sm text-primary-300 mt-2">
                          Speakers: {session.speakers.map((s) => s.name).join(', ')}
                        </p>
                      )}
                    </div>
                  ))}
                </div>
              </GlassCard>
            )}

            {workshops.length > 0 && (
              <GlassCard>
                <h2 className="text-xl font-semibold mb-4">Workshops</h2>
                <div className="space-y-3">
                  {workshops.map((workshop: { id: number; title: string; price: number; is_free: boolean; instructor_name?: string }) => (
                    <div key={workshop.id} className="flex items-center justify-between p-4 rounded-xl bg-white/5">
                      <div>
                        <h3 className="font-medium">{workshop.title}</h3>
                        <p className="text-sm text-slate-400">{workshop.instructor_name}</p>
                      </div>
                      <div className="flex items-center gap-3">
                        <span className="text-primary-400 font-medium">
                          {workshop.is_free ? 'Free' : formatCurrency(workshop.price)}
                        </span>
                        {isAuthenticated && (
                          <button
                            onClick={() => registerMutation.mutate(workshop.id)}
                            disabled={registerMutation.isPending}
                            className="btn-primary text-sm py-1.5 px-4"
                          >
                            Register
                          </button>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </GlassCard>
            )}
          </div>

          <div className="space-y-6">
            <GlassCard>
              <div className="space-y-4">
                <div className="flex items-center gap-3">
                  <Calendar className="w-5 h-5 text-primary-400" />
                  <div>
                    <p className="text-sm text-slate-400">Date</p>
                    <p className="font-medium">{formatDate(event.start_date)}</p>
                  </div>
                </div>
                {event.venue && (
                  <div className="flex items-center gap-3">
                    <MapPin className="w-5 h-5 text-primary-400" />
                    <div>
                      <p className="text-sm text-slate-400">Venue</p>
                      <p className="font-medium">{event.venue}</p>
                    </div>
                  </div>
                )}
                <div className="flex items-center gap-3">
                  <Users className="w-5 h-5 text-primary-400" />
                  <div>
                    <p className="text-sm text-slate-400">Attendees</p>
                    <p className="font-medium">{event.registration_count || 0} registered</p>
                  </div>
                </div>
                <div className="pt-4 border-t border-white/10">
                  <p className="text-2xl font-bold gradient-text mb-4">
                    {event.is_free ? 'Free' : formatCurrency(event.ticket_price, event.currency)}
                  </p>
                  {isAuthenticated ? (
                    <button
                      onClick={() => registerMutation.mutate(undefined)}
                      disabled={registerMutation.isPending}
                      className="btn-primary w-full flex items-center justify-center gap-2"
                    >
                      <Ticket className="w-5 h-5" />
                      {registerMutation.isPending ? 'Processing...' : 'Register Now'}
                    </button>
                  ) : (
                    <button onClick={() => navigate('/login')} className="btn-primary w-full">
                      Login to Register
                    </button>
                  )}
                </div>
              </div>
            </GlassCard>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
