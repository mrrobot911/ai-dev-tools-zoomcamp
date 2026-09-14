import { useEffect, useState, useRef, useCallback } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { getServices } from '../services';
import type { Session, SessionParticipant, DiagramState, Note, SessionEvent, NoteVisibility } from '../types';
import DiagramEditor from '../components/DiagramEditor';
import NotesPanel from '../components/NotesPanel';
import EventLog from '../components/EventLog';

export default function WorkspacePage() {
  const { sessionId } = useParams<{ sessionId: string }>();
  const navigate = useNavigate();

  const [session, setSession] = useState<Session | null>(null);
  const [participant, setParticipant] = useState<SessionParticipant | null>(null);
  const [diagram, setDiagram] = useState<DiagramState>({ elements: [] });
  const [notes, setNotes] = useState<Note[]>([]);
  const [events, setEvents] = useState<SessionEvent[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [showCompleteConfirm, setShowCompleteConfirm] = useState(false);
  const [rightPanel, setRightPanel] = useState<'notes' | 'activity'>('notes');
  const [copied, setCopied] = useState(false);

  const abortRef = useRef<AbortController | null>(null);

  const loadAll = useCallback(async () => {
    if (!sessionId) return;
    const svc = getServices();
    const currentParticipant = svc.auth.getCurrentParticipant();
    if (!currentParticipant) {
      setError('No participant found. Please create or join a session.');
      setLoading(false);
      return;
    }

    const [sessionRes, diagramRes, notesRes, eventsRes] = await Promise.all([
      svc.session.getSession(sessionId),
      svc.diagram.getDiagram(sessionId),
      svc.note.getNotes(sessionId, currentParticipant.id),
      svc.event.getEvents(sessionId),
    ]);

    if (sessionRes.error || !sessionRes.data) {
      setError(sessionRes.error ?? 'Session not found.');
      setLoading(false);
      return;
    }

    setSession(sessionRes.data);
    setParticipant(currentParticipant);
    setDiagram(diagramRes.data ?? { elements: [] });
    setNotes(notesRes.data ?? []);
    setEvents(eventsRes.data ?? []);
    setLoading(false);
  }, [sessionId]);

  useEffect(() => {
    loadAll();
  }, [loadAll]);

  useEffect(() => {
    if (!sessionId) return;
    const svc = getServices();
    const controller = new AbortController();
    abortRef.current = controller;

    let unsubSession: (() => void) | undefined;
    let unsubDiagram: (() => void) | undefined;
    let unsubEvents: (() => void) | undefined;
    let unsubNotes: (() => void) | undefined;

    svc.session.subscribeToSession(
      sessionId,
      (s) => setSession(s),
      { signal: controller.signal },
    ).then((unsub) => { unsubSession = unsub; });

    svc.diagram.subscribeToDiagram(
      sessionId,
      (d) => setDiagram(d),
      { signal: controller.signal },
    ).then((unsub) => { unsubDiagram = unsub; });

    svc.event.subscribeToEvents(
      sessionId,
      (e) => setEvents((prev) => [...prev, e]),
      { signal: controller.signal },
    ).then((unsub) => { unsubEvents = unsub; });

    if (participant) {
      svc.note.subscribeToNotes(
        sessionId,
        participant.id,
        (n) => setNotes(n),
        { signal: controller.signal },
      ).then((unsub) => { unsubNotes = unsub; });
    }

    return () => {
      controller.abort();
      unsubSession?.();
      unsubDiagram?.();
      unsubEvents?.();
      unsubNotes?.();
    };
  }, [sessionId, participant]);

  const handleAddElement = useCallback(
    (element: Omit<import('../types').DiagramElement, 'id'>) => {
      if (!sessionId || !participant) return;
      getServices().diagram.addElement(sessionId, element, participant.id);
    },
    [sessionId, participant],
  );

  const handleUpdateElement = useCallback(
    (elementId: string, updates: Partial<import('../types').DiagramElement>) => {
      if (!sessionId || !participant) return;
      getServices().diagram.updateElement(sessionId, elementId, updates, participant.id);
    },
    [sessionId, participant],
  );

  const handleRemoveElement = useCallback(
    (elementId: string) => {
      if (!sessionId || !participant) return;
      getServices().diagram.removeElement(sessionId, elementId, participant.id);
    },
    [sessionId, participant],
  );

  const handleAddNote = useCallback(
    (content: string, visibility: NoteVisibility) => {
      if (!sessionId || !participant) return;
      getServices().note.addNote({
        sessionId,
        authorId: participant.id,
        authorName: participant.name,
        content,
        visibility,
      });
    },
    [sessionId, participant],
  );

  const handleUpdateNote = useCallback(
    (noteId: string, content: string) => {
      if (!participant) return;
      getServices().note.updateNote(noteId, { content }, participant.id);
    },
    [participant],
  );

  const handleRemoveNote = useCallback(
    (noteId: string) => {
      if (!participant) return;
      getServices().note.removeNote(noteId, participant.id);
    },
    [participant],
  );

  async function handleComplete() {
    if (!sessionId) return;
    await getServices().session.completeSession(sessionId);
    setShowCompleteConfirm(false);
  }

  function handleLeave() {
    getServices().auth.clearCurrentParticipant();
    navigate('/');
  }

  function copyJoinCode() {
    if (!session) return;
    navigator.clipboard.writeText(session.joinCode).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  }

  if (loading) {
    return (
      <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <p style={{ color: 'var(--color-text-muted)' }}>Loading session...</p>
      </div>
    );
  }

  if (error || !session || !participant) {
    return (
      <div
        style={{
          minHeight: '100vh',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          gap: 16,
        }}
      >
        <p className="error-text" style={{ fontSize: 16 }}>{error ?? 'Something went wrong.'}</p>
        <Link to="/">
          <button className="btn btn-primary">Go Home</button>
        </Link>
      </div>
    );
  }

  const isInterviewer = participant.role === 'interviewer';
  const isCompleted = session.status === 'completed';

  return (
    <div style={{ height: '100vh', display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
      <header
        style={{
          padding: '12px 20px',
          borderBottom: '1px solid var(--color-border)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          gap: 16,
          flexShrink: 0,
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 12, minWidth: 0 }}>
          <span
            style={{
              fontSize: 11,
              fontWeight: 700,
              padding: '3px 8px',
              borderRadius: 4,
              background: isInterviewer ? 'rgba(59,130,246,0.15)' : 'rgba(16,185,129,0.15)',
              color: isInterviewer ? 'var(--color-primary-light)' : 'var(--color-accent)',
              whiteSpace: 'nowrap',
            }}
          >
            {isInterviewer ? 'INTERVIEWER' : 'CANDIDATE'}
          </span>
          <h1 style={{ fontSize: 16, fontWeight: 700, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
            {session.title}
          </h1>
          {isCompleted && (
            <span
              style={{
                fontSize: 11,
                fontWeight: 700,
                padding: '3px 8px',
                borderRadius: 4,
                background: 'rgba(239,68,68,0.15)',
                color: 'var(--color-error)',
                whiteSpace: 'nowrap',
              }}
            >
              COMPLETED
            </span>
          )}
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          {/* Participants */}
          <div style={{ display: 'flex', gap: 4 }}>
            {session.participants.map((p) => (
              <span
                key={p.id}
                title={p.name}
                style={{
                  width: 30,
                  height: 30,
                  borderRadius: '50%',
                  background: p.role === 'interviewer' ? 'var(--color-primary)' : 'var(--color-accent)',
                  color: '#fff',
                  fontSize: 12,
                  fontWeight: 700,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  border: '2px solid var(--color-surface)',
                }}
              >
                {p.name.charAt(0).toUpperCase()}
              </span>
            ))}
          </div>

          {/* Join code */}
          {isInterviewer && !isCompleted && (
            <button
              onClick={copyJoinCode}
              className="btn btn-ghost btn-sm"
              title="Click to copy"
              style={{ fontFamily: 'var(--font-mono)', letterSpacing: 1 }}
            >
              {copied ? 'Copied!' : `Code: ${session.joinCode}`}
            </button>
          )}

          {/* Actions */}
          {isInterviewer && !isCompleted && (
            <button
              className="btn btn-danger btn-sm"
              onClick={() => setShowCompleteConfirm(true)}
            >
              Finish
            </button>
          )}
          <button className="btn btn-ghost btn-sm" onClick={handleLeave}>
            Leave
          </button>
        </div>
      </header>

      {/* Main content */}
      <div style={{ flex: 1, display: 'flex', overflow: 'hidden' }}>
        {/* Diagram */}
        <div style={{ flex: 1, position: 'relative', borderRight: '1px solid var(--color-border)' }}>
          <DiagramEditor
            state={diagram}
            onAddElement={handleAddElement}
            onUpdateElement={handleUpdateElement}
            onRemoveElement={handleRemoveElement}
            readonly={isCompleted}
          />
        </div>

        {/* Right panel */}
        <div
          style={{
            width: 340,
            display: 'flex',
            flexDirection: 'column',
            background: 'var(--color-surface)',
            flexShrink: 0,
          }}
        >
          {/* Tabs */}
          <div style={{ display: 'flex', borderBottom: '1px solid var(--color-border)' }}>
            <button
              onClick={() => setRightPanel('notes')}
              style={{
                flex: 1,
                padding: '10px',
                fontSize: 13,
                fontWeight: 600,
                borderBottom: rightPanel === 'notes' ? '2px solid var(--color-primary)' : '2px solid transparent',
                color: rightPanel === 'notes' ? 'var(--color-text)' : 'var(--color-text-muted)',
                transition: 'all 0.15s ease',
              }}
            >
              Notes
            </button>
            <button
              onClick={() => setRightPanel('activity')}
              style={{
                flex: 1,
                padding: '10px',
                fontSize: 13,
                fontWeight: 600,
                borderBottom: rightPanel === 'activity' ? '2px solid var(--color-primary)' : '2px solid transparent',
                color: rightPanel === 'activity' ? 'var(--color-text)' : 'var(--color-text-muted)',
                transition: 'all 0.15s ease',
              }}
            >
              Activity
            </button>
          </div>

          {/* Panel content */}
          <div style={{ flex: 1, overflow: 'hidden' }}>
            {rightPanel === 'notes' ? (
              <NotesPanel
                notes={notes}
                currentParticipantId={participant.id}
                onAddNote={handleAddNote}
                onUpdateNote={handleUpdateNote}
                onRemoveNote={handleRemoveNote}
                sessionId={session.id}
              />
            ) : (
              <EventLog events={events} />
            )}
          </div>
        </div>
      </div>

      {/* Complete confirmation modal */}
      {showCompleteConfirm && (
        <div
          onClick={() => setShowCompleteConfirm(false)}
          style={{
            position: 'fixed',
            inset: 0,
            background: 'rgba(0,0,0,0.5)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 100,
          }}
        >
          <div
            className="fade-in"
            onClick={(e) => e.stopPropagation()}
            style={{
              background: 'var(--color-surface)',
              border: '1px solid var(--color-border)',
              borderRadius: 'var(--radius-lg)',
              padding: 28,
              maxWidth: 400,
              width: '90%',
            }}
          >
            <h2 style={{ fontSize: 20, fontWeight: 700, marginBottom: 8 }}>Finish session?</h2>
            <p style={{ color: 'var(--color-text-muted)', marginBottom: 24, fontSize: 14 }}>
              This will mark the session as completed. The diagram will become read-only.
            </p>
            <div style={{ display: 'flex', gap: 10, justifyContent: 'flex-end' }}>
              <button className="btn btn-ghost" onClick={() => setShowCompleteConfirm(false)}>
                Cancel
              </button>
              <button className="btn btn-danger" onClick={handleComplete}>
                Finish Session
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
