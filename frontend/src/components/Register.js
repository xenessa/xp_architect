import { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { register, login, getInviteDetails } from '../services/api';

const styles = {
  page: {
    minHeight: '100vh',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    background: 'linear-gradient(135deg, #f5f7fa 0%, #e4e8ec 100%)',
    padding: 16,
  },
  card: {
    background: '#fff',
    borderRadius: 8,
    boxShadow: '0 4px 20px rgba(0,0,0,0.08)',
    padding: 32,
    width: '100%',
    maxWidth: 380,
  },
  title: {
    margin: '0 0 24px 0',
    fontSize: 24,
    fontWeight: 600,
    color: '#1a1a2e',
    textAlign: 'center',
  },
  form: {
    display: 'flex',
    flexDirection: 'column',
    gap: 16,
  },
  formGroup: {
    display: 'flex',
    flexDirection: 'column',
    gap: 4,
  },
  label: {
    fontSize: 14,
    fontWeight: 500,
    color: '#374151',
    marginBottom: -4,
  },
  input: {
    padding: '10px 12px',
    fontSize: 16,
    border: '1px solid #d1d5db',
    borderRadius: 6,
    outline: 'none',
    transition: 'border-color 0.2s',
  },
  inputReadOnly: {
    padding: '10px 12px',
    fontSize: 16,
    border: '1px solid #d1d5db',
    borderRadius: 6,
    outline: 'none',
    transition: 'border-color 0.2s',
    background: '#f3f4f6',
    cursor: 'not-allowed',
  },
  select: {
    padding: '10px 12px',
    fontSize: 16,
    border: '1px solid #d1d5db',
    borderRadius: 6,
    outline: 'none',
    background: '#fff',
  },
  button: {
    marginTop: 8,
    padding: '12px 16px',
    fontSize: 16,
    fontWeight: 600,
    color: '#fff',
    background: '#2563eb',
    border: 'none',
    borderRadius: 6,
    cursor: 'pointer',
  },
  buttonDisabled: {
    opacity: 0.7,
    cursor: 'not-allowed',
  },
  error: {
    padding: '10px 12px',
    fontSize: 14,
    color: '#b91c1c',
    background: '#fef2f2',
    border: '1px solid #fecaca',
    borderRadius: 6,
  },
  link: {
    marginTop: 16,
    color: '#2563eb',
    textDecoration: 'none',
    fontSize: 14,
    textAlign: 'center',
    display: 'block',
  },
  inviteBanner: {
    padding: '12px 16px',
    background: '#eff6ff',
    border: '1px solid #bfdbfe',
    borderRadius: 6,
    marginBottom: 16,
    fontSize: 14,
    color: '#1e40af',
    textAlign: 'center',
  },
};

function Register() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const inviteToken = searchParams.get('token');

  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [role, setRole] = useState('STAKEHOLDER');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [inviteLoading, setInviteLoading] = useState(false);
  const [inviteError, setInviteError] = useState('');
  const [projectName, setProjectName] = useState('');

  const isInvited = Boolean(inviteToken);

  useEffect(() => {
    const fetchInviteDetails = async () => {
      if (!inviteToken) return;
      setInviteLoading(true);
      setInviteError('');
      try {
        const res = await getInviteDetails(inviteToken);
        const { email: invitedEmail, name: invitedName, project_name: invitedProjectName } = res.data;
        if (invitedName) {
          setName(invitedName);
        }
        if (invitedEmail) {
          setEmail(invitedEmail);
        }
        if (invitedProjectName) {
          setProjectName(invitedProjectName);
        }
      } catch (err) {
        const detail = err.response?.data?.detail;
        const message =
          typeof detail === 'string'
            ? detail
            : 'Unable to load invitation details. The invite may be invalid or expired.';
        setInviteError(message);
      } finally {
        setInviteLoading(false);
      }
    };

    fetchInviteDetails();
  }, [inviteToken]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    if (!name.trim() || !email.trim() || !password) {
      setError('Please fill in all fields.');
      return;
    }
    setLoading(true);
    try {
      const chosenRole = isInvited ? 'STAKEHOLDER' : role;
      await register(email.trim(), password, name.trim(), chosenRole, inviteToken);
      // Immediately log in after successful registration
      const loginRes = await login(email.trim(), password);
      const { access_token, user } = loginRes.data;
      localStorage.setItem('token', access_token);
      localStorage.setItem('user', JSON.stringify(user));
      if (user.role === 'SA') {
        navigate('/dashboard', { replace: true });
      } else {
        if (user.assessment_completed) {
          navigate('/stakeholder-dashboard', { replace: true });
        } else {
          navigate('/assessment', { replace: true });
        }
      }
    } catch (err) {
      const detail = err.response?.data?.detail;
      const message = Array.isArray(detail)
        ? detail.join(' ')
        : typeof detail === 'string'
          ? detail
          : 'Registration failed. Please check your details and try again.';
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={styles.page}>
      <div style={styles.card}>
        <h1 style={styles.title}>{isInvited ? 'Join Project' : 'Create Account'}</h1>

        {isInvited && inviteLoading && (
          <div style={{ textAlign: 'center', fontSize: 14, marginBottom: 16 }}>
            Loading invitation details...
          </div>
        )}

        {isInvited && !inviteLoading && inviteError && (
          <div style={styles.error}>
            <div style={{ marginBottom: 8 }}>{inviteError}</div>
            <a href="/" style={styles.link}>
              Go back to login
            </a>
          </div>
        )}

        {isInvited && !inviteLoading && !inviteError && projectName && (
          <div style={styles.inviteBanner}>
            You&apos;ve been invited to join <strong>{projectName}</strong>.
          </div>
        )}

        {!isInvited || (isInvited && !inviteLoading && !inviteError) ? (
          <form style={styles.form} onSubmit={handleSubmit}>
          <div style={styles.formGroup}>
            <label style={styles.label} htmlFor="name">
              Name
            </label>
            <input
              id="name"
              type="text"
              autoComplete="name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              style={styles.input}
              disabled={loading}
            />
          </div>

          <div style={styles.formGroup}>
            <label style={styles.label} htmlFor="email">
              Email
            </label>
            <input
              id="email"
              type="email"
              autoComplete="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              style={isInvited ? styles.inputReadOnly : styles.input}
              disabled={loading || isInvited}
              readOnly={isInvited}
            />
          </div>

          <div style={styles.formGroup}>
            <label style={styles.label} htmlFor="password">
              Password
            </label>
            <input
              id="password"
              type="password"
              autoComplete="new-password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              style={styles.input}
              disabled={loading}
            />
          </div>

          {!isInvited && (
            <div style={styles.formGroup}>
              <label style={styles.label} htmlFor="role">
                Role
              </label>
              <select
                id="role"
                value={role}
                onChange={(e) => setRole(e.target.value)}
                style={styles.select}
                disabled={loading}
              >
                <option value="SA">Solution Architect</option>
                <option value="STAKEHOLDER">Stakeholder</option>
              </select>
            </div>
          )}

          {error && <div style={styles.error}>{error}</div>}

          <button
            type="submit"
            style={{
              ...styles.button,
              ...(loading ? styles.buttonDisabled : {}),
            }}
            disabled={loading}
          >
            {loading ? 'Creating account…' : 'Create account'}
          </button>

          <a href="/" style={styles.link}>
            Already have an account? Sign in
          </a>
        </form>
        ) : null}
      </div>
    </div>
  );
}

export default Register;

