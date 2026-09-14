import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { getServices } from '../services';

export default function CreateSessionPage() {
  const navigate = useNavigate();
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [interviewerName, setInterviewerName] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);

    if (!title.trim() || !interviewerName.trim()) {
      setError('Session title and your name are required.');
      return;
    }

    setLoading(true);
    const result = await getServices().session.createSession({
      title: title.trim(),
      description: description.trim(),
      interviewerName: interviewerName.trim(),
    });
    setLoading(false);

    if (result.error || !result.data) {
      setError(result.error ?? 'Failed to create session.');
      return;
    }

    getServices().auth.setCurrentParticipant(result.data.participant);
    navigate(`/session/${result.data.session.id}`);
  }

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <header
        style={{
          padding: '16px 32px',
          borderBottom: '1px solid var(--color-border)',
          display: 'flex',
          alignItems: 'center',
          gap: 16,
        }}
      >
        <Link to="/" style={{ textDecoration: 'none' }}>
          <button className="btn btn-ghost btn-sm">← Back</button>
        </Link>
        <span style={{ fontSize: 18, fontWeight: 700 }}>Create Session</span>
      </header>

      <main
        style={{
          flex: 1,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          padding: 20,
        }}
      >
        <div className="card fade-in" style={{ width: '100%', maxWidth: 480 }}>
          <h2 style={{ fontSize: 24, fontWeight: 700, marginBottom: 8 }}>
            Start a new interview
          </h2>
          <p style={{ color: 'var(--color-text-muted)', marginBottom: 24, fontSize: 14 }}>
            You'll get a join code to share with your candidate.
          </p>

          <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
            <div>
              <label className="label" htmlFor="title">Session title *</label>
              <input
                id="title"
                className="input"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="e.g. Design a URL shortener"
                autoFocus
              />
            </div>

            <div>
              <label className="label" htmlFor="description">Description (optional)</label>
              <textarea
                id="description"
                className="input"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Brief context or requirements for the candidate"
                rows={3}
              />
            </div>

            <div>
              <label className="label" htmlFor="name">Your name *</label>
              <input
                id="name"
                className="input"
                value={interviewerName}
                onChange={(e) => setInterviewerName(e.target.value)}
                placeholder="Interviewer name"
              />
            </div>

            {error && <p className="error-text">{error}</p>}

            <button type="submit" className="btn btn-primary" disabled={loading}>
              {loading ? 'Creating...' : 'Create Session'}
            </button>
          </form>
        </div>
      </main>
    </div>
  );
}
