import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { ArrowRight, Calendar, Users, Sparkles, Zap, Globe } from 'lucide-react';

const features = [
  { icon: Calendar, title: 'Smart Events', desc: 'Create and discover AI-curated events' },
  { icon: Users, title: 'AI Matchmaking', desc: 'Connect with like-minded professionals' },
  { icon: Sparkles, title: 'Live Engagement', desc: 'Real-time polls, Q&A, and chat' },
  { icon: Zap, title: 'Instant Payments', desc: 'Seamless Razorpay checkout' },
  { icon: Globe, title: 'Virtual & Hybrid', desc: 'Host events anywhere in the world' },
];

export function HomePage() {
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <section className="py-20 text-center">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
        >
          <span className="inline-block px-4 py-1.5 rounded-full glass text-sm text-primary-300 mb-6">
            AI-Powered Event Platform
          </span>
          <h1 className="text-5xl md:text-7xl font-bold mb-6 leading-tight">
            Where Events Meet
            <br />
            <span className="gradient-text">Intelligent Networking</span>
          </h1>
          <p className="text-xl text-slate-400 max-w-2xl mx-auto mb-10">
            The future of event management — combining Eventbrite, LinkedIn, Discord, and Google AI
            into one stunning platform.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link to="/events" className="btn-primary inline-flex items-center gap-2 text-lg px-8 py-3">
              Explore Events <ArrowRight className="w-5 h-5" />
            </Link>
            <Link to="/register" className="btn-secondary inline-flex items-center gap-2 text-lg px-8 py-3">
              Start Free
            </Link>
          </div>
        </motion.div>
      </section>

      <section className="py-16 grid md:grid-cols-2 lg:grid-cols-3 gap-6">
        {features.map((feature, i) => (
          <motion.div
            key={feature.title}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.1 }}
            className="glass-card group"
          >
            <div className="w-12 h-12 rounded-xl bg-primary-500/20 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
              <feature.icon className="w-6 h-6 text-primary-400" />
            </div>
            <h3 className="text-xl font-semibold mb-2">{feature.title}</h3>
            <p className="text-slate-400">{feature.desc}</p>
          </motion.div>
        ))}
      </section>

      <section className="py-20 text-center glass rounded-3xl mb-20">
        <h2 className="text-3xl font-bold mb-4">Ready to transform your events?</h2>
        <p className="text-slate-400 mb-8">Join thousands of organizers and attendees worldwide.</p>
        <Link to="/register" className="btn-primary text-lg px-8 py-3">
          Get Started Now
        </Link>
      </section>
    </div>
  );
}
