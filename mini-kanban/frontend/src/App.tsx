import { AuthProvider, useAuth } from '@/context/AuthContext';
import { useRouter, parseRoute } from '@/hooks/useRouter';
import { LoginPage } from '@/pages/LoginPage';
import { DashboardPage } from '@/pages/DashboardPage';
import { BoardPage } from '@/pages/BoardPage';
import { AccessDeniedPage } from '@/pages/AccessDeniedPage';
import { Loader2 } from 'lucide-react';

function AppRoutes() {
  const { user, loading } = useAuth();
  const { path, navigate } = useRouter();
  const route = parseRoute(path);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50">
        <Loader2 className="animate-spin text-slate-400" size={32} />
      </div>
    );
  }

  // Unauthenticated users
  if (!user) {
    if (route.page === 'register') {
      return <LoginPage invitationToken={route.invitationToken} />;
    }
    if (route.page === 'login') {
      return <LoginPage />;
    }
    navigate('/login');
    return null;
  }

  // Authenticated users
  if (route.page === 'login') {
    navigate('/dashboard');
    return null;
  }

  if (route.page === 'register') {
    navigate('/dashboard');
    return null;
  }

  if (route.page === 'access-denied') return <AccessDeniedPage />;
  if (route.page === 'board' && route.boardId)
    return <BoardPage boardId={route.boardId} />;

  return <DashboardPage />;
}

export default function App() {
  return (
    <AuthProvider>
      <AppRoutes />
    </AuthProvider>
  );
}
