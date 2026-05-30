import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { CheckCircle, ArrowRight } from 'lucide-react';

export function PaymentSuccessPage() {
  return (
    <div className="min-h-[70vh] flex items-center justify-center px-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        className="text-center glass p-12 rounded-2xl max-w-md"
      >
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ type: 'spring', delay: 0.2 }}
          className="w-20 h-20 mx-auto mb-6 rounded-full bg-emerald-500/20 flex items-center justify-center"
        >
          <CheckCircle className="w-10 h-10 text-emerald-400" />
        </motion.div>
        <h1 className="text-3xl font-bold mb-2">Payment Successful!</h1>
        <p className="text-slate-400 mb-8">
          Your registration is confirmed. Check your email for the ticket and QR code.
        </p>
        <div className="flex flex-col gap-3">
          <Link to="/events" className="btn-primary inline-flex items-center justify-center gap-2">
            Browse More Events <ArrowRight className="w-4 h-4" />
          </Link>
          <Link to="/dashboard" className="btn-secondary">
            Go to Dashboard
          </Link>
        </div>
      </motion.div>
    </div>
  );
}

export function PaymentFailurePage() {
  return (
    <div className="min-h-[70vh] flex items-center justify-center px-4">
      <div className="text-center glass p-12 rounded-2xl max-w-md">
        <h1 className="text-3xl font-bold mb-2 text-red-400">Payment Failed</h1>
        <p className="text-slate-400 mb-8">Something went wrong. Please try again.</p>
        <Link to="/events" className="btn-primary">
          Try Again
        </Link>
      </div>
    </div>
  );
}
