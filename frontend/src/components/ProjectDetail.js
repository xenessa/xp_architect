import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  getProject,
  getProjectProgress,
  addUserToProject,
  activateProjectUser,
  getStakeholderDiscoveryResults,
  updateProject,
  deactivateStakeholder,
  deleteStakeholder,
} from '../services/api';
import ConsolidatedReport from './ConsolidatedReport';

const PHASES = {
  1: { name: 'Open Discovery' },
  2: { name: 'Targeted Follow-ups' },
  3: { name: 'Validation & Clarification' },
  4: { name: 'Future State & Priorities' },
};

const styles = {
  page: {
    minHeight: '100vh',
    background: '#f5f7fa',
  },
  header: {
    background: '#fff',
    boxShadow: '0 1px 3px rgba(0,0,0,0.06)',
    padding: '20px 24px',
    marginBottom: 24,
  },
  headerInner: {
    maxWidth: 1200,
    margin: '0 auto',
  },
  backBtn: {
    display: 'inline-flex',
    alignItems: 'center',
    gap: 6,
    marginBottom: 16,
    padding: '6px 0',
    fontSize: 14,
    fontWeight: 500,
    color: '#6b7280',
    background: 'none',
    border: 'none',
    cursor: 'pointer',
  },
  projectName: {
    margin: '0 0 12px 0',
    fontSize: 26,
    fontWeight: 600,
    color: '#1a1a2e',
  },
  scope: {
    margin: '0 0 12px 0',
    fontSize: 15,
    color: '#4b5563',
    lineHeight: 1.5,
    whiteSpace: 'pre-wrap',
  },
  instructions: {
    margin: '0 0 12px 0',
    fontSize: 14,
    color: '#6b7280',
    lineHeight: 1.5,
    whiteSpace: 'pre-wrap',
  },
  dateRange: {
    margin: 0,
    fontSize: 14,
    color: '#9ca3af',
  },
  main: {
    maxWidth: 1200,
    margin: '0 auto',
    padding: '0 24px 24px',
  },
  section: {
    background: '#fff',
    borderRadius: 8,
    boxShadow: '0 1px 3px rgba(0,0,0,0.06)',
    padding: 24,
    marginBottom: 24,
  },
  sectionTitle: {
    margin: '0 0 16px 0',
    fontSize: 18,
    fontWeight: 600,
    color: '#1a1a2e',
  },
  progressSummary: {
    display: 'flex',
    alignItems: 'center',
    gap: 16,
    flexWrap: 'wrap',
    marginBottom: 16,
  },
  progressText: {
    margin: 0,
    fontSize: 15,
    color: '#4b5563',
  },
  progressBar: {
    flex: '1 1 200px',
    height: 10,
    background: '#e5e7eb',
    borderRadius: 5,
    overflow: 'hidden',
    display: 'flex',
  },
  progressBarSegment: {
    height: '100%',
    transition: 'width 0.2s',
  },
  stakeholderList: {
    listStyle: 'none',
    margin: 0,
    padding: 0,
  },
  stakeholderRow: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: '14px 0',
    borderBottom: '1px solid #f3f4f6',
    gap: 12,
    flexWrap: 'wrap',
  },
  stakeholderInfo: {
    flex: '1 1 200px',
  },
  stakeholderName: {
    margin: '0 0 4px 0',
    fontSize: 15,
    fontWeight: 600,
    color: '#1a1a2e',
  },
  stakeholderEmail: {
    margin: 0,
    fontSize: 14,
    color: '#6b7280',
  },
  badge: {
    display: 'inline-block',
    padding: '4px 10px',
    fontSize: 12,
    fontWeight: 600,
    borderRadius: 6,
    textTransform: 'uppercase',
  },
  badgeInvited: {
    background: '#fef3c7',
    color: '#b45309',
  },
  badgeActive: {
    background: '#dbeafe',
    color: '#1d4ed8',
  },
  badgeInactive: {
    background: '#e5e7eb',
    color: '#6b7280',
  },
  badgeCompleted: {
    background: '#d1fae5',
    color: '#047857',
  },
  discoveryStatus: {
    fontSize: 13,
    fontWeight: 500,
    marginLeft: 8,
  },
  activateBtn: {
    padding: '6px 14px',
    fontSize: 13,
    fontWeight: 500,
    color: '#fff',
    background: '#2563eb',
    border: 'none',
    borderRadius: 6,
    cursor: 'pointer',
  },
  copyLinkBtn: {
    padding: '6px 14px',
    fontSize: 13,
    fontWeight: 500,
    color: '#fff',
    background: '#059669',
    border: 'none',
    borderRadius: 6,
    cursor: 'pointer',
  },
  copiedBtn: {
    background: '#10b981',
  },
  addForm: {
    display: 'flex',
    gap: 12,
    flexWrap: 'wrap',
    alignItems: 'flex-end',
    marginTop: 16,
    paddingTop: 16,
    borderTop: '1px solid #f3f4f6',
  },
  addFormGroup: {
    display: 'flex',
    flexDirection: 'column',
    gap: 4,
  },
  label: {
    fontSize: 12,
    fontWeight: 500,
    color: '#6b7280',
  },
  input: {
    padding: '8px 12px',
    fontSize: 14,
    border: '1px solid #d1d5db',
    borderRadius: 6,
    outline: 'none',
    minWidth: 180,
  },
  addBtn: {
    padding: '8px 16px',
    fontSize: 14,
    fontWeight: 600,
    color: '#fff',
    background: '#2563eb',
    border: 'none',
    borderRadius: 6,
    cursor: 'pointer',
  },
  addBtnDisabled: {
    opacity: 0.7,
    cursor: 'not-allowed',
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
  loading: {
    textAlign: 'center',
    padding: 48,
    color: '#6b7280',
    fontSize: 15,
  },
};

