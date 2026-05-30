import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { Search, MapPin, Calendar, Users, Tag } from 'lucide-react';
import { eventsApi } from '../services/api';
import { GlassCard, Skeleton } from '../components/ui/GlassCard';
import { formatDate, formatCurrency } from '../utils';
import type { Event } from '../types';

export function EventsPage() {
  const [search, setSearch] = useState('');
  const [selectedTag, setSelectedTag] = useState('');

  const { data, isLoading } = useQuery({
    queryKey: ['events', search, selectedTag],
    queryFn: () =>
      eventsApi.list({
        search: search || undefined,
        tags: selectedTag || undefined,
      } as Record<string, string>),
  });

  const events: Event[] = data?.data?.items || [];
  const allTags = [...new Set(events.flatMap((e) => e.tags || []))];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-4xl font-bold mb-2">Discover Events</h1>
        <p className="text-slate-400">Find your next conference, workshop, or meetup</p>
      </div>

      <div className="flex flex-col md:flex-row gap-4 mb-8">
        <div className="relative flex-1">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search events..."
            className="input-field pl-12"
          />
        </div>
        <div className="flex gap-2 flex-wrap">
          <button
            onClick={() => setSelectedTag('')}
            className={`px-4 py-2 rounded-xl text-sm transition-all ${
              !selectedTag ? 'bg-primary-500/30 text-primary-300' : 'glass hover:bg-white/10'
            }`}
          >
            All
          </button>
          {allTags.map((tag) => (
            <button
              key={tag}
              onClick={() => setSelectedTag(tag)}
              className={`px-4 py-2 rounded-xl text-sm transition-all flex items-center gap-1 ${
                selectedTag === tag ? 'bg-primary-500/30 text-primary-300' : 'glass hover:bg-white/10'
              }`}
            >
              <Tag className="w-3 h-3" /> {tag}
            </button>
          ))}
        </div>
      </div>

      {isLoading ? (
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1, 2, 3, 4, 5, 6].map((i) => (
            <Skeleton key={i} className="h-64" />
          ))}
        </div>
      ) : events.length === 0 ? (
        <div className="text-center py-20 glass rounded-2xl">
          <Calendar className="w-16 h-16 mx-auto text-slate-500 mb-4" />
          <p className="text-xl text-slate-400">No events found</p>
        </div>
      ) : (
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {events.map((event, i) => (
            <motion.div
              key={event.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.05 }}
            >
              <Link to={`/events/${event.id}`}>
                <GlassCard className="h-full cursor-pointer overflow-hidden p-0">
                  <div className="h-40 bg-gradient-to-br from-primary-600/40 to-accent/30 flex items-center justify-center">
                    {event.banner_url ? (
                      <img src={event.banner_url} alt="" className="w-full h-full object-cover" />
                    ) : (
                      <Calendar className="w-16 h-16 text-primary-300/50" />
                    )}
                  </div>
                  <div className="p-5">
                    <div className="flex gap-2 mb-2 flex-wrap">
                      {(event.tags || []).slice(0, 3).map((tag) => (
                        <span key={tag} className="text-xs px-2 py-0.5 rounded-full bg-primary-500/20 text-primary-300">
                          {tag}
                        </span>
                      ))}
                    </div>
                    <h3 className="text-lg font-semibold mb-2 line-clamp-2">{event.title}</h3>
                    <p className="text-sm text-slate-400 mb-4 line-clamp-2">
                      {event.short_description}
                    </p>
                    <div className="space-y-2 text-sm text-slate-400">
                      <div className="flex items-center gap-2">
                        <Calendar className="w-4 h-4" />
                        {formatDate(event.start_date)}
                      </div>
                      {event.venue && (
                        <div className="flex items-center gap-2">
                          <MapPin className="w-4 h-4" />
                          {event.venue}
                        </div>
                      )}
                      <div className="flex items-center justify-between pt-2">
                        <span className="flex items-center gap-1">
                          <Users className="w-4 h-4" />
                          {event.registration_count || 0} registered
                        </span>
                        <span className="font-semibold text-primary-400">
                          {event.is_free ? 'Free' : formatCurrency(event.ticket_price, event.currency)}
                        </span>
                      </div>
                    </div>
                  </div>
                </GlassCard>
              </Link>
            </motion.div>
          ))}
        </div>
      )}
    </div>
  );
}
