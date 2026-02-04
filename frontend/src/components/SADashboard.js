import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getProjects, createProject } from '../services/api';

const styles = {
  page: {
    minHeight: '100vh',
    background: '#f5f7fa',
  },
  header: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: '16px 24px',
    background: '#fff',
    boxShadow: '0 1px 3px rgba(0,0,0,0.06)',
  },
  welcome: {
    margin: 0,
    fontSize: 18,
    fontWeight: 600,
    color: '#1a1a2e',
  },
  logoutBtn: {
    padding: '8px 16px',
    fontSize: 14,
    fontWeight: 500,
    color: '#6b7280',
    background: 'transparent',
    border: '1px solid #d1d5db',
    borderRadius: 6,
    cursor: 'pointer',
  },
  main: {
    maxWidth: 1200,
    margin: '0 auto',
    padding: 24,
  },
  topBar: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 24,
  },
  title: {
    margin: 0,
    fontSize: 22,
    fontWeight: 600,
    color: '#1a1a2e',
  },
  createBtn: {
    padding: '10px 20px',
    fontSize: 14,
    fontWeight: 600,
    color: '#fff',
    background: '#2563eb',
    border: 'none',
    borderRadius: 6,
    cursor: 'pointer',
  },
  grid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))',
    gap: 20,
  },
  card: {
    background: '#fff',
    borderRadius: 8,
    boxShadow: '0 1px 3px rgba(0,0,0,0.06)',
    padding: 20,
    display: 'flex',
    flexDirection: 'column',
    gap: 12,
  },
  cardName: {
    margin: 0,
    fontSize: 17,
    fontWeight: 600,
    color: '#1a1a2e',
  },
  cardScope: {
    fontSize: 14,
    color: '#6b7280',
    lineHeight: 1.4,
    flex: 1,
  },
  cardDates: {
    fontSize: 13,
    color: '#9ca3af',
  },
  miniProgressContainer: {
    marginTop: 12,
  },
  miniProgressBar: {
    height: 6,
    background: '#e5e7eb',
    borderRadius: 3,
    overflow: 'hidden',
    marginBottom: 4,
  },
  miniProgressFill: {
    height: '100%',
    background: '#10b981',
    borderRadius: 3,
    transition: 'width 0.2s',
  },
  miniProgressText: {
    fontSize: 12,
    color: '#6b7280',
  },
  viewBtn: {
    alignSelf: 'flex-start',
    padding: '8px 16px',
    fontSize: 14,
    fontWeight: 500,
    color: '#2563eb',
    background: 'transparent',
    border: '1px solid #2563eb',
    borderRadius: 6,
    cursor: 'pointer',
  },
  empty: {
    textAlign: 'center',
    padding: 48,
    color: '#6b7280',
    fontSize: 15,
  },
  error: {
    padding: 12,
    background: '#fef2f2',
    border: '1px solid #fecaca',
    borderRadius: 6,
    color: '#b91c1c',
    fontSize: 14,
    marginBottom: 16,
  },
  overlay: {
    position: 'fixed',
    inset: 0,
    background: 'rgba(0,0,0,0.4)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 24,
    zIndex: 1000,
  },
  modal: {
    background: '#fff',
    borderRadius: 8,
    boxShadow: '0 10px 40px rgba(0,0,0,0.15)',
    width: '100%',
    maxWidth: 520,
    maxHeight: '90vh',
    overflow: 'auto',
  },
  modalHeader: {
    padding: '20px 24px',
    borderBottom: '1px solid #e5e7eb',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  modalTitle: {
    margin: 0,
    fontSize: 18,
    fontWeight: 600,
    color: '#1a1a2e',
  },
  modalClose: {
    background: 'none',
    border: 'none',
    fontSize: 24,
    color: '#9ca3af',
    cursor: 'pointer',
    lineHeight: 1,
    padding: 0,
  },
  modalBody: {
    padding: 24,
  },
  form: {
    display: 'flex',
    flexDirection: 'column',
    gap: 16,
  },
  label: {
    fontSize: 14,
    fontWeight: 500,
    color: '#374151',
  },
  input: {
    padding: '10px 12px',
    fontSize: 14,
    border: '1px solid #d1d5db',
    borderRadius: 6,
    outline: 'none',
    width: '100%',
    boxSizing: 'border-box',
  },
  textarea: {
    padding: '10px 12px',
    fontSize: 14,
    border: '1px solid #d1d5db',
    borderRadius: 6,
    outline: 'none',
    width: '100%',
    boxSizing: 'border-box',
    minHeight: 80,
    resize: 'vertical',
    fontFamily: 'inherit',
  },
  modalFooter: {
    padding: '16px 24px',
    borderTop: '1px solid #e5e7eb',
    display: 'flex',
    justifyContent: 'flex-end',
    gap: 12,
  },
  cancelBtn: {
    padding: '10px 18px',
    fontSize: 14,
    fontWeight: 500,
    color: '#6b7280',
    background: '#fff',
    border: '1px solid #d1d5db',
    borderRadius: 6,
    cursor: 'pointer',
  },
  submitBtn: {
    padding: '10px 18px',
    fontSize: 14,
    fontWeight: 600,
    color: '#fff',
    background: '#2563eb',
    border: 'none',
    borderRadius: 6,
    cursor: 'pointer',
  },
  submitBtnDisabled: {
    opacity: 0.7,
    cursor: 'not-allowed',
  },
};

