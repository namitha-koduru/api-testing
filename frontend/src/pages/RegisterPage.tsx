import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Link, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useMutation } from '@tanstack/react-query';
import { authApi } from '../services/api';

const schema = z.object({
  email: z.string().email(),
  username: z.string().min(3),
  password: z.string().min(6),
  first_name: z.string().optional(),
  last_name: z.string().optional(),
  role: z.enum(['attendee', 'organizer']),
});

type FormData = z.infer<typeof schema>;

export function RegisterPage() {
  const navigate = useNavigate();
  const { register, handleSubmit, formState: { errors } } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: { role: 'attendee' as const },
  });

  const mutation = useMutation({
    mutationFn: (data: FormData) => authApi.register(data as Record<string, string>),
    onSuccess: () => navigate('/login'),
  });

  return (
    <div className="min-h-[80vh] flex items-center justify-center px-4 py-12">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="w-full max-w-md glass p-8 rounded-2xl"
      >
        <h1 className="text-3xl font-bold text-center mb-2">Join EventNet</h1>
        <p className="text-slate-400 text-center mb-8">Create your account and start networking</p>

        <form onSubmit={handleSubmit((d) => mutation.mutate(d))} className="space-y-4">
          <div className="grid grid-cols-2 gap-3">
            <input {...register('first_name')} placeholder="First name" className="input-field" />
            <input {...register('last_name')} placeholder="Last name" className="input-field" />
          </div>
          <input {...register('username')} placeholder="Username" className="input-field" />
          {errors.username && <p className="text-red-400 text-sm">{errors.username.message}</p>}
          <input {...register('email')} placeholder="Email" className="input-field" />
          {errors.email && <p className="text-red-400 text-sm">{errors.email.message}</p>}
          <input {...register('password')} type="password" placeholder="Password" className="input-field" />
          {errors.password && <p className="text-red-400 text-sm">{errors.password.message}</p>}
          <select {...register('role')} className="input-field">
            <option value="attendee">Attendee</option>
            <option value="organizer">Organizer</option>
          </select>

          {mutation.isError && (
            <p className="text-red-400 text-sm text-center">
              {(mutation.error as { response?: { data?: { message?: string } } })?.response?.data?.message ||
                'Registration failed'}
            </p>
          )}

          <button type="submit" disabled={mutation.isPending} className="btn-primary w-full">
            {mutation.isPending ? 'Creating account...' : 'Create Account'}
          </button>
        </form>

        <p className="text-center text-sm text-slate-400 mt-6">
          Already have an account?{' '}
          <Link to="/login" className="text-primary-400 hover:underline">
            Sign in
          </Link>
        </p>
      </motion.div>
    </div>
  );
}
