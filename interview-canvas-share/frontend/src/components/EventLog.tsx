import type { SessionEvent } from '../types';

interface EventLogProps {
  events: SessionEvent[];
}

function formatTime(ts: number): string {
  return new Date(ts).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
}

function describeEvent(event: SessionEvent): string {
  switch (event.type) {
    case 'join':
      return `${event.participantName} joined`;
    case 'leave':
      return `${event.participantName} left`;
    case 'element-add':
      return `${event.participantName || 'Someone'} added an element`;
    case 'element-update':
      return `${event.participantName || 'Someone'} updated an element`;
    case 'element-remove':
      return `${event.participantName || 'Someone'} removed an element`;
    case 'note-add':
      return `${event.participantName} added a note`;
    case 'note-update':
      return `${event.participantName} updated a note`;
    case 'note-remove':
      return `${event.participantName} removed a note`;
    case 'session-complete':
      return 'Session completed';
    default:
      return event.type;
  }
}

export default function EventLog({ events }: EventLogProps) {
  const sorted = [...events].sort((a, b) => b.timestamp - a.timestamp);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      <div style={{ padding: '12px 16px', borderBottom: '1px solid var(--color-border)' }}>
        <h3 style={{ fontSize: 14, fontWeight: 700 }}>Activity</h3>
      </div>
      <div style={{ flex: 1, overflowY: 'auto', padding: '8px 16px' }}>
        {sorted.length === 0 ? (
          <p style={{ color: 'var(--color-text-muted)', fontSize: 13, textAlign: 'center', marginTop: 20 }}>
            No activity yet.
          </p>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
            {sorted.map((event) => (
              <div
                key={event.id}
                className="fade-in"
                style={{
                  display: 'flex',
                  gap: 8,
                  fontSize: 12,
                  padding: '4px 0',
                }}
              >
                <span style={{ color: 'var(--color-text-muted)', flexShrink: 0, fontFamily: 'var(--font-mono)' }}>
                  {formatTime(event.timestamp)}
                </span>
                <span style={{ color: 'var(--color-text)' }}>{describeEvent(event)}</span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