function truncate(str, len) {
  if (!str) return '';
  return str.length <= len ? str : str.slice(0, len) + '…';
}

function formatDate(dateStr) {
  if (!dateStr) return '—';
  try {
    const d = new Date(dateStr);
    return d.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
  } catch {
    return dateStr;
  }
}

function SADashboard() {
  const [user, setUser] = useState(null);
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [modalOpen, setModalOpen] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [formError, setFormError] = useState('');
  const [form, setForm] = useState({
    name: '',
    description: '',
    scope: '',
    instructions: '',
    start_date: '',
    end_date: '',
  });
  const navigate = useNavigate();

  useEffect(() => {
    const raw = localStorage.getItem('user');
    if (raw) {
      try {
        setUser(JSON.parse(raw));
      } catch (_) {}
    }
  }, []);

  const loadProjects = async () => {
    setError('');
    try {
      const res = await getProjects();
      setProjects(res.data.projects || []);
    } catch (err) {
      const detail = err.response?.data?.detail;
      setError(Array.isArray(detail) ? detail.join(' ') : detail || 'Failed to load projects.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadProjects();
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    navigate('/', { replace: true });
  };

  const openModal = () => {
    setForm({
      name: '',
      description: '',
      scope: '',
      instructions: '',
      start_date: '',
      end_date: '',
    });
    setFormError('');
    setModalOpen(true);
  };

  const closeModal = () => {
    setModalOpen(false);
    setFormError('');
  };

  const handleFormChange = (field, value) => {
    setForm((prev) => ({ ...prev, [field]: value }));
  };

  const handleCreateSubmit = async (e) => {
    e.preventDefault();
    setFormError('');
    const { name, scope, start_date, end_date } = form;
    if (!name?.trim()) {
      setFormError('Name is required.');
      return;
    }
    if (!scope?.trim()) {
      setFormError('Scope is required.');
      return;
    }
    if (!start_date) {
      setFormError('Start date is required.');
      return;
    }
    if (!end_date) {
      setFormError('End date is required.');
      return;
    }
    if (new Date(end_date) < new Date(start_date)) {
      setFormError('End date must be on or after start date.');
      return;
    }
    setSubmitting(true);
    try {
      await createProject({
        name: name.trim(),
        description: form.description?.trim() || null,
        scope: scope.trim(),
        instructions: form.instructions?.trim() || null,
        start_date,
        end_date,
      });
      closeModal();
      await loadProjects();
    } catch (err) {
      const detail = err.response?.data?.detail;
      setFormError(Array.isArray(detail) ? detail.join(' ') : detail || 'Failed to create project.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div style={styles.page}>
      <header style={styles.header}>
        <h1 style={styles.welcome}>Welcome, {user?.name ?? 'User'}</h1>
        <button type="button" style={styles.logoutBtn} onClick={handleLogout}>
          Logout
        </button>
      </header>

      <main style={styles.main}>
        <div style={styles.topBar}>
          <h2 style={styles.title}>Projects</h2>
          <button type="button" style={styles.createBtn} onClick={openModal}>
            Create Project
          </button>
        </div>

        {error && <div style={styles.error}>{error}</div>}

        {loading ? (
          <div style={styles.empty}>Loading projects…</div>
        ) : projects.length === 0 ? (
          <div style={styles.empty}>No projects yet. Create one to get started.</div>
        ) : (
          <div style={styles.grid}>
            {projects.map((p) => (
              <div key={p.id} style={styles.card}>
                <h3 style={styles.cardName}>{p.name}</h3>
                <p style={styles.cardScope}>{truncate(p.scope, 100)}</p>
                <p style={styles.cardDates}>
                  {formatDate(p.start_date)} – {formatDate(p.end_date)}
                </p>
                <div style={styles.miniProgressContainer}>
                  {p.total_users && p.total_users > 0 ? (
                    <>
                      <div style={styles.miniProgressBar}>
                        <div
                          style={{
                            ...styles.miniProgressFill,
                            width: `${p.completion_percentage ?? 0}%`,
                          }}
                        />
                      </div>
                      <div style={styles.miniProgressText}>
                        {p.completed_users ?? 0}/{p.total_users} stakeholders complete (
                        {p.completion_percentage?.toFixed(1) ?? '0.0'}%)
                      </div>
                    </>
                  ) : (
                    <div style={{ ...styles.miniProgressText, color: '#9ca3af' }}>
                      No stakeholders
                    </div>
                  )}
                </div>
                <button
                  type="button"
                  style={styles.viewBtn}
                  onClick={() => navigate(`/project/${p.id}`)}
                >
                  View
                </button>
              </div>
            ))}
          </div>
        )}
      </main>

      {modalOpen && (
        <div style={styles.overlay} onClick={closeModal}>
          <div style={styles.modal} onClick={(e) => e.stopPropagation()}>
            <div style={styles.modalHeader}>
              <h2 style={styles.modalTitle}>Create Project</h2>
              <button type="button" style={styles.modalClose} onClick={closeModal} aria-label="Close">
                ×
              </button>
            </div>
            <form onSubmit={handleCreateSubmit}>
              <div style={styles.modalBody}>
                <div style={styles.form}>
                  <label style={styles.label} htmlFor="create-name">
                    Name *
                  </label>
                  <input
                    id="create-name"
                    type="text"
                    value={form.name}
                    onChange={(e) => handleFormChange('name', e.target.value)}
                    style={styles.input}
                    placeholder="Project name"
                    disabled={submitting}
                  />
                  <label style={styles.label} htmlFor="create-description">
                    Description
                  </label>
                  <input
                    id="create-description"
                    type="text"
                    value={form.description}
                    onChange={(e) => handleFormChange('description', e.target.value)}
                    style={styles.input}
                    placeholder="Optional"
                    disabled={submitting}
                  />
                  <label style={styles.label} htmlFor="create-scope">
                    Scope *
                  </label>
                  <textarea
                    id="create-scope"
                    value={form.scope}
                    onChange={(e) => handleFormChange('scope', e.target.value)}
                    style={styles.textarea}
                    placeholder="Project scope"
                    disabled={submitting}
                  />
                  <label style={styles.label} htmlFor="create-instructions">
                    Instructions
                  </label>
                  <textarea
                    id="create-instructions"
                    value={form.instructions}
                    onChange={(e) => handleFormChange('instructions', e.target.value)}
                    style={styles.textarea}
                    placeholder="Optional"
                    disabled={submitting}
                  />
                  <label style={styles.label} htmlFor="create-start">
                    Start Date *
                  </label>
                  <input
                    id="create-start"
                    type="date"
                    value={form.start_date}
                    onChange={(e) => handleFormChange('start_date', e.target.value)}
                    style={styles.input}
                    disabled={submitting}
                  />
                  <label style={styles.label} htmlFor="create-end">
                    End Date *
                  </label>
                  <input
                    id="create-end"
                    type="date"
                    value={form.end_date}
                    onChange={(e) => handleFormChange('end_date', e.target.value)}
                    style={styles.input}
                    disabled={submitting}
                  />
                  {formError && <div style={styles.error}>{formError}</div>}
                </div>
              </div>
              <div style={styles.modalFooter}>
                <button type="button" style={styles.cancelBtn} onClick={closeModal} disabled={submitting}>
                  Cancel
                </button>
                <button
                  type="submit"
                  style={{ ...styles.submitBtn, ...(submitting ? styles.submitBtnDisabled : {}) }}
                  disabled={submitting}
                >
                  {submitting ? 'Creating…' : 'Create Project'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

export default SADashboard;
