import { useState, useEffect } from 'react';
import { getConsolidatedReport } from '../services/api';

const styles = {
  overlay: {
    position: 'fixed',
    inset: 0,
    background: 'rgba(15,23,42,0.45)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 24,
    zIndex: 1000,
  },
  modal: {
    background: '#fff',
    borderRadius: 12,
    boxShadow: '0 20px 60px rgba(15,23,42,0.4)',
    maxWidth: 900,
    width: '100%',
    maxHeight: '90vh',
    display: 'flex',
    flexDirection: 'column',
  },
  header: {
    padding: '16px 20px',
    borderBottom: '1px solid #e5e7eb',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    flexWrap: 'wrap',
    gap: 12,
  },
  title: {
    margin: 0,
    fontSize: 18,
    fontWeight: 600,
    color: '#111827',
  },
  meta: {
    margin: 0,
    fontSize: 13,
    color: '#6b7280',
  },
  headerRight: {
    display: 'flex',
    alignItems: 'center',
    gap: 8,
  },
  regenerateBtn: {
    padding: '8px 14px',
    fontSize: 13,
    fontWeight: 500,
    borderRadius: 6,
    border: '1px solid #d1d5db',
    background: '#ffffff',
    color: '#374151',
    cursor: 'pointer',
  },
  closeBtn: {
    border: 'none',
    background: 'transparent',
    fontSize: 22,
    lineHeight: 1,
    cursor: 'pointer',
    color: '#9ca3af',
  },
  body: {
    padding: 20,
    overflow: 'auto',
    flex: 1,
  },
  reportContent: {
    whiteSpace: 'pre-wrap',
    fontSize: 14,
    color: '#374151',
    lineHeight: 1.6,
    fontFamily: 'inherit',
  },
  loading: {
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
  },
};

function ConsolidatedReport({ projectId, onClose }) {
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(true);
  const [regenerating, setRegenerating] = useState(false);
  const [error, setError] = useState('');

  const fetchReport = async (forceRegenerate = false) => {
    if (!projectId) return;
    setError('');
    if (forceRegenerate) {
      setRegenerating(true);
    } else {
      setLoading(true);
    }
    try {
      const res = await getConsolidatedReport(projectId, forceRegenerate);
      setReport(res.data);
    } catch (err) {
      const detail = err.response?.data?.detail;
      setError(Array.isArray(detail) ? detail.join(' ') : detail || 'Failed to load consolidated report.');
    } finally {
      setLoading(false);
      setRegenerating(false);
    }
  };

  useEffect(() => {
    fetchReport(false);
  }, [projectId]);

  const handleRegenerate = () => {
    fetchReport(true);
  };

  return (
    <div style={styles.overlay} onClick={onClose}>
      <div style={styles.modal} onClick={(e) => e.stopPropagation()}>
        <div style={styles.header}>
          <div>
            <h3 style={styles.title}>Consolidated Discovery Report</h3>
            {report && (
              <p style={styles.meta}>
                Synthesized from {report.stakeholder_count} stakeholder{report.stakeholder_count !== 1 ? 's' : ''}
                {report.generated_at && (
                  <> · Generated {new Date(report.generated_at).toLocaleDateString()}</>
                )}
              </p>
            )}
          </div>
          <div style={styles.headerRight}>
            {report && (
              <button
                type="button"
                style={styles.regenerateBtn}
                onClick={handleRegenerate}
                disabled={regenerating}
              >
                {regenerating ? 'Regenerating…' : 'Regenerate Report'}
              </button>
            )}
            <button type="button" style={styles.closeBtn} onClick={onClose} aria-label="Close">
              ×
            </button>
          </div>
        </div>
        <div style={styles.body}>
          {loading && !report && (
            <div style={styles.loading}>Generating consolidated report…</div>
          )}
          {regenerating && report && (
            <div style={styles.loading}>Regenerating consolidated report…</div>
          )}
          {error && <div style={styles.error}>{error}</div>}
          {report && !regenerating && (
            <div style={styles.reportContent}>{report.report_content}</div>
          )}
        </div>
      </div>
    </div>
  );
}

export default ConsolidatedReport;
