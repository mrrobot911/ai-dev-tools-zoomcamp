import { useState } from 'react';
import type { Note, NoteVisibility } from '../types';

interface NotesPanelProps {
  notes: Note[];
  onAddNote: (content: string, visibility: NoteVisibility) => void;
  onUpdateNote: (noteId: string, content: string) => void;
  onRemoveNote: (noteId: string) => void;
}

export default function NotesPanel({
  notes,
  onAddNote,
  onUpdateNote,
  onRemoveNote,
}: NotesPanelProps) {
  const [newContent, setNewContent] = useState('');
  const [newVisibility, setNewVisibility] = useState<NoteVisibility>('private');
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editContent, setEditContent] = useState('');

  function handleAdd() {
    if (!newContent.trim()) return;
    onAddNote(newContent.trim(), newVisibility);
    setNewContent('');
  }

  function startEdit(note: Note) {
    setEditingId(note.id);
    setEditContent(note.content);
  }

  function saveEdit() {
    if (editingId && editContent.trim()) {
      onUpdateNote(editingId, editContent.trim());
    }
    setEditingId(null);
    setEditContent('');
  }

  const sorted = [...notes].sort((a, b) => b.updatedAt - a.updatedAt);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      <div style={{ padding: '12px 16px', borderBottom: '1px solid var(--color-border)' }}>
        <h3 style={{ fontSize: 14, fontWeight: 700, marginBottom: 10 }}>Add Note</h3>
        <textarea
          className="input"
          value={newContent}
          onChange={(e) => setNewContent(e.target.value)}
          placeholder="Write a note..."
          rows={2}
          style={{ fontSize: 13 }}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) {
              handleAdd();
            }
          }}
        />
        <div style={{ display: 'flex', gap: 8, marginTop: 8, alignItems: 'center' }}>
          <select
            className="input"
            value={newVisibility}
            onChange={(e) => setNewVisibility(e.target.value as NoteVisibility)}
            style={{ width: 'auto', fontSize: 13, padding: '6px 10px' }}
          >
            <option value="private">Private</option>
            <option value="shared">Shared</option>
          </select>
          <button className="btn btn-primary btn-sm" onClick={handleAdd} disabled={!newContent.trim()}>
            Add
          </button>
        </div>
      </div>

      <div style={{ flex: 1, overflowY: 'auto', padding: '8px 16px' }}>
        {sorted.length === 0 ? (
          <p style={{ color: 'var(--color-text-muted)', fontSize: 13, textAlign: 'center', marginTop: 20 }}>
            No notes yet.
          </p>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {sorted.map((note) => {
              const isEditing = editingId === note.id;
              return (
                <div
                  key={note.id}
                  className="fade-in"
                  style={{
                    background: 'var(--color-surface-2)',
                    border: '1px solid var(--color-border)',
                    borderRadius: 'var(--radius-md)',
                    padding: 10,
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}>
                    <span style={{ fontSize: 12, color: 'var(--color-text-muted)' }}>
                      {note.authorName}
                    </span>
                    <span
                      style={{
                        fontSize: 10,
                        fontWeight: 600,
                        padding: '2px 8px',
                        borderRadius: 4,
                        background: note.visibility === 'shared' ? 'rgba(16,185,129,0.15)' : 'rgba(139,145,167,0.15)',
                        color: note.visibility === 'shared' ? 'var(--color-accent)' : 'var(--color-text-muted)',
                      }}
                    >
                      {note.visibility === 'shared' ? 'SHARED' : 'PRIVATE'}
                    </span>
                  </div>
                  {isEditing ? (
                    <div>
                      <textarea
                        className="input"
                        value={editContent}
                        onChange={(e) => setEditContent(e.target.value)}
                        rows={2}
                        style={{ fontSize: 13 }}
                        autoFocus
                      />
                      <div style={{ display: 'flex', gap: 6, marginTop: 6 }}>
                        <button className="btn btn-primary btn-sm" onClick={saveEdit}>Save</button>
                        <button className="btn btn-ghost btn-sm" onClick={() => setEditingId(null)}>Cancel</button>
                      </div>
                    </div>
                  ) : (
                    <>
                      <p style={{ fontSize: 13, whiteSpace: 'pre-wrap', wordBreak: 'break-word' }}>
                        {note.content}
                      </p>
                      <div style={{ display: 'flex', gap: 6, marginTop: 6 }}>
                        <button className="btn btn-ghost btn-sm" onClick={() => startEdit(note)}>Edit</button>
                        <button className="btn btn-ghost btn-sm" onClick={() => onRemoveNote(note.id)}>Delete</button>
                      </div>
                    </>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
