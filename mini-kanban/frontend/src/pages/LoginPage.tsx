import { useState, type FormEvent } from 'react';
import { useAuth } from '@/context/AuthContext';
import { Input, Button } from '@/components/ui';
import { useRouter } from '@/hooks/useRouter';
import { Kanban, Loader2 } from 'lucide-react';

interface LoginPageProps {
  invitationToken?: string;
}

export function LoginPage({ invitationToken }: LoginPageProps) {
  const { login, register } = useAuth();
  const { navigate } = useRouter();
  const [isRegister, setIsRegister] = useState(!invitationToken ? false : true);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError('');
    setSubmitting(true);
    try {
      if (isRegister) {
        await register(email, password, name, invitationToken);
      } else {
        await login(email, password);
      }
      navigate('/dashboard');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 to-slate-200 p-4">
      <div className="w-full max-w-md">
        <div className="flex items-center justify-center gap-3 mb-8">
          <div className="flex items-center justify-center w-12 h-12 rounded-xl bg-slate-800 text-white">
            <Kanban size={28} />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-slate-800">Mini Kanban</h1>
            <p className="text-sm text-slate-500">Collaborative task boards</p>
          </div>
        </div>

        <div className="bg-white rounded-2xl shadow-xl border border-slate-200 p-8">
          {invitationToken && (
            <div className="mb-4 rounded-lg bg-amber-50 border border-amber-200 px-4 py-3 text-sm text-amber-800">
              You've been invited to a board. {isRegister ? 'Register' : 'Sign in'} to join.
            </div>
          )}

          <h2 className="text-xl font-semibold text-slate-800 mb-6">
            {isRegister ? 'Create your account' : 'Welcome back'}
          </h2>

          <form onSubmit={handleSubmit} className="space-y-4">
            {isRegister && (
              <Input
                label="Name"
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Jane Doe"
                required
              />
            )}
            <Input
              label="Email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="jane@example.com"
              required
            />
            <Input
              label="Password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              required
            />

            {error && (
              <div className="rounded-lg bg-red-50 border border-red-200 px-4 py-2 text-sm text-red-700">
                {error}
              </div>
            )}

            <Button type="submit" className="w-full" disabled={submitting}>
              {submitting ? (
                <>
                  <Loader2 size={16} className="animate-spin" />
                  {isRegister ? 'Creating account...' : 'Signing in...'}
                </>
              ) : isRegister ? (
                'Create account'
              ) : (
                'Sign in'
              )}
            </Button>
          </form>

          <p className="mt-6 text-center text-sm text-slate-500">
            {isRegister ? 'Already have an account?' : "Don't have an account?"}{' '}
            <button
              onClick={() => {
                setIsRegister(!isRegister);
                setError('');
              }}
              className="font-medium text-slate-700 hover:text-slate-900 underline"
            >
              {isRegister ? 'Sign in' : 'Register'}
            </button>
          </p>

          {!isRegister && !invitationToken && (
            <p className="mt-3 text-center text-xs text-slate-400">
              Demo account: demo@example.com / password
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
