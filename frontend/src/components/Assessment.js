import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { submitAssessment } from '../services/api';

const QUESTIONS = [
  {
    id: 1,
    text: 'When learning about a new system or process, I prefer...',
    A: 'Step-by-step instructions with specific details',
    B: 'An overview of how everything connects',
    C: "Real examples and stories from others who've used it",
    D: 'Focus on what problems it solves',
  },
  {
    id: 2,
    text: "I get frustrated when someone...",
    A: 'Gives me vague answers when I need specifics',
    B: 'Drowns me in details without explaining why it matters',
    C: 'Uses abstract concepts without concrete examples',
    D: 'Focuses on process instead of outcomes',
  },
  {
    id: 3,
    text: 'When explaining something I know well, I naturally...',
    A: 'Walk through it step-by-step with all the details',
    B: 'Start with the big picture and how pieces fit together',
    C: 'Tell a story or give examples from experience',
    D: 'Focus on why it matters and what problem it solves',
  },
  {
    id: 4,
    text: 'When making a decision, I prefer to have...',
    A: 'Specific data points and clear criteria',
    B: 'Understanding of how it affects the whole system',
    C: 'Examples of how similar decisions played out',
    D: 'Clear problem definition and expected outcomes',
  },
  {
    id: 5,
    text: 'In work conversations, I prefer when people...',
    A: 'Are precise and specific about details',
    B: 'Explain context and connections',
    C: 'Share real examples and experiences',
    D: 'Get straight to the problem and solution',
  },
];

const RANKS = [1, 2, 3, 4];

function isValidRanks(ranks) {
  if (!ranks || typeof ranks !== 'object') return false;
  const values = [ranks.A, ranks.B, ranks.C, ranks.D].filter((v) => v != null);
  return values.length === 4 && new Set(values).size === 4 && values.every((v) => v >= 1 && v <= 4);
}

const styles = {
  page: {
    minHeight: '100vh',
    background: 'linear-gradient(160deg, #f0f9ff 0%, #e0f2fe 35%, #f5f3ff 100%)',
    padding: '24px 16px',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
  },
  container: {
    width: '100%',
    maxWidth: 620,
  },
  progressBar: {
    width: '100%',
    height: 6,
    background: 'rgba(255,255,255,0.6)',
    borderRadius: 3,
    overflow: 'hidden',
    marginBottom: 32,
  },
  progressFill: {
    height: '100%',
    background: 'linear-gradient(90deg, #0ea5e9, #8b5cf6)',
    borderRadius: 3,
    transition: 'width 0.3s ease',
  },
  welcomeCard: {
    background: '#fff',
    borderRadius: 16,
    boxShadow: '0 4px 24px rgba(0,0,0,0.06)',
    padding: 40,
    textAlign: 'center',
  },
  welcomeTitle: {
    margin: '0 0 16px 0',
    fontSize: 26,
    fontWeight: 600,
    color: '#0f172a',
    lineHeight: 1.3,
  },
  welcomeSub: {
    margin: '0 0 12px 0',
    fontSize: 16,
    color: '#475569',
    lineHeight: 1.5,
  },
  welcomeHint: {
    margin: '24px 0 0 0',
    padding: '16px 20px',
    background: '#f8fafc',
    borderRadius: 12,
    fontSize: 15,
    color: '#64748b',
    lineHeight: 1.5,
  },
  questionCard: {
    background: '#fff',
    borderRadius: 16,
    boxShadow: '0 4px 24px rgba(0,0,0,0.06)',
    padding: 32,
  },
  stepLabel: {
    fontSize: 13,
    fontWeight: 600,
    color: '#0ea5e9',
    textTransform: 'uppercase',
    letterSpacing: '0.05em',
    marginBottom: 12,
  },
  questionText: {
    margin: '0 0 24px 0',
    fontSize: 18,
    fontWeight: 600,
    color: '#0f172a',
    lineHeight: 1.4,
  },
  optionRow: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    gap: 16,
    padding: '14px 16px',
    marginBottom: 10,
    background: '#f8fafc',
    borderRadius: 12,
    border: '1px solid transparent',
    transition: 'border-color 0.2s, background 0.2s',
  },
  optionLabel: {
    fontSize: 13,
    fontWeight: 700,
    color: '#64748b',
    minWidth: 24,
  },
  optionText: {
    flex: 1,
    margin: 0,
    fontSize: 15,
    color: '#334155',
    lineHeight: 1.4,
  },
  rankSelect: {
    padding: '8px 12px',
    fontSize: 15,
    fontWeight: 600,
    color: '#0f172a',
    background: '#fff',
    border: '2px solid #e2e8f0',
    borderRadius: 8,
    cursor: 'pointer',
    minWidth: 56,
  },
  navRow: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginTop: 32,
    gap: 16,
  },
  btnSecondary: {
    padding: '12px 24px',
    fontSize: 15,
    fontWeight: 600,
    color: '#64748b',
    background: '#f1f5f9',
    border: 'none',
    borderRadius: 10,
    cursor: 'pointer',
  },
  btnPrimary: {
    padding: '12px 28px',
    fontSize: 15,
    fontWeight: 600,
    color: '#fff',
    background: 'linear-gradient(135deg, #0ea5e9, #8b5cf6)',
    border: 'none',
    borderRadius: 10,
    cursor: 'pointer',
    boxShadow: '0 4px 14px rgba(14, 165, 233, 0.35)',
  },
  btnPrimaryDisabled: {
    opacity: 0.7,
    cursor: 'not-allowed',
  },
  error: {
    marginTop: 16,
    padding: '12px 16px',
    background: '#fef2f2',
    border: '1px solid #fecaca',
    borderRadius: 10,
    fontSize: 14,
    color: '#b91c1c',
  },
  submitError: {
    marginBottom: 16,
    padding: '12px 16px',
    background: '#fef2f2',
    border: '1px solid #fecaca',
    borderRadius: 10,
    fontSize: 14,
    color: '#b91c1c',
  },
};

