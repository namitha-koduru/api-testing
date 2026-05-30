import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { MessageCircle, X, Send, Sparkles } from 'lucide-react';
import { useMutation } from '@tanstack/react-query';
import { aiApi } from '../../services/api';
import { useAuthStore } from '../../store/authStore';

export function AIAssistant() {
  const { isAuthenticated } = useAuthStore();
  const [open, setOpen] = useState(false);
  const [message, setMessage] = useState('');
  const [messages, setMessages] = useState<{ role: 'user' | 'ai'; content: string }[]>([
    { role: 'ai', content: 'Hi! I\'m EventNet AI. Ask me about events, networking, or sessions.' },
  ]);

  const chatMutation = useMutation({
    mutationFn: (msg: string) => aiApi.chat(msg),
    onSuccess: (res) => {
      setMessages((prev) => [...prev, { role: 'ai', content: res.data.response }]);
    },
    onError: () => {
      setMessages((prev) => [
        ...prev,
        { role: 'ai', content: 'Sorry, I couldn\'t process that. Please try again.' },
      ]);
    },
  });

  const send = () => {
    if (!message.trim()) return;
    setMessages((prev) => [...prev, { role: 'user', content: message }]);
    chatMutation.mutate(message);
    setMessage('');
  };

  if (!isAuthenticated) return null;

  return (
    <>
      <motion.button
        whileHover={{ scale: 1.1 }}
        whileTap={{ scale: 0.95 }}
        onClick={() => setOpen(true)}
        className="fixed bottom-6 right-6 w-14 h-14 rounded-full bg-gradient-to-br from-primary-500 to-accent shadow-lg shadow-primary-500/40 flex items-center justify-center z-40"
      >
        <Sparkles className="w-6 h-6 text-white" />
      </motion.button>

      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ opacity: 0, y: 20, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 20, scale: 0.95 }}
            className="fixed bottom-24 right-6 w-96 h-[500px] glass rounded-2xl shadow-2xl z-50 flex flex-col overflow-hidden"
          >
            <div className="flex items-center justify-between p-4 border-b border-white/10 bg-primary-500/10">
              <div className="flex items-center gap-2">
                <MessageCircle className="w-5 h-5 text-primary-400" />
                <span className="font-semibold">EventNet AI</span>
              </div>
              <button onClick={() => setOpen(false)} className="p-1 hover:bg-white/10 rounded-lg">
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="flex-1 overflow-y-auto p-4 space-y-3">
              {messages.map((msg, i) => (
                <div
                  key={i}
                  className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-[80%] p-3 rounded-2xl text-sm ${
                      msg.role === 'user'
                        ? 'bg-primary-500/30 rounded-br-sm'
                        : 'bg-white/5 rounded-bl-sm'
                    }`}
                  >
                    {msg.content}
                  </div>
                </div>
              ))}
              {chatMutation.isPending && (
                <div className="flex gap-1 p-3">
                  <span className="w-2 h-2 bg-primary-400 rounded-full animate-bounce" />
                  <span className="w-2 h-2 bg-primary-400 rounded-full animate-bounce delay-100" />
                  <span className="w-2 h-2 bg-primary-400 rounded-full animate-bounce delay-200" />
                </div>
              )}
            </div>

            <div className="p-4 border-t border-white/10 flex gap-2">
              <input
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && send()}
                placeholder="Ask anything..."
                className="input-field flex-1 py-2 text-sm"
              />
              <button onClick={send} disabled={chatMutation.isPending} className="btn-primary p-2.5">
                <Send className="w-5 h-5" />
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}
