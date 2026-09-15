import { useState, useEffect, useCallback } from 'react';
import { useAuth } from '@/context/AuthContext';
import { useRouter } from '@/hooks/useRouter';
import { service } from '@/services';
import type { BoardSummary } from '@/services/types';
import { Button, Input, Modal, Avatar } from '@/components/ui';
import {
  Kanban,
  Plus,
  Users,
  LogOut,
  Loader2,
  Trash2,
  Pencil,
  Crown,
} from 'lucide-react';

export function DashboardPage() {
  const { user, logout } = useAuth();
  const { navigate } = useRouter();
  const [boards, setBoards] = useState<BoardSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);
  const [newBoardName, setNewBoardName] = useState('');
  const [error, setError] = useState('');
  const [creating, setCreating] = useState(false);

  const loadBoards = useCallback(async () => {
    try {
      const list = await service.listBoards();
      setBoards(list);
    } catch {
      // ignore
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadBoards();
  }, [loadBoards]);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setCreating(true);
    try {
      await service.createBoard({ name: newBoardName });
      setNewBoardName('');
      setShowCreate(false);
      await loadBoards();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create board');
    } finally {
      setCreating(false);
    }
  };

  const handleDelete = async (boardId: string, name: string) => {
    if (!confirm(`Delete board "${name}"? This permanently removes all columns, cards, and participants.`))
      return;
    try {
      await service.deleteBoard(boardId);
      await loadBoards();
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to delete board');
    }
  };

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50">
        <Loader2 className="animate-spin text-slate-400" size={32} />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Header */}
      <header className="bg-white border-b border-slate-200">
        <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="flex items-center justify-center w-10 h-10 rounded-lg bg-slate-800 text-white">
              <Kanban size={24} />
            </div>
            <div>
              <h1 className="text-lg font-bold text-slate-800">Mini Kanban</h1>
              <p className="text-xs text-slate-500">Your boards</p>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <Avatar name={user?.name ?? 'User'} size="sm" />
              <span className="text-sm font-medium text-slate-700 hidden sm:inline">
                {user?.name}
              </span>
            </div>
            <Button variant="ghost" size="sm" onClick={handleLogout}>
              <LogOut size={16} />
              <span className="hidden sm:inline">Sign out</span>
            </Button>
          </div>
        </div>
      </header>

      {/* Content */}
      <main className="max-w-6xl mx-auto px-6 py-8">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-2xl font-bold text-slate-800">Boards</h2>
            <p className="text-sm text-slate-500 mt-1">
              {boards.length} of 10 boards used
            </p>
          </div>
          <Button onClick={() => setShowCreate(true)} disabled={boards.length >= 10}>
            <Plus size={18} />
            New board
          </Button>
        </div>

        {boards.length === 0 ? (
          <div className="text-center py-20">
            <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-slate-100 text-slate-400 mb-4">
              <Kanban size={32} />
            </div>
            <h3 className="text-lg font-semibold text-slate-700">No boards yet</h3>
            <p className="text-sm text-slate-500 mt-1 mb-4">
              Create your first board to start organizing tasks.
            </p>
            <Button onClick={() => setShowCreate(true)}>
              <Plus size={18} />
              Create board
            </Button>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {boards.map(({ board, participantCount, role }) => (
              <div
                key={board.id}
                className="group bg-white rounded-xl border border-slate-200 p-5 hover:border-slate-300 hover:shadow-md transition-all duration-200 cursor-pointer"
                onClick={() => navigate(`/board/${board.id}`)}
              >
                <div className="flex items-start justify-between mb-3">
                  <h3 className="text-base font-semibold text-slate-800 line-clamp-1">
                    {board.name}
                  </h3>
                  {role === 'owner' ? (
                    <span className="inline-flex items-center gap-1 text-xs font-medium text-amber-600 bg-amber-50 px-2 py-0.5 rounded-full">
                      <Crown size={12} />
                      Owner
                    </span>
                  ) : (
                    <span className="text-xs font-medium text-slate-500 bg-slate-100 px-2 py-0.5 rounded-full">
                      Participant
                    </span>
                  )}
                </div>
                <div className="flex items-center gap-4 text-sm text-slate-500">
                  <span className="flex items-center gap-1">
                    <Users size={14} />
                    {participantCount} participant{participantCount !== 1 ? 's' : ''}
                  </span>
                  <span className="flex items-center gap-1 text-xs">
                    <Crown size={12} />
                    {board.ownerName}
                  </span>
                </div>
                {role === 'owner' && (
                  <div className="mt-3 flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={(e) => {
                        e.stopPropagation();
                        const newName = prompt('Rename board:', board.name);
                        if (newName && newName.trim()) {
                          service
                            .updateBoard(board.id, { name: newName.trim() })
                            .then(loadBoards)
                            .catch((err) => alert(err.message));
                        }
                      }}
                    >
                      <Pencil size={14} />
                      Rename
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleDelete(board.id, board.name);
                      }}
                    >
                      <Trash2 size={14} />
                      Delete
                    </Button>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </main>

      {/* Create board modal */}
      <Modal open={showCreate} onClose={() => setShowCreate(false)} title="Create new board">
        <form onSubmit={handleCreate} className="space-y-4">
          <Input
            label="Board name"
            type="text"
            value={newBoardName}
            onChange={(e) => setNewBoardName(e.target.value)}
            placeholder="My project board"
            autoFocus
            error={error}
          />
          <p className="text-xs text-slate-500">
            The board will start with three columns: To Do, In Progress, and Done.
          </p>
          <div className="flex gap-3 justify-end">
            <Button type="button" variant="secondary" onClick={() => setShowCreate(false)}>
              Cancel
            </Button>
            <Button type="submit" disabled={creating || !newBoardName.trim()}>
              {creating ? (
                <>
                  <Loader2 size={16} className="animate-spin" />
                  Creating...
                </>
              ) : (
                'Create board'
              )}
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
