import { useState, useEffect, useCallback } from 'react';

export interface RouteState {
  path: string;
  params: Record<string, string>;
}

function parsePath(): string {
  const hash = window.location.hash.slice(1);
  return hash || '/';
}

export function useRouter() {
  const [path, setPath] = useState(parsePath());

  useEffect(() => {
    const handler = () => setPath(parsePath());
    window.addEventListener('hashchange', handler);
    return () => window.removeEventListener('hashchange', handler);
  }, []);

  const navigate = useCallback((to: string) => {
    window.location.hash = to;
  }, []);

  return { path, navigate };
}

export function parseRoute(path: string): {
  page: 'dashboard' | 'board' | 'login' | 'register' | 'access-denied';
  boardId?: string;
  invitationToken?: string;
} {
  if (path === '/' || path === '/dashboard') return { page: 'dashboard' };
  if (path === '/login') return { page: 'login' };
  if (path === '/register') return { page: 'register' };
  if (path === '/access-denied') return { page: 'access-denied' };

  const boardMatch = path.match(/^\/board\/([^/?]+)/);
  if (boardMatch) return { page: 'board', boardId: boardMatch[1] };

  const inviteMatch = path.match(/^\/invite\/([^/?]+)/);
  if (inviteMatch) return { page: 'register', invitationToken: inviteMatch[1] };

  return { page: 'dashboard' };
}