const STATUS_BADGE_STYLES = {
  INVITED: { ...styles.badge, ...styles.badgeInvited },
  ACTIVE: { ...styles.badge, ...styles.badgeActive },
  INACTIVE: { ...styles.badge, ...styles.badgeInactive },
  COMPLETED: { ...styles.badge, ...styles.badgeCompleted },
};

function calculateDetailedProgress(users) {
  if (!users || users.length === 0) {
    return { completedPct: 0, inProgressPct: 0, notStartedPct: 0 };
  }

  const totalPhases = users.length * 4; // 4 phases per user
  let completedPhases = 0;
  let inProgressPhases = 0;

  users.forEach((user) => {
    if (user.discovery_status === 'COMPLETED') {
      // Fully complete = 4 phases
      completedPhases += 4;
    } else if (user.discovery_status === 'IN_PROGRESS') {
      // Count approved phases as complete
      const approved = user.phases_approved?.length || 0;
      completedPhases += approved;
      // Current phase counts as partial progress (half a phase)
      inProgressPhases += 0.5;
    }
    // NOT_STARTED, no session, or INVITED = 0 phases
  });

  const completedPct = (completedPhases / totalPhases) * 100;
  const inProgressPct = (inProgressPhases / totalPhases) * 100;
  const notStartedPct = 100 - completedPct - inProgressPct;

  return { completedPct, inProgressPct, notStartedPct };
}

