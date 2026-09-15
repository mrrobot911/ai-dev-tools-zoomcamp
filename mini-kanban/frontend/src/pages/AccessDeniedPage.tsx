import { useRouter } from '@/hooks/useRouter';
import { Button } from '@/components/ui';
import { ShieldX } from 'lucide-react';

export function AccessDeniedPage() {
  const { navigate } = useRouter();

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-50">
      <div className="text-center">
        <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-red-50 text-red-500 mb-4">
          <ShieldX size={32} />
        </div>
        <h1 className="text-2xl font-bold text-slate-800 mb-2">Access Denied</h1>
        <p className="text-sm text-slate-500 mb-6 max-w-sm">
          You don't have permission to access this board. If you believe this is an error,
          ask the board owner to invite you.
        </p>
        <Button onClick={() => navigate('/dashboard')}>
          Back to dashboard
        </Button>
      </div>
    </div>
  );
}
