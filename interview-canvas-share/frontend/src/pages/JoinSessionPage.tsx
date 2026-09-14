import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { getServices } from '../services';

export default function JoinSessionPage() {
  const navigate = useNavigate();
  const [joinCode, setJoinCode] = useState('');
  const [candidateName, setCandidateName] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);

    if (!joinCode.trim() || !candidateName.trim()) {
      setError('Join code and your name are required.');
      return;
    }

    setLoading(true);
    const result = await getServices().session.joinSession({
      joinCode: joinCode.trim().toUpperCase(),
      candidateName: candidateName.trim(),
    });
    setLoading(false);

    if (result.error || !result.data) {
      setError(result.error ?? 'Failed to join session.');
      return;
    }

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
        <span style={{ fontSize: 18, fontWeight: 700 }}>Join Session</span>
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
            Join an interview
          </h2>
          <p style={{ color: 'var(--color-text-muted)', marginBottom: 24, fontSize: 14 }}>
            Enter the code your interviewer shared with you.
          </p>

          <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
            <div>
              <label className="label" htmlFor="code">Join code *</label>
              <input
                id="code"
                className="input"
                value={joinCode}
                onChange={(e) => setJoinCode(e.target.value.toUpperCase())}
                placeholder="e.g. AB12CD"
                style={{ fontFamily: 'var(--font-mono)', letterSpacing: 2, textTransform: 'uppercase' }}
                autoFocus
              />
            </div>

            <div>
              <label className="label" htmlFor="name">Your name *</label>
              <input
                id="name"
                className="input"
                value={candidateName}
                onChange={(e) => setCandidateName(e.target.value)}
                placeholder="Candidate name"
              />
            </div>

            {error && <p className="error-text">{error}</p>}

            <button type="submit" className="btn btn-primary" disabled={loading}>
              {loading ? 'Joining...' : 'Join Session'}
            </button>
          </form>
        </div>
      </main>
    </div>
  );
}