function Assessment() {
  const navigate = useNavigate();
  const [step, setStep] = useState(0);
  const [answers, setAnswers] = useState(() =>
    QUESTIONS.map(() => ({ A: null, B: null, C: null, D: null }))
  );
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    const raw = localStorage.getItem('user');
    if (raw) {
      try {
        const user = JSON.parse(raw);
        if (user.assessment_completed) {
          navigate('/stakeholder-dashboard', { replace: true });
          return;
        }
      } catch (_) {}
    }
  }, [navigate]);

  const progressPercent = step === 0 ? 0 : (step / QUESTIONS.length) * 100;

  const setRank = (questionIndex, option, value) => {
    const valueNum = value === '' ? null : Number(value);
    setAnswers((prev) => {
      const next = [...prev];
      next[questionIndex] = { ...next[questionIndex], [option]: valueNum };
      return next;
    });
    setError('');
  };

  const handleNext = () => {
    const current = answers[step - 1];
    if (!isValidRanks(current)) {
      setError('Please assign each option a different rank from 1 to 4 (1 = most like you).');
      return;
    }
    setError('');
    if (step < QUESTIONS.length) {
      setStep(step + 1);
    }
  };

  const handlePrev = () => {
    setError('');
    setStep((s) => Math.max(0, s - 1));
  };

  const handleSubmit = async () => {
    const last = answers[QUESTIONS.length - 1];
    if (!isValidRanks(last)) {
      setError('Please assign each option a different rank from 1 to 4 (1 = most like you).');
      return;
    }
    setError('');
    setSubmitting(true);
    try {
      const responses = QUESTIONS.map((q, i) => ({
        question: `Question ${q.id}`,
        ranks: answers[i],
      }));
      const res = await submitAssessment(responses);
      const user = res.data;
      const stored = localStorage.getItem('user');
      const parsed = stored ? JSON.parse(stored) : {};
      localStorage.setItem('user', JSON.stringify({ ...parsed, ...user, assessment_completed: true }));
      navigate('/stakeholder-dashboard', { replace: true });
    } catch (err) {
      const detail = err.response?.data?.detail;
      setError(Array.isArray(detail) ? detail.join(' ') : detail || 'Something went wrong. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div style={styles.page}>
      <div style={styles.container}>
        {step > 0 && (
          <div style={styles.progressBar}>
            <div style={{ ...styles.progressFill, width: `${progressPercent}%` }} />
          </div>
        )}

        {step === 0 && (
          <div style={styles.welcomeCard}>
            <h1 style={styles.welcomeTitle}>Welcome to your Discovery Session</h1>
            <p style={styles.welcomeSub}>
              First, let's understand your communication style. This helps us tailor the conversation to you.
            </p>
            <p style={styles.welcomeSub}>
              For each question, rank the 4 options from 1 to 4 (1 = most like you, 4 = least like you).
            </p>
            <p style={styles.welcomeHint}>
              There are no wrong answers — we're just learning how you prefer to communicate.
            </p>
            <div style={styles.navRow}>
              <div />
              <button type="button" style={styles.btnPrimary} onClick={() => setStep(1)}>
                Start assessment
              </button>
            </div>
          </div>
        )}

        {step >= 1 && step <= QUESTIONS.length && (
          <div style={styles.questionCard}>
            <div style={styles.stepLabel}>
              Question {step} of {QUESTIONS.length}
            </div>
            <h2 style={styles.questionText}>{QUESTIONS[step - 1].text}</h2>
            {['A', 'B', 'C', 'D'].map((key) => (
              <div key={key} style={styles.optionRow}>
                <span style={styles.optionLabel}>{key})</span>
                <p style={styles.optionText}>{QUESTIONS[step - 1][key]}</p>
                <select
                  value={answers[step - 1][key] ?? ''}
                  onChange={(e) => setRank(step - 1, key, e.target.value)}
                  style={styles.rankSelect}
                  aria-label={`Rank for option ${key}`}
                >
                  <option value="">Rank</option>
                  {RANKS.map((r) => (
                    <option key={r} value={r}>
                      {r}
                    </option>
                  ))}
                </select>
              </div>
            ))}
            {error && <div style={styles.error}>{error}</div>}
            <div style={styles.navRow}>
              <button type="button" style={styles.btnSecondary} onClick={handlePrev}>
                {step === 1 ? 'Back' : 'Previous'}
              </button>
              {step < QUESTIONS.length ? (
                <button type="button" style={styles.btnPrimary} onClick={handleNext}>
                  Next
                </button>
              ) : (
                <button
                  type="button"
                  style={{
                    ...styles.btnPrimary,
                    ...(submitting ? styles.btnPrimaryDisabled : {}),
                  }}
                  onClick={handleSubmit}
                  disabled={submitting}
                >
                  {submitting ? 'Submitting…' : 'Complete assessment'}
                </button>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default Assessment;