function formatDiscoveryStatus(user) {
  // Not registered yet
  if (!user.user_id) {
    return { text: 'Awaiting Registration', color: '#9ca3af' };
  }

  // No session started
  if (!user.discovery_status || user.discovery_status === 'NOT_STARTED') {
    return { text: 'Not Started', color: '#9ca3af' };
  }

  // Completed
  if (user.discovery_status === 'COMPLETED') {
    return { text: 'Discovery Complete', color: '#047857' };
  }

  // In progress - show phase detail
  const phase = user.current_phase || 1;
  const approvedCount = user.phases_approved?.length || 0;

  if (approvedCount >= phase) {
    return { text: `Phase ${phase} Approved`, color: '#1d4ed8' };
  } else {
    return { text: `In Progress - Phase ${phase}`, color: '#b45309' };
  }
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

function ProjectDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [project, setProject] = useState(null);
  const [progress, setProgress] = useState(null);
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [addName, setAddName] = useState('');
  const [addEmail, setAddEmail] = useState('');
  const [adding, setAdding] = useState(false);
  const [addError, setAddError] = useState('');
  const [activatingId, setActivatingId] = useState(null);
  const [copiedToken, setCopiedToken] = useState(null);
  const [resultsUser, setResultsUser] = useState(null);
  const [resultsData, setResultsData] = useState(null);
  const [resultsLoading, setResultsLoading] = useState(false);
  const [resultsError, setResultsError] = useState('');
  const [editOpen, setEditOpen] = useState(false);
  const [editForm, setEditForm] = useState({
    name: '',
    scope: '',
    start_date: '',
    end_date: '',
  });
  const [editSubmitting, setEditSubmitting] = useState(false);
  const [editError, setEditError] = useState('');
  const [deleteConfirmUser, setDeleteConfirmUser] = useState(null);
  const [consolidatedReportOpen, setConsolidatedReportOpen] = useState(false);

  const loadProject = async () => {
    if (!id) return;
    setError('');
    setLoading(true);
    try {
      const [detailRes, progressRes] = await Promise.all([
        getProject(id),
        getProjectProgress(id),
      ]);
      setProject(detailRes.data.project);
      setUsers(detailRes.data.users || []);
      setProgress(progressRes.data);
    } catch (err) {
      const detail = err.response?.data?.detail;
      setError(Array.isArray(detail) ? detail.join(' ') : detail || 'Failed to load project.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadProject();
  }, [id]);

  const handleBack = () => navigate('/dashboard');

  const handleAddStakeholder = async (e) => {
    e.preventDefault();
    setAddError('');
    const name = addName.trim();
    const email = addEmail.trim();
    if (!name || !email) {
      setAddError('Name and email are required.');
      return;
    }
    setAdding(true);
    try {
      await addUserToProject(id, email, name);
      setAddName('');
      setAddEmail('');
      await loadProject();
    } catch (err) {
      const detail = err.response?.data?.detail;
      setAddError(Array.isArray(detail) ? detail.join(' ') : detail || 'Failed to add stakeholder.');
    } finally {
      setAdding(false);
    }
  };

  const handleActivate = async (userId) => {
    setActivatingId(userId);
    try {
      await activateProjectUser(id, userId);
      await loadProject();
    } catch (err) {
      const detail = err.response?.data?.detail;
      setError(Array.isArray(detail) ? detail.join(' ') : detail || 'Failed to activate user.');
    } finally {
      setActivatingId(null);
    }
  };

  const handleCopyInvite = async (projectUserId, inviteToken) => {
    if (!inviteToken) {
      setError('No invite link available for this stakeholder.');
      return;
    }
    const url = `${window.location.origin}/register?token=${encodeURIComponent(inviteToken)}`;
    try {
      if (navigator.clipboard && navigator.clipboard.writeText) {
        await navigator.clipboard.writeText(url);
      } else {
        // Fallback for older browsers
        window.prompt('Copy this invite link:', url);
      }
      setCopiedToken(projectUserId);
      setTimeout(() => setCopiedToken(null), 2000);
    } catch (err) {
      // Best-effort: show a simple error
      setError('Failed to copy invite link. Please try again.');
    }
  };

  const openEditModal = () => {
    if (!project) return;
    setEditForm({
      name: project.name || '',
      scope: project.scope || '',
      start_date: project.start_date || '',
      end_date: project.end_date || '',
    });
    setEditError('');
    setEditOpen(true);
  };

  const closeEditModal = () => {
    setEditOpen(false);
    setEditError('');
  };

  const handleEditChange = (field, value) => {
    setEditForm((prev) => ({ ...prev, [field]: value }));
  };

  const handleEditSubmit = async (e) => {
    e.preventDefault();
    if (!id) return;
    setEditError('');
    const { name, scope, start_date, end_date } = editForm;
    if (!name.trim()) {
      setEditError('Name is required.');
      return;
    }
    if (!scope.trim()) {
      setEditError('Scope is required.');
      return;
    }
    if (!start_date || !end_date) {
      setEditError('Start and end date are required.');
      return;
    }
    if (new Date(end_date) < new Date(start_date)) {
      setEditError('End date must be on or after start date.');
      return;
    }
    setEditSubmitting(true);
    try {
      await updateProject(id, {
        name: name.trim(),
        scope: scope.trim(),
        start_date,
        end_date,
      });
      await loadProject();
      closeEditModal();
    } catch (err) {
      const detail = err.response?.data?.detail;
      setEditError(Array.isArray(detail) ? detail.join(' ') : detail || 'Failed to update project.');
    } finally {
      setEditSubmitting(false);
    }
  };

  const handleDeactivate = async (user) => {
    if (!id || !user.user_id) return;
    try {
      await deactivateStakeholder(id, user.user_id);
      await loadProject();
    } catch (err) {
      const detail = err.response?.data?.detail;
      setError(Array.isArray(detail) ? detail.join(' ') : detail || 'Failed to deactivate stakeholder.');
    }
  };

  const handleDelete = async () => {
    if (!id || !deleteConfirmUser?.user_id) return;
    try {
      await deleteStakeholder(id, deleteConfirmUser.user_id);
      setDeleteConfirmUser(null);
      await loadProject();
    } catch (err) {
      const detail = err.response?.data?.detail;
      setError(Array.isArray(detail) ? detail.join(' ') : detail || 'Failed to delete stakeholder.');
    }
  };

  const openDeleteConfirm = (user) => {
    setDeleteConfirmUser(user);
  };

  const closeDeleteConfirm = () => {
    setDeleteConfirmUser(null);
  };

  const handleViewResults = async (user) => {
    if (!id || !user.user_id) return;
    setResultsUser(user);
    setResultsData(null);
    setResultsError('');
    setResultsLoading(true);
    try {
      const res = await getStakeholderDiscoveryResults(id, user.user_id);
      setResultsData(res.data);
    } catch (err) {
      const detail = err.response?.data?.detail;
      setResultsError(Array.isArray(detail) ? detail.join(' ') : detail || 'Failed to load discovery results.');
    } finally {
      setResultsLoading(false);
    }
  };

  const closeResults = () => {
    setResultsUser(null);
    setResultsData(null);
    setResultsError('');
  };

  if (loading) {
    return (
      <div style={styles.page}>
        <div style={styles.loading}>Loading project…</div>
      </div>
    );
  }

  if (error && !project) {
    return (
      <div style={styles.page}>
        <div style={styles.main}>
          <div style={styles.error}>{error}</div>
          <button type="button" style={styles.backBtn} onClick={handleBack}>
            ← Back to Dashboard
          </button>
        </div>
      </div>
    );
  }

  if (!project) {
    return (
      <div style={styles.page}>
        <div style={styles.main}>
          <div style={styles.loading}>Project not found.</div>
          <button type="button" style={styles.backBtn} onClick={handleBack}>
            ← Back to Dashboard
          </button>
        </div>
      </div>
    );
  }

  const total = progress?.total_users ?? 0;
  const completed = progress?.completed ?? 0;
  const inProgress = progress?.in_progress ?? 0;
  const notStarted = progress?.not_started ?? 0;
  const { completedPct, inProgressPct, notStartedPct } = calculateDetailedProgress(users);

  return (
    <div style={styles.page}>
      <header style={styles.header}>
        <div style={styles.headerInner}>
          <button type="button" style={styles.backBtn} onClick={handleBack}>
            ← Back to Dashboard
          </button>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12, flexWrap: 'wrap' }}>
            <h1 style={styles.projectName}>{project.name}</h1>
            <button
              type="button"
              style={{
                padding: '6px 12px',
                fontSize: 13,
                fontWeight: 500,
                borderRadius: 6,
                border: '1px solid #d1d5db',
                background: '#ffffff',
                color: '#374151',
                cursor: 'pointer',
              }}
              onClick={openEditModal}
            >
              Edit Project
            </button>
          </div>
          {project.scope && <p style={styles.scope}>{project.scope}</p>}
          {project.instructions && (
            <p style={styles.instructions}>{project.instructions}</p>
          )}
          <p style={styles.dateRange}>
            {formatDate(project.start_date)} – {formatDate(project.end_date)}
          </p>
        </div>
      </header>

      <main style={styles.main}>
        {error && <div style={styles.error}>{error}</div>}

        <section style={styles.section}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 12, marginBottom: 16 }}>
            <h2 style={{ ...styles.sectionTitle, margin: 0 }}>Progress</h2>
            {completed >= 1 && (
              <button
                type="button"
                style={{
                  padding: '10px 18px',
                  fontSize: 14,
                  fontWeight: 600,
                  borderRadius: 8,
                  border: 'none',
                  background: '#059669',
                  color: '#fff',
                  cursor: 'pointer',
                }}
                onClick={() => setConsolidatedReportOpen(true)}
              >
                Generate Consolidated Report
              </button>
            )}
          </div>
          <div style={styles.progressSummary}>
            <p style={styles.progressText}>
              {completed}/{total} completed, {inProgress} in progress, {notStarted} not started
            </p>
            <div style={styles.progressBar}>
              <div
                style={{
                  ...styles.progressBarSegment,
                  width: `${completedPct}%`,
                  background: '#10b981',
                }}
              />
              <div
                style={{
                  ...styles.progressBarSegment,
                  width: `${inProgressPct}%`,
                  background: '#3b82f6',
                }}
              />
              <div
                style={{
                  ...styles.progressBarSegment,
                  width: `${notStartedPct}%`,
                  background: '#e5e7eb',
                }}
              />
            </div>
          </div>
        </section>

        <section style={styles.section}>
          <h2 style={styles.sectionTitle}>Stakeholders</h2>
          {users.length === 0 ? (
            <p style={{ margin: 0, color: '#6b7280', fontSize: 14 }}>
              No stakeholders yet. Add one below.
            </p>
          ) : (
            <ul style={styles.stakeholderList}>
              {users.map((u) => (
                <li key={u.id} style={styles.stakeholderRow}>
                  <div style={styles.stakeholderInfo}>
                    <p style={styles.stakeholderName}>{u.name}</p>
                    <p style={styles.stakeholderEmail}>{u.email}</p>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                    <span style={STATUS_BADGE_STYLES[u.status] || styles.badge}>
                      {u.status}
                    </span>
                    {(() => {
                      const { text, color } = formatDiscoveryStatus(u);
                      return (
                        <span style={{ ...styles.discoveryStatus, color }}>
                          {text}
                        </span>
                      );
                    })()}
                  </div>
                  {u.status === 'INVITED' && u.user_id && (
                    <button
                      type="button"
                      style={styles.activateBtn}
                      onClick={() => handleActivate(u.user_id)}
                      disabled={activatingId === u.user_id}
                    >
                      {activatingId === u.user_id ? 'Activating…' : 'Activate'}
                    </button>
                  )}
                  {u.status === 'INVITED' && !u.user_id && (
                    <button
                      type="button"
                      style={{
                        ...styles.copyLinkBtn,
                        ...(copiedToken === u.id ? styles.copiedBtn : {}),
                      }}
                      onClick={() => handleCopyInvite(u.id, u.invite_token)}
                    >
                      {copiedToken === u.id ? 'Copied!' : 'Copy Invite Link'}
                    </button>
                  )}
                  {u.user_id && (
                    <button
                      type="button"
                      style={{
                        ...styles.activateBtn,
                        background: '#4b5563',
                      }}
                      onClick={() => handleViewResults(u)}
                    >
                      View Results
                    </button>
                  )}
                </li>
              ))}
            </ul>
          )}

          <form onSubmit={handleAddStakeholder} style={styles.addForm}>
            <div style={styles.addFormGroup}>
              <label style={styles.label} htmlFor="add-name">
                Name
              </label>
              <input
                id="add-name"
                type="text"
                value={addName}
                onChange={(e) => setAddName(e.target.value)}
                style={styles.input}
                placeholder="Stakeholder name"
                disabled={adding}
              />
            </div>
            <div style={styles.addFormGroup}>
              <label style={styles.label} htmlFor="add-email">
                Email
              </label>
              <input
                id="add-email"
                type="email"
                value={addEmail}
                onChange={(e) => setAddEmail(e.target.value)}
                style={styles.input}
                placeholder="email@example.com"
                disabled={adding}
              />
            </div>
            <button
              type="submit"
              style={{ ...styles.addBtn, ...(adding ? styles.addBtnDisabled : {}) }}
              disabled={adding}
            >
              {adding ? 'Adding…' : 'Add Stakeholder'}
            </button>
          </form>
          {addError && <div style={{ ...styles.error, marginTop: 12 }}>{addError}</div>}
        </section>
      </main>
      {editOpen && (
        <div
          style={{
            position: 'fixed',
            inset: 0,
            background: 'rgba(15,23,42,0.45)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            padding: 24,
            zIndex: 1000,
          }}
          onClick={closeEditModal}
        >
          <div
            style={{
              background: '#fff',
              borderRadius: 12,
              boxShadow: '0 20px 60px rgba(15,23,42,0.4)',
              maxWidth: 600,
              width: '100%',
            }}
            onClick={(e) => e.stopPropagation()}
          >
            <div
              style={{
                padding: '16px 20px',
                borderBottom: '1px solid #e5e7eb',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
              }}
            >
              <h3 style={{ margin: 0, fontSize: 18, fontWeight: 600, color: '#111827' }}>
                Edit Project
              </h3>
              <button
                type="button"
                onClick={closeEditModal}
                style={{
                  border: 'none',
                  background: 'transparent',
                  fontSize: 22,
                  lineHeight: 1,
                  cursor: 'pointer',
                  color: '#9ca3af',
                }}
                aria-label="Close"
              >
                ×
              </button>
            </div>
            <form onSubmit={handleEditSubmit}>
              <div style={{ padding: 20, display: 'flex', flexDirection: 'column', gap: 12 }}>
                <div>
                  <label style={styles.label} htmlFor="edit-name">
                    Name
                  </label>
                  <input
                    id="edit-name"
                    type="text"
                    value={editForm.name}
                    onChange={(e) => handleEditChange('name', e.target.value)}
                    style={styles.input}
                    disabled={editSubmitting}
                  />
                </div>
                <div>
                  <label style={styles.label} htmlFor="edit-scope">
                    Scope
                  </label>
                  <textarea
                    id="edit-scope"
                    value={editForm.scope}
                    onChange={(e) => handleEditChange('scope', e.target.value)}
                    style={{
                      ...styles.input,
                      minHeight: 80,
                      resize: 'vertical',
                      fontFamily: 'inherit',
                    }}
                    disabled={editSubmitting}
                  />
                </div>
                <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
                  <div style={{ flex: '1 1 160px' }}>
                    <label style={styles.label} htmlFor="edit-start">
                      Start Date
                    </label>
                    <input
                      id="edit-start"
                      type="date"
                      value={editForm.start_date}
                      onChange={(e) => handleEditChange('start_date', e.target.value)}
                      style={styles.input}
                      disabled={editSubmitting}
                    />
                  </div>
                  <div style={{ flex: '1 1 160px' }}>
                    <label style={styles.label} htmlFor="edit-end">
                      End Date
                    </label>
                    <input
                      id="edit-end"
                      type="date"
                      value={editForm.end_date}
                      onChange={(e) => handleEditChange('end_date', e.target.value)}
                      style={styles.input}
                      disabled={editSubmitting}
                    />
                  </div>
                </div>
                {editError && <div style={styles.error}>{editError}</div>}
              </div>
              <div
                style={{
                  padding: '16px 20px',
                  borderTop: '1px solid #e5e7eb',
                  display: 'flex',
                  justifyContent: 'flex-end',
                  gap: 8,
                }}
              >
                <button
                  type="button"
                  onClick={closeEditModal}
                  style={{
                    padding: '8px 14px',
                    fontSize: 14,
                    fontWeight: 500,
                    borderRadius: 6,
                    border: '1px solid #d1d5db',
                    background: '#ffffff',
                    color: '#374151',
                    cursor: 'pointer',
                  }}
                  disabled={editSubmitting}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  style={{
                    padding: '8px 16px',
                    fontSize: 14,
                    fontWeight: 600,
                    borderRadius: 6,
                    border: 'none',
                    background: '#2563eb',
                    color: '#fff',
                    cursor: 'pointer',
                    opacity: editSubmitting ? 0.7 : 1,
                  }}
                  disabled={editSubmitting}
                >
                  {editSubmitting ? 'Saving…' : 'Save Changes'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
      {resultsUser && (
        <div
          style={{
            position: 'fixed',
            inset: 0,
            background: 'rgba(15,23,42,0.45)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            padding: 24,
            zIndex: 1000,
          }}
          onClick={closeResults}
        >
          <div
            style={{
              background: '#fff',
              borderRadius: 12,
              boxShadow: '0 20px 60px rgba(15,23,42,0.4)',
              maxWidth: 800,
              width: '100%',
              maxHeight: '90vh',
              display: 'flex',
              flexDirection: 'column',
            }}
            onClick={(e) => e.stopPropagation()}
          >
            <div
              style={{
                padding: '16px 20px',
                borderBottom: '1px solid #e5e7eb',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
              }}
            >
              <div>
                <h3 style={{ margin: 0, fontSize: 18, fontWeight: 600, color: '#111827' }}>
                  Discovery Results – {resultsUser.name || resultsUser.email}
                </h3>
                <p style={{ margin: 0, fontSize: 13, color: '#6b7280' }}>
                  View phase summaries and the final discovery report (if available).
                </p>
              </div>
              <button
                type="button"
                onClick={closeResults}
                style={{
                  border: 'none',
                  background: 'transparent',
                  fontSize: 22,
                  lineHeight: 1,
                  cursor: 'pointer',
                  color: '#9ca3af',
                }}
                aria-label="Close"
              >
                ×
              </button>
            </div>
            <div
              style={{
                padding: 20,
                overflow: 'auto',
              }}
            >
              {resultsLoading && (
                <div style={{ fontSize: 14, color: '#6b7280' }}>Loading discovery results…</div>
              )}
              {resultsError && (
                <div style={{ ...styles.error, marginBottom: 12 }}>{resultsError}</div>
              )}
              {resultsData && (
                <>
                  {[1, 2, 3, 4].map((phaseNum) => {
                    const key = String(phaseNum);
                    const summary = resultsData.phase_summaries?.[key];
                    if (!summary) return null;
                    const phase = PHASES[phaseNum] || `Phase ${phaseNum}`;
                    return (
                      <details key={key} style={{ marginBottom: 12 }}>
                        <summary
                          style={{
                            cursor: 'pointer',
                            fontSize: 14,
                            fontWeight: 600,
                            color: '#111827',
                            padding: '6px 0',
                          }}
                        >
                          Phase {phaseNum} – {phase}
                        </summary>
                        <div
                          style={{
                            marginTop: 4,
                            padding: 12,
                            borderRadius: 8,
                            background: '#f9fafb',
                            border: '1px solid #e5e7eb',
                            whiteSpace: 'pre-wrap',
                            fontSize: 14,
                            color: '#374151',
                          }}
                        >
                          {summary}
                        </div>
                      </details>
                    );
                  })}
                  {resultsData.final_report && (
                    <details open style={{ marginTop: 16 }}>
                      <summary
                        style={{
                          cursor: 'pointer',
                          fontSize: 14,
                          fontWeight: 600,
                          color: '#111827',
                          padding: '6px 0',
                        }}
                      >
                        Final Discovery Report
                      </summary>
                      <div
                        style={{
                          marginTop: 4,
                          padding: 12,
                          borderRadius: 8,
                          background: '#f9fafb',
                          border: '1px solid #e5e7eb',
                          whiteSpace: 'pre-wrap',
                          fontSize: 14,
                          color: '#374151',
                        }}
                      >
                        {resultsData.final_report}
                      </div>
                    </details>
                  )}
                  {!resultsData.final_report && !resultsData.phase_summaries && !resultsLoading && (
                    <div style={{ fontSize: 14, color: '#6b7280' }}>
                      No discovery results are available yet for this stakeholder.
                    </div>
                  )}
                </>
              )}
            </div>
          </div>
        </div>
      )}
      {consolidatedReportOpen && (
        <ConsolidatedReport
          projectId={id}
          onClose={() => setConsolidatedReportOpen(false)}
        />
      )}
      {deleteConfirmUser && (
        <div
          style={{
            position: 'fixed',
            inset: 0,
            background: 'rgba(15,23,42,0.45)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            padding: 24,
            zIndex: 1000,
          }}
          onClick={closeDeleteConfirm}
        >
          <div
            style={{
              background: '#fff',
              borderRadius: 12,
              boxShadow: '0 20px 60px rgba(15,23,42,0.4)',
              maxWidth: 480,
              width: '100%',
              padding: 20,
            }}
            onClick={(e) => e.stopPropagation()}
          >
            <h3 style={{ margin: '0 0 8px 0', fontSize: 18, fontWeight: 600, color: '#111827' }}>
              Remove Stakeholder?
            </h3>
            <p style={{ margin: '0 0 16px 0', fontSize: 14, color: '#4b5563', lineHeight: 1.5 }}>
              Are you sure you want to remove {deleteConfirmUser.name || deleteConfirmUser.email} from
              this project? This will remove their project assignment and{' '}
              <strong>all associated discovery data</strong>.
            </p>
            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 8 }}>
              <button
                type="button"
                onClick={closeDeleteConfirm}
                style={{
                  padding: '8px 14px',
                  fontSize: 14,
                  fontWeight: 500,
                  borderRadius: 6,
                  border: '1px solid #d1d5db',
                  background: '#ffffff',
                  color: '#374151',
                  cursor: 'pointer',
                }}
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={handleDelete}
                style={{
                  padding: '8px 16px',
                  fontSize: 14,
                  fontWeight: 600,
                  borderRadius: 6,
                  border: 'none',
                  background: '#b91c1c',
                  color: '#fff',
                  cursor: 'pointer',
                }}
              >
                Yes, Remove
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default ProjectDetail;
