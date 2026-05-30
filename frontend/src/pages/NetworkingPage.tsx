import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { UserPlus, MessageCircle, Sparkles } from 'lucide-react';
import { networkingApi } from '../services/api';
import { GlassCard, Skeleton } from '../components/ui/GlassCard';
import type { MatchSuggestion } from '../types';

export function NetworkingPage() {
  const queryClient = useQueryClient();

  const { data: suggestions, isLoading } = useQuery({
    queryKey: ['suggestions'],
    queryFn: () => networkingApi.suggestions(),
  });

  const { data: connections } = useQuery({
    queryKey: ['connections'],
    queryFn: () => networkingApi.connections(),
  });

  const connectMutation = useMutation({
    mutationFn: (receiverId: number) => networkingApi.connect(receiverId),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['connections'] }),
  });

  const matches: MatchSuggestion[] = suggestions?.data || [];
  const connectionList = connections?.data || [];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <h1 className="text-3xl font-bold mb-2">Networking</h1>
      <p className="text-slate-400 mb-8">AI-powered matchmaking to grow your professional network</p>

      <section className="mb-12">
        <div className="flex items-center gap-2 mb-6">
          <Sparkles className="w-5 h-5 text-primary-400" />
          <h2 className="text-xl font-semibold">Suggested Connections</h2>
        </div>

        {isLoading ? (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[1, 2, 3].map((i) => (
              <Skeleton key={i} className="h-48" />
            ))}
          </div>
        ) : (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {matches.map((match, i) => (
              <motion.div
                key={match.user.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.05 }}
              >
                <GlassCard>
                  <div className="flex items-start gap-4">
                    <div className="w-14 h-14 rounded-full bg-gradient-to-br from-primary-500 to-accent flex items-center justify-center text-xl font-bold shrink-0">
                      {match.user.full_name?.charAt(0)}
                    </div>
                    <div className="flex-1 min-w-0">
                      <h3 className="font-semibold truncate">{match.user.full_name}</h3>
                      <p className="text-sm text-slate-400 truncate">{match.user.headline || match.user.company}</p>
                      <div className="mt-2">
                        <div className="flex items-center gap-2">
                          <div className="flex-1 h-2 rounded-full bg-white/10 overflow-hidden">
                            <div
                              className="h-full bg-gradient-to-r from-primary-500 to-accent rounded-full"
                              style={{ width: `${match.score}%` }}
                            />
                          </div>
                          <span className="text-sm font-medium text-primary-400">{match.score}%</span>
                        </div>
                      </div>
                      {match.reasons.length > 0 && (
                        <p className="text-xs text-slate-500 mt-2 line-clamp-2">{match.reasons.join(' · ')}</p>
                      )}
                    </div>
                  </div>
                  <div className="flex gap-2 mt-4">
                    <button
                      onClick={() => connectMutation.mutate(match.user.id)}
                      disabled={connectMutation.isPending}
                      className="btn-primary flex-1 flex items-center justify-center gap-2 text-sm py-2"
                    >
                      <UserPlus className="w-4 h-4" /> Connect
                    </button>
                    <button className="btn-secondary p-2">
                      <MessageCircle className="w-4 h-4" />
                    </button>
                  </div>
                </GlassCard>
              </motion.div>
            ))}
          </div>
        )}
      </section>

      <section>
        <h2 className="text-xl font-semibold mb-6">Your Connections</h2>
        {connectionList.length === 0 ? (
          <div className="glass-card text-center py-12 text-slate-400">
            No connections yet. Start connecting with suggested people above!
          </div>
        ) : (
          <div className="space-y-3">
            {connectionList.map((conn: { id: number; requester_id: number; receiver_id: number; status: string; networking_score?: number }) => (
              <GlassCard key={conn.id} hover={false} className="flex items-center justify-between py-4">
                <div>
                  <p className="font-medium">Connection #{conn.id}</p>
                  <p className="text-sm text-slate-400">Status: {conn.status}</p>
                </div>
                {conn.networking_score && (
                  <span className="text-primary-400 font-medium">{conn.networking_score}% match</span>
                )}
              </GlassCard>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
