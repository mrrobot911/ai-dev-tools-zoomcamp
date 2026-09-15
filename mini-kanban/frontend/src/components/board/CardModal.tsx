import { useState, useEffect, type FormEvent } from 'react';
import type { Card, Participant } from '@/types';
import { Modal, Input, Textarea, Select, Button } from '@/components/ui';
import { Loader2, Trash2 } from 'lucide-react';

interface CardModalProps {
  open: boolean;
  onClose: () => void;
  card: Card | null;
  columnId: string;
  participants: Participant[];
  onSave: (data: {
    title: string;
    description: string;
    assigneeId: string | null;
  }) => Promise<void>;
  onDelete?: () => Promise<void>;
  canDelete: boolean;
}

export function CardModal({
  open,
  onClose,
  card,
  columnId,
  participants,
  onSave,
  onDelete,
  canDelete,
}: CardModalProps) {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [assigneeId, setAssigneeId] = useState<string>('');
  const [saving, setSaving] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (card) {
      setTitle(card.title);
      setDescription(card.description);
      setAssigneeId(card.assigneeId ?? '');
    } else {
      setTitle('');
      setDescription('');
      setAssigneeId('');
    }
    setError('');
  }, [card, open]);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim()) {
      setError('Title is required');
      return;
    }
    setSaving(true);
    setError('');
    try {
      await onSave({
        title: title.trim(),
        description: description.trim(),
        assigneeId: assigneeId || null,
      });
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save card');
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (): Promise<void> => {
    if (!confirm('Delete this card?')) return;
    setDeleting(true);
    try {
      await onDelete?.();
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete card');
    } finally {
      setDeleting(false);
    }
  };

  return (
    <Modal
      open={open}
      onClose={onClose}
      title={card ? 'Edit card' : 'New card'}
    >
      <form onSubmit={handleSave} className="space-y-4">
        <Input
          label="Title"
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="Card title"
          autoFocus
          error={error}
        />
        <Textarea
          label="Description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="Add more details..."
          rows={4}
        />
        <Select
          label="Assignee"
          value={assigneeId}
          onChange={(e) => setAssigneeId(e.target.value)}
        >
          <option value="">Unassigned</option>
          {participants.map((p) => (
            <option key={p.userId} value={p.userId}>
              {p.name} {p.role === 'owner' ? '(Owner)' : ''}
            </option>
          ))}
        </Select>

        {card && (
          <div className="pt-2 text-xs text-slate-400 space-y-0.5">
            <p>Created by {card.creatorName}</p>
            <p>Created: {new Date(card.createdAt).toLocaleString()}</p>
            <p>Updated: {new Date(card.updatedAt).toLocaleString()}</p>
          </div>
        )}

        <div className="flex items-center justify-between pt-2">
          {card && canDelete ? (
            <Button
              type="button"
              variant="danger"
              size="sm"
              onClick={handleDelete}
              disabled={deleting}
            >
              {deleting ? (
                <Loader2 size={14} className="animate-spin" />
              ) : (
                <Trash2 size={14} />
              )}
              Delete
            </Button>
          ) : (
            <span />
          )}
          <div className="flex gap-3">
            <Button type="button" variant="secondary" onClick={onClose}>
              Cancel
            </Button>
            <Button type="submit" disabled={saving}>
              {saving ? (
                <Loader2 size={16} className="animate-spin" />
              ) : card ? (
                'Save changes'
              ) : (
                'Create card'
              )}
            </Button>
          </div>
        </div>
      </form>
    </Modal>
  );
}
