import { useState, useEffect, useCallback, useMemo } from 'react';
import {
  DndContext,
  DragOverlay,
  PointerSensor,
  useSensor,
  useSensors,
  type DragStartEvent,
  type DragEndEvent,
  closestCorners,
} from '@dnd-kit/core';
import {
  SortableContext,
  horizontalListSortingStrategy,
  arrayMove,
} from '@dnd-kit/sortable';
import { useAuth } from '@/context/AuthContext';
import { useRouter } from '@/hooks/useRouter';
import { service } from '@/services';
import type { BoardWithDetails, Card, Column, Participant } from '@/types';
import { ColumnView } from '@/components/board/ColumnView';
import { CardModal } from '@/components/board/CardModal';
import { Button, Input, Modal, Avatar } from '@/components/ui';
import {
  ArrowLeft,
  Plus,
  Search,
  Users,
  Link2,
  Copy,
  Check,
  Loader2,
  Crown,
  UserMinus,
  LogOut,
  Pencil,
  X,
  AlertTriangle,
} from 'lucide-react';

export function BoardPage({ boardId }: { boardId: string }) {
  const { user } = useAuth();
  const { navigate } = useRouter();
  const [board, setBoard] = useState<BoardWithDetails | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [filterAssignee, setFilterAssignee] = useState<string>('');
  const [activeCardId, setActiveCardId] = useState<string | null>(null);
  const [showCardModal, setShowCardModal] = useState(false);
  const [editingCard, setEditingCard] = useState<Card | null>(null);
  const [targetColumnId, setTargetColumnId] = useState('');
  const [showParticipants, setShowParticipants] = useState(false);
  const [showInvitations, setShowInvitations] = useState(false);
  const [showAddColumn, setShowAddColumn] = useState(false);
  const [editingColumn, setEditingColumn] = useState<Column | null>(null);
  const [newColumnName, setNewColumnName] = useState('');
  const [copiedToken, setCopiedToken] = useState<string | null>(null);
  const [actionError, setActionError] = useState('');
  const [invitations, setInvitations] = useState<{ id: string; token: string; used: boolean }[]>([]);

  const sensors = useSensors(
    useSensor(PointerSensor, { activationConstraint: { distance: 6 } })
  );

  const loadBoard = useCallback(async () => {
    try {
      const b = await service.getBoard(boardId);
      setBoard(b);
      setError('');
    } catch (err) {
      const status = (err as Error & { status?: number }).status;
      if (status === 403) {
        navigate('/access-denied');
        return;
      }
      setError(err instanceof Error ? err.message : 'Failed to load board');
    } finally {
      setLoading(false);
    }
  }, [boardId, navigate]);

  useEffect(() => {
    loadBoard();
  }, [loadBoard]);

  // Filtered cards
  const filteredCards = useMemo(() => {
    if (!board) return [];
    return board.cards.filter((card) => {
      const matchesSearch =
        !searchQuery || card.title.toLowerCase().includes(searchQuery.toLowerCase());
      const matchesAssignee =
        !filterAssignee || card.assigneeId === filterAssignee;
      return matchesSearch && matchesAssignee;
    });
  }, [board, searchQuery, filterAssignee]);

  const cardsByColumn = useMemo(() => {
    const map: Record<string, Card[]> = {};
    if (!board) return map;
    for (const col of board.columns) {
      map[col.id] = filteredCards.filter((c) => c.columnId === col.id);
    }
    return map;
  }, [board, filteredCards]);

  const isOwner = board?.role === 'owner';

  const handleDragStart = (e: DragStartEvent) => {
    setActiveCardId(e.active.id as string);
  };

  const handleDragEnd = async (e: DragEndEvent) => {
    setActiveCardId(null);
    const { active, over } = e;
    if (!over || !board) return;

    const activeData = active.data.current;
    const overData = over.data.current;
    if (!activeData) return;

    // Column reorder
    if (activeData.type === 'column' && overData?.type === 'column') {
      const activeColId = activeData.columnId as string;
      const overColId = overData.columnId as string;
      if (activeColId === overColId) return;
      const oldIndex = board.columns.findIndex((c) => c.id === activeColId);
      const newIndex = board.columns.findIndex((c) => c.id === overColId);
      const newOrder = arrayMove(board.columns, oldIndex, newIndex);
      // Optimistic update
      setBoard({ ...board, columns: newOrder });
      try {
        await service.reorderColumns(boardId, newOrder.map((c) => c.id));
      } catch {
        await loadBoard();
      }
      return;
    }

    // Card move
    if (activeData.type === 'card') {
      const cardId = activeData.cardId as string;
      const card = board.cards.find((c) => c.id === cardId);
      if (!card) return;

      let targetColumnId: string | null = null;
      if (overData?.type === 'column') {
        targetColumnId = overData.columnId;
      } else if (overData?.type === 'card') {
        const overCard = board.cards.find((c) => c.id === overData.cardId);
        if (overCard) targetColumnId = overCard.columnId;
      }

      if (!targetColumnId || targetColumnId === card.columnId) return;

      // Optimistic update
      const updatedCards = board.cards.map((c) =>
        c.id === cardId ? { ...c, columnId: targetColumnId! } : c
      );
      setBoard({ ...board, cards: updatedCards });

      try {
        await service.moveCard(boardId, { cardId, targetColumnId });
      } catch {
        await loadBoard();
      }
    }
  };

  const handleAddCard = (columnId: string) => {
    setEditingCard(null);
    setTargetColumnId(columnId);
    setShowCardModal(true);
  };

  const handleEditCard = (card: Card) => {
    setEditingCard(card);
    setTargetColumnId(card.columnId);
    setShowCardModal(true);
  };

  const handleSaveCard = async (data: {
    title: string;
    description: string;
    assigneeId: string | null;
  }) => {
    setActionError('');
    if (editingCard) {
      await service.updateCard(boardId, editingCard.id, data);
    } else {
      await service.createCard(boardId, {
        boardId,
        columnId: targetColumnId,
        title: data.title,
        description: data.description,
        assigneeId: data.assigneeId,
      });
    }
    await loadBoard();
  };

  const handleDeleteCard = async () => {
    if (!editingCard) return;
    await service.deleteCard(boardId, editingCard.id);
    await loadBoard();
  };

  const handleAddColumn = async (e: React.FormEvent) => {
    e.preventDefault();
    setActionError('');
    try {
      await service.createColumn(boardId, { boardId, name: newColumnName });
      setNewColumnName('');
      setShowAddColumn(false);
      await loadBoard();
    } catch (err) {
      setActionError(err instanceof Error ? err.message : 'Failed to create column');
    }
  };

  const handleEditColumn = (col: Column) => {
    setEditingColumn(col);
    setNewColumnName(col.name);
    setShowAddColumn(true);
  };

  const handleSaveColumn = async (e: React.FormEvent) => {
    e.preventDefault();
    setActionError('');
    try {
      if (editingColumn) {
        await service.updateColumn(boardId, editingColumn.id, { name: newColumnName });
      } else {
        await service.createColumn(boardId, { boardId, name: newColumnName });
      }
      setNewColumnName('');
      setShowAddColumn(false);
      setEditingColumn(null);
      await loadBoard();
    } catch (err) {
      setActionError(err instanceof Error ? err.message : 'Failed to save column');
    }
  };

  const handleDeleteColumn = async (col: Column) => {
    if (!confirm(`Delete column "${col.name}"?`)) return;
    try {
      await service.deleteColumn(boardId, col.id);
      await loadBoard();
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to delete column');
    }
  };

  const loadInvitations = useCallback(async () => {
    try {
 const list = await service.listInvitations(boardId);
      setInvitations(list.map((i) => ({ id: i.id, token: i.token, used: i.used })));
    } catch {
      // ignore
    }
  }, [boardId]);

  useEffect(() => {
    if (showInvitations) loadInvitations();
  }, [showInvitations, loadInvitations]);

  const handleCreateInvitation = async () => {
    try {
      const inv = await service.createInvitation(boardId);
      const url = `${window.location.origin}/#/invite/${inv.token}`;
      await navigator.clipboard.writeText(url);
      setCopiedToken(inv.token);
      setTimeout(() => setCopiedToken(null), 2000);
      await loadInvitations();
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to create invitation');
    }
  };

  const handleRemoveParticipant = async (userId: string) => {
    if (!confirm('Remove this participant from the board?')) return;
    try {
      await service.removeParticipant(boardId, userId);
      await loadBoard();
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to remove participant');
    }
  };

  const handleLeaveBoard = async () => {
    if (!confirm('Leave this board?')) return;
    try {
      await service.leaveBoard(boardId);
      navigate('/dashboard');
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to leave board');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50">
        <Loader2 className="animate-spin text-slate-400" size={32} />
      </div>
    );
  }

  if (error && !board) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50">
        <div className="text-center">
          <AlertTriangle size={32} className="text-amber-500 mx-auto mb-3" />
          <p className="text-slate-700 font-medium">{error}</p>
          <Button className="mt-4" onClick={() => navigate('/dashboard')}>
            Back to dashboard
          </Button>
        </div>
      </div>
    );
  }

  if (!board) return null;

  const activeCard = activeCardId
    ? board.cards.find((c) => `card_${c.id}` === activeCardId)
    : null;

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      {/* Header */}
      <header className="bg-white border-b border-slate-200 shrink-0">
        <div className="px-6 py-3 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Button variant="ghost" size="sm" onClick={() => navigate('/dashboard')}>
              <ArrowLeft size={16} />
              <span className="hidden sm:inline">Dashboard</span>
            </Button>
            <div className="h-6 w-px bg-slate-200" />
            <h1 className="text-lg font-bold text-slate-800">{board.name}</h1>
            {isOwner && (
              <button
                onClick={() => {
                  const newName = prompt('Rename board:', board.name);
                  if (newName && newName.trim()) {
                    service
                      .updateBoard(boardId, { name: newName.trim() })
                      .then(loadBoard)
                      .catch((err) => alert(err.message));
                  }
                }}
                className="p-1 rounded text-slate-400 hover:bg-slate-100 hover:text-slate-600"
              >
                <Pencil size={14} />
              </button>
            )}
          </div>

          <div className="flex items-center gap-2">
            {/* Participants */}
            <div className="flex items-center -space-x-1.5 mr-2">
              {board.participants.slice(0, 5).map((p) => (
                <div key={p.userId} className="ring-2 ring-white rounded-full">
                  <Avatar name={p.name} size="sm" />
                </div>
              ))}
              {board.participants.length > 5 && (
                <div className="ring-2 ring-white rounded-full w-7 h-7 bg-slate-200 text-slate-600 text-xs flex items-center justify-center font-medium">
                  +{board.participants.length - 5}
                </div>
              )}
            </div>
            <Button variant="secondary" size="sm" onClick={() => setShowParticipants(true)}>
              <Users size={14} />
              <span className="hidden sm:inline">Participants</span>
            </Button>
            {isOwner && (
              <Button variant="secondary" size="sm" onClick={() => setShowInvitations(true)}>
                <Link2 size={14} />
                <span className="hidden sm:inline">Invite</span>
              </Button>
            )}
            {!isOwner && (
              <Button variant="ghost" size="sm" onClick={handleLeaveBoard}>
                <LogOut size={14} />
                <span className="hidden sm:inline">Leave</span>
              </Button>
            )}
          </div>
        </div>

        {/* Search & filter bar */}
        <div className="px-6 pb-3 flex items-center gap-3">
          <div className="relative flex-1 max-w-xs">
            <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search cards by title..."
              className="w-full pl-9 pr-3 py-1.5 text-sm rounded-lg border border-slate-300 outline-none focus:border-slate-500 focus:ring-1 focus:ring-slate-500"
            />
            {searchQuery && (
              <button
                onClick={() => setSearchQuery('')}
                className="absolute right-2 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
              >
                <X size={14} />
              </button>
            )}
          </div>
          <select
            value={filterAssignee}
            onChange={(e) => setFilterAssignee(e.target.value)}
            className="text-sm rounded-lg border border-slate-300 px-3 py-1.5 outline-none focus:border-slate-500 focus:ring-1 focus:ring-slate-500"
          >
            <option value="">All assignees</option>
            {board.participants.map((p) => (
              <option key={p.userId} value={p.userId}>
                {p.name}
              </option>
            ))}
          </select>
        </div>
      </header>

      {/* Board content */}
      <div className="flex-1 overflow-x-auto overflow-y-hidden p-4">
        <DndContext
          sensors={sensors}
          collisionDetection={closestCorners}
          onDragStart={handleDragStart}
          onDragEnd={handleDragEnd}
        >
          <div className="flex gap-3 h-full items-start">
            <SortableContext
              items={board.columns.map((c) => `col_${c.id}`)}
              strategy={horizontalListSortingStrategy}
            >
              {board.columns.map((col) => (
                <ColumnView
                  key={col.id}
                  column={col}
                  cards={cardsByColumn[col.id] ?? []}
                  participants={board.participants}
                  role={board.role}
                  currentUserId={user?.id ?? ''}
                  onAddCard={handleAddCard}
                  onEditCard={handleEditCard}
                  onDeleteCard={(card) => {
                    if (confirm(`Delete card "${card.title}"?`)) {
                      service
                        .deleteCard(boardId, card.id)
                        .then(loadBoard)
                        .catch((err) => alert(err.message));
                    }
                  }}
                  onEditColumn={handleEditColumn}
                  onDeleteColumn={handleDeleteColumn}
                />
              ))}
            </SortableContext>

            {/* Add column button */}
            {isOwner && board.columns.length < 10 && (
              <div className="w-72 min-w-[18rem]">
                <button
                  onClick={() => {
                    setEditingColumn(null);
                    setNewColumnName('');
                    setShowAddColumn(true);
                  }}
                  className="w-full flex items-center justify-center gap-2 py-3 rounded-xl border-2 border-dashed border-slate-300 text-slate-500 hover:border-slate-400 hover:text-slate-700 transition-colors"
                >
                  <Plus size={16} />
                  Add column
                </button>
              </div>
            )}
          </div>

          <DragOverlay>
            {activeCard ? (
              <div className="bg-white rounded-lg border border-slate-200 p-3 shadow-lg w-72 opacity-90">
                <p className="text-sm font-medium text-slate-800">{activeCard.title}</p>
                {activeCard.assigneeName && (
                  <p className="text-xs text-slate-500 mt-1">{activeCard.assigneeName}</p>
                )}
              </div>
            ) : null}
          </DragOverlay>
        </DndContext>
      </div>

      {/* Card modal */}
      <CardModal
        open={showCardModal}
        onClose={() => {
          setShowCardModal(false);
          setEditingCard(null);
        }}
        card={editingCard}
        columnId={targetColumnId}
        participants={board.participants}
        onSave={handleSaveCard}
        onDelete={editingCard ? handleDeleteCard : undefined}
        canDelete={editingCard ? isOwner || editingCard.creatorId === user?.id : false}
      />

      {/* Column modal */}
      <Modal
        open={showAddColumn}
        onClose={() => {
          setShowAddColumn(false);
          setEditingColumn(null);
        }}
        title={editingColumn ? 'Rename column' : 'New column'}
      >
        <form onSubmit={handleSaveColumn} className="space-y-4">
          <Input
            label="Column name"
            type="text"
            value={newColumnName}
            onChange={(e) => setNewColumnName(e.target.value)}
            placeholder="Column name"
            autoFocus
            error={actionError}
          />
          <div className="flex gap-3 justify-end">
            <Button
              type="button"
              variant="secondary"
              onClick={() => {
                setShowAddColumn(false);
                setEditingColumn(null);
              }}
            >
              Cancel
            </Button>
            <Button type="submit" disabled={!newColumnName.trim()}>
              {editingColumn ? 'Save' : 'Create'}
            </Button>
          </div>
        </form>
      </Modal>

      {/* Participants modal */}
      <Modal
        open={showParticipants}
        onClose={() => setShowParticipants(false)}
        title="Board participants"
      >
        <div className="space-y-2">
          {board.participants.map((p) => (
            <div
              key={p.userId}
              className="flex items-center justify-between rounded-lg border border-slate-200 px-3 py-2"
            >
              <div className="flex items-center gap-3">
                <Avatar name={p.name} size="md" />
                <div>
                  <p className="text-sm font-medium text-slate-800 flex items-center gap-1">
                    {p.name}
                    {p.role === 'owner' && <Crown size={14} className="text-amber-500" />}
                  </p>
                  <p className="text-xs text-slate-500">{p.email}</p>
                </div>
              </div>
              {isOwner && p.role !== 'owner' && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => handleRemoveParticipant(p.userId)}
                >
                  <UserMinus size={14} />
                </Button>
              )}
            </div>
          ))}
          <div className="pt-2 text-xs text-slate-400">
            {board.participants.length} / 10 participants
          </div>
        </div>
      </Modal>

      {/* Invitations modal */}
      <Modal
        open={showInvitations}
        onClose={() => setShowInvitations(false)}
        title="Invitation links"
      >
        <div className="space-y-4">
          <Button onClick={handleCreateInvitation} disabled={board.participants.length >= 10}>
            <Plus size={16} />
            Generate new link
          </Button>
          <p className="text-xs text-slate-500">
            Each link can be used only once. When a new user registers through the link,
            they automatically join this board.
          </p>
          <div className="space-y-2">
            {invitations.length === 0 ? (
              <p className="text-sm text-slate-400 text-center py-4">
                No invitation links yet
              </p>
            ) : (
              invitations.map((inv) => (
                <div
                  key={inv.id}
                  className="flex items-center justify-between rounded-lg border border-slate-200 px-3 py-2"
                >
                  <div className="flex items-center gap-2 flex-1 min-w-0">
                    <code className="text-xs text-slate-600 truncate">
                      {window.location.origin}/#/invite/{inv.token}
                    </code>
                  </div>
                  <div className="flex items-center gap-2 ml-2">
                    {inv.used ? (
                      <span className="text-xs text-slate-400 bg-slate-100 px-2 py-0.5 rounded-full">
                        Used
                      </span>
                    ) : copiedToken === inv.token ? (
                      <span className="text-xs text-emerald-600 flex items-center gap-1">
                        <Check size={12} />
                        Copied
                      </span>
                    ) : (
                      <button
                        onClick={() => {
                          const url = `${window.location.origin}/#/invite/${inv.token}`;
                          navigator.clipboard.writeText(url);
                          setCopiedToken(inv.token);
                          setTimeout(() => setCopiedToken(null), 2000);
                        }}
                        className="p-1 rounded text-slate-400 hover:bg-slate-100 hover:text-slate-600"
                      >
                        <Copy size={14} />
                      </button>
                    )}
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </Modal>
    </div>
  );
}
