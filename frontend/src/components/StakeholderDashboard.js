import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getSession } from '../services/api';

const PHASES = {
  1: 'Open Discovery - Tell me about your work',
  2: 'Targeted Follow-ups - Filling in the gaps',
  3: 'Validation - Confirming understanding',
  4: 'Future State - Defining success',
};

const styles = {
  page: {
    minHeight: '100vh',
    background: 'linear-gradient(160deg, #f0f9ff 0%, #e0f2fe 40%, #f5f3ff 100%)',
    padding: '32px 24px',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
  },
  container: {
    width: '100%',
    maxWidth: 560,
  },
  header: {
    marginBottom: 32,
    textAlign: 'center',
  },
  welcome: {
    margin: 0,
    fontSize: 28,
    fontWeight: 600,
    color: '#0f172a',
    lineHeight: 1.3,
  },
  card: {
    background: '#fff',
    borderRadius: 16,
    boxShadow: '0 4px 24px rgba(0,0,0,0.06)',
    padding: 32,
    marginBottom: 24,
  },
  cardTitle: {
    margin: '0 0 8px 0',
    fontSize: 16,
    fontWeight: 600,
    color: '#64748b',
    textTransform: 'uppercase',
    letterSpacing: '0.04em',
  },
  projectName: {
    margin: '0 0 12px 0',
    fontSize: 20,
    fontWeight: 600,
    color: '#0f172a',
  },
  scope: {
    margin: 0,
    fontSize: 15,
    color: '#475569',
    lineHeight: 1.5,
  },
  statusSection: {
    marginTop: 24,
    paddingTop: 24,
    borderTop: '1px solid #e2e8f0',
    textAlign: 'center',
  },
  statusTitle: {
    margin: '0 0 8px 0',
    fontSize: 18,
    fontWeight: 600,
    color: '#0f172a',
  },
  statusSub: {
    margin: '0 0 20px 0',
    fontSize: 15,
    color: '#64748b',
    lineHeight: 1.4,
  },
  checkmark: {
    display: 'inline-flex',
    alignItems: 'center',
    justifyContent: 'center',
    width: 56,
    height: 56,
    borderRadius: '50%',
    background: 'linear-gradient(135deg, #10b981, #059669)',
    color: '#fff',
    fontSize: 28,
    marginBottom: 16,
  },
  ctaBtn: {
    display: 'inline-block',
    padding: '16px 32px',
    fontSize: 17,
    fontWeight: 600,
    color: '#fff',
    background: 'linear-gradient(135deg, #2563eb, #8b5cf6)',
    border: 'none',
    borderRadius: 12,
    cursor: 'pointer',
    boxShadow: '0 4px 20px rgba(37, 99, 235, 0.35)',
    textDecoration: 'none',
  },
  ctaBtnSecondary: {
    background: '#f1f5f9',
    color: '#334155',
    boxShadow: 'none',
  },
  error: {
    padding: 12,
    marginBottom: 24,
    background: '#fef2f2',
    border: '1px solid #fecaca',
    borderRadius: 10,
    fontSize: 14,
    color: '#b91c1c',
    width: '100%',
    maxWidth: 560,
  },
  loading: {
    textAlign: 'center',
    padding: 48,
    fontSize: 16,
    color: '#64748b',
  },
};

function StakeholderDashboard() {
  const [user, setUser] = useState(null);
  const [session, setSession] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    const raw = localStorage.getItem('user');
    if (raw) {
      try {
        setUser(JSON.parse(raw));
      } catch (_) {}
    }
  }, []);

  useEffect(() => {
    let cancelled = false;
    const load = async () => {
      setError('');
      try {
        const res = await getSession();
        if (!cancelled) setSession(res.data);
      } catch (err) {
        if (cancelled) return;
        const detail = err.response?.data?.detail;
        setError(Array.isArray(detail) ? detail.join(' ') : detail || 'Failed to load session.');
      } finally {
        if (!cancelled) setLoading(false);
      }
    };
    load();
    return () => { cancelled = true; };
  }, []);

  const handleBeginResume = () => navigate('/session');
  const handleViewReport = () => navigate('/session');

  if (loading) {
    return (
      <div style={styles.page}>
        <div style={styles.loading}>Loading…</div>
      </div>
    );
  }

  const phase = session?.current_phase ?? 1;
  const phaseNum = Math.min(4, Math.max(1, phase));
  const status = session?.status ?? 'NOT_STARTED';
  const isComplete = status === 'COMPLETED';

  return (
    <div style={styles.page}>
      <div style={styles.container}>
        <header style={styles.header}>
          <h1 style={styles.welcome}>Welcome back, {user?.name ?? 'there'}</h1>
        </header>

        {error && <div style={styles.error}>{error}</div>}

        <div style={styles.card}>
          <div style={styles.cardTitle}>Your discovery</div>
          <h2 style={styles.projectName}>Your Discovery Session</h2>
          <p style={styles.scope}>
            Work through four phases with your solution architect to capture context, validate understanding, and define success.
          </p>

          <div style={styles.statusSection}>
            {status === 'NOT_STARTED' && (
              <>
                <h3 style={styles.statusTitle}>Ready to begin your discovery session?</h3>
                <p style={styles.statusSub}>
                  You'll have a guided conversation across four phases. Start whenever you're ready.
                </p>
                <button type="button" style={styles.ctaBtn} onClick={handleBeginResume}>
                  Begin Discovery
                </button>
              </>
            )}

            {status === 'IN_PROGRESS' && (
              <>
                <h3 style={styles.statusTitle}>You're on Phase {phaseNum} of 4</h3>
                <p style={styles.statusSub}>{PHASES[phaseNum]}</p>
                <button type="button" style={styles.ctaBtn} onClick={handleBeginResume}>
                  Resume Discovery
                </button>
              </>
            )}

            {isComplete && (
              <>
                <div style={styles.checkmark}>✓</div>
                <h3 style={styles.statusTitle}>Discovery Complete!</h3>
                <p style={styles.statusSub}>
                  Your discovery session is finished. View your report to see the summary.
                </p>
                <button type="button" style={styles.ctaBtn} onClick={handleViewReport}>
                  View Report
                </button>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default StakeholderDashboard;
