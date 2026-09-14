import { Link } from 'react-router-dom';

export default function HomePage() {
  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <header style={{ padding: '16px 32px', borderBottom: '1px solid var(--color-border)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <span style={{ fontSize: 20, fontWeight: 800 }}>System Design Interview</span>
        </div>
      </header>

      <main
        style={{
          flex: 1,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          padding: '40px 20px',
          textAlign: 'center',
        }}
      >
        <h1
          style={{
            fontSize: 'clamp(32px, 5vw, 48px)',
            fontWeight: 800,
            lineHeight: 1.2,
            maxWidth: 600,
            marginBottom: 16,
          }}
        >
          Conduct collaborative system design interviews
        </h1>
        <p
          style={{
            fontSize: 18,
            color: 'var(--color-text-muted)',
            maxWidth: 500,
            marginBottom: 40,
          }}
        >
          Create a session, share the join code, and collaborate on architecture
          diagrams in real time.
        </p>
        <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap', justifyContent: 'center' }}>
          <Link to="/create">
            <button className="btn btn-primary" style={{ padding: '14px 28px', fontSize: 16 }}>
              Create a Session
            </button>
          </Link>
          <Link to="/join">
            <button className="btn btn-ghost" style={{ padding: '14px 28px', fontSize: 16 }}>
              Join with Code
            </button>
          </Link>
        </div>
      </main>
    </div>
  );
}
