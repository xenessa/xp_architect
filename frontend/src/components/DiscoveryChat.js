import { useState, useEffect, useRef, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  getSession,
  sendMessage,
  approveSummary,
  getReport,
} from '../services/api';

const PHASES = {
  1: 'Open Discovery - Tell me about your work',
  2: 'Targeted Follow-ups - Filling in the gaps',
  3: 'Validation - Confirming understanding',
  4: 'Future State - Defining success',
};

const PHASE_HEADER_NAMES = {
  1: 'Open Discovery',
  2: 'Targeted Follow-ups',
  3: 'Validation',
  4: 'Future State',
};

const styles = {
  page: {
    display: 'flex',
    flexDirection: 'column',
    height: '100vh',
    background: '#f8fafc',
  },
  header: {
    flexShrink: 0,
    padding: '12px 24px',
    background: '#fff',
    borderBottom: '1px solid #e2e8f0',
    boxShadow: '0 1px 3px rgba(0,0,0,0.04)',
  },
  headerRow: {
    maxWidth: 800,
    margin: '0 auto',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    gap: 16,
  },
  headerBtn: {
    padding: '8px 14px',
    fontSize: 14,
    fontWeight: 500,
    color: '#64748b',
    background: 'transparent',
    border: '1px solid #e2e8f0',
    borderRadius: 8,
    cursor: 'pointer',
    flexShrink: 0,
  },
  phaseCenter: {
    flex: 1,
    textAlign: 'center',
    fontSize: 15,
    fontWeight: 600,
    color: '#0f172a',
  },
  chatArea: {
    flex: 1,
    overflow: 'auto',
    padding: '20px 24px',
    display: 'flex',
    flexDirection: 'column',
    gap: 12,
    maxWidth: 800,
    margin: '0 auto',
    width: '100%',
  },
  bubble: {
    maxWidth: '85%',
    padding: '12px 16px',
    borderRadius: 16,
    fontSize: 15,
    lineHeight: 1.5,
    whiteSpace: 'pre-wrap',
    wordBreak: 'break-word',
  },
  bubbleAssistant: {
    alignSelf: 'flex-start',
    background: '#e2e8f0',
    color: '#1e293b',
    borderBottomLeftRadius: 4,
  },
  bubbleUser: {
    alignSelf: 'flex-end',
    background: '#2563eb',
    color: '#fff',
    borderBottomRightRadius: 4,
  },
  phaseDivider: {
    alignSelf: 'stretch',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    gap: 8,
    padding: '16px 24px',
    margin: '12px 0',
    background: '#f0f9ff',
    borderTop: '1px solid #bae6fd',
    borderBottom: '1px solid #bae6fd',
    borderRadius: 8,
  },
  phaseDividerText: {
    margin: 0,
    fontSize: 14,
    fontWeight: 600,
    color: '#0369a1',
    letterSpacing: '0.02em',
  },
  phaseDividerLabel: {
    margin: 0,
    fontSize: 13,
    color: '#64748b',
    fontWeight: 500,
  },
  toolbar: {
    flexShrink: 0,
    padding: '14px 24px',
    background: '#f1f5f9',
    borderTop: '1px solid #e2e8f0',
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    gap: 12,
    flexWrap: 'wrap',
  },
  toolbarInner: {
    maxWidth: 800,
    margin: '0 auto',
    display: 'flex',
    alignItems: 'center',
    gap: 12,
    flexWrap: 'wrap',
  },
  toolbarBtnPause: {
    padding: '10px 18px',
    fontSize: 14,
    fontWeight: 500,
    color: '#64748b',
    background: '#fff',
    border: '1px solid #cbd5e1',
    borderRadius: 8,
    cursor: 'pointer',
    transition: 'background 0.15s, border-color 0.15s, color 0.15s',
  },
  toolbarBtnEndPhase: {
    padding: '10px 18px',
    fontSize: 14,
    fontWeight: 600,
    color: '#1d4ed8',
    background: '#fff',
    border: '2px solid #2563eb',
    borderRadius: 8,
    cursor: 'pointer',
    transition: 'background 0.15s, border-color 0.15s, color 0.15s',
  },
  endPhaseConfirmOverlay: {
    position: 'fixed',
    inset: 0,
    background: 'rgba(0,0,0,0.4)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 24,
    zIndex: 1002,
  },
  endPhaseConfirmCard: {
    background: '#fff',
    borderRadius: 12,
    boxShadow: '0 20px 60px rgba(0,0,0,0.15)',
    maxWidth: 420,
    width: '100%',
    padding: 24,
  },
  endPhaseConfirmTitle: {
    margin: '0 0 12px 0',
    fontSize: 18,
    fontWeight: 600,
    color: '#0f172a',
  },
  endPhaseConfirmMessage: {
    margin: '0 0 24px 0',
    fontSize: 15,
    color: '#475569',
    lineHeight: 1.5,
  },
  endPhaseConfirmActions: {
    display: 'flex',
    justifyContent: 'flex-end',
    gap: 12,
  },
  endPhaseConfirmCancel: {
    padding: '10px 18px',
    fontSize: 14,
    fontWeight: 500,
    color: '#64748b',
    background: '#f1f5f9',
    border: '1px solid #e2e8f0',
    borderRadius: 8,
    cursor: 'pointer',
  },
  endPhaseConfirmYes: {
    padding: '10px 18px',
    fontSize: 14,
    fontWeight: 600,
    color: '#fff',
    background: '#2563eb',
    border: 'none',
    borderRadius: 8,
    cursor: 'pointer',
  },
  inputBar: {
    flexShrink: 0,
    padding: '16px 24px',
    background: '#fff',
    borderTop: '1px solid #e2e8f0',
    boxShadow: '0 -2px 10px rgba(0,0,0,0.04)',
  },
  inputInner: {
    maxWidth: 800,
    margin: '0 auto',
    display: 'flex',
    gap: 12,
    alignItems: 'flex-end',
  },
  input: {
    flex: 1,
    padding: '12px 16px',
    fontSize: 15,
    border: '2px solid #e2e8f0',
    borderRadius: 12,
    outline: 'none',
    resize: 'none',
    minHeight: 44,
    maxHeight: 120,
    fontFamily: 'inherit',
    transition: 'border-color 0.2s',
  },
  sendBtn: {
    flexShrink: 0,
    padding: '12px 24px',
    fontSize: 15,
    fontWeight: 600,
    color: '#fff',
    background: '#2563eb',
    border: 'none',
    borderRadius: 12,
    cursor: 'pointer',
  },
  sendBtnDisabled: {
    opacity: 0.6,
    cursor: 'not-allowed',
  },
  loadingRow: {
    alignSelf: 'flex-start',
    padding: '12px 16px',
    background: '#e2e8f0',
    borderRadius: 16,
    borderBottomLeftRadius: 4,
    fontSize: 14,
    color: '#64748b',
  },
  error: {
    padding: 12,
    margin: '0 24px 16px',
    background: '#fef2f2',
    border: '1px solid #fecaca',
    borderRadius: 8,
    fontSize: 14,
    color: '#b91c1c',
    maxWidth: 800,
    marginLeft: 'auto',
    marginRight: 'auto',
  },
  summaryOverlay: {
    position: 'fixed',
    inset: 0,
    background: 'rgba(0,0,0,0.4)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 24,
    zIndex: 1000,
  },
  summaryCard: {
    background: '#fff',
    borderRadius: 16,
    boxShadow: '0 20px 60px rgba(0,0,0,0.15)',
    maxWidth: 560,
    width: '100%',
    maxHeight: '85vh',
    overflow: 'hidden',
    display: 'flex',
    flexDirection: 'column',
  },
  summaryCardHeader: {
    padding: '20px 24px',
    borderBottom: '1px solid #e2e8f0',
    fontSize: 16,
    fontWeight: 600,
    color: '#0f172a',
  },
  summaryCardBody: {
    padding: 24,
    overflow: 'auto',
    fontSize: 15,
    lineHeight: 1.6,
    color: '#334155',
    whiteSpace: 'pre-wrap',
  },
  summaryCardLoading: {
    padding: 24,
    fontSize: 15,
    color: '#64748b',
    fontStyle: 'italic',
  },
  summaryCardActions: {
    padding: '16px 24px',
    borderTop: '1px solid #e2e8f0',
    display: 'flex',
    flexWrap: 'wrap',
    gap: 10,
  },
  summaryBtn: {
    padding: '10px 18px',
    fontSize: 14,
    fontWeight: 600,
    border: 'none',
    borderRadius: 8,
    cursor: 'pointer',
  },
  summaryBtnApprove: {
    background: '#10b981',
    color: '#fff',
  },
  summaryBtnSecondary: {
    background: '#f1f5f9',
    color: '#475569',
  },
  summaryFeedback: {
    width: '100%',
    marginTop: 12,
    padding: '12px 16px',
    fontSize: 14,
    border: '2px solid #e2e8f0',
    borderRadius: 8,
    outline: 'none',
    resize: 'vertical',
    minHeight: 80,
    fontFamily: 'inherit',
  },
  completeCard: {
    maxWidth: 560,
    margin: '24px auto',
    padding: 40,
    background: '#fff',
    borderRadius: 16,
    boxShadow: '0 4px 24px rgba(0,0,0,0.06)',
    textAlign: 'center',
  },
  completeTitle: {
    margin: '0 0 12px 0',
    fontSize: 24,
    fontWeight: 600,
    color: '#0f172a',
  },
  completeSub: {
    margin: '0 0 24px 0',
    fontSize: 16,
    color: '#64748b',
    lineHeight: 1.5,
  },
  viewReportBtn: {
    padding: '14px 28px',
    fontSize: 16,
    fontWeight: 600,
    color: '#fff',
    background: 'linear-gradient(135deg, #2563eb, #8b5cf6)',
    border: 'none',
    borderRadius: 12,
    cursor: 'pointer',
  },
  returnDashboardBtn: {
    marginTop: 12,
    padding: '12px 24px',
    fontSize: 15,
    fontWeight: 500,
    color: '#64748b',
    background: '#f1f5f9',
    border: '1px solid #e2e8f0',
    borderRadius: 12,
    cursor: 'pointer',
  },
  reportOverlay: {
    position: 'fixed',
    inset: 0,
    background: 'rgba(0,0,0,0.5)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 24,
    zIndex: 1001,
  },
  reportCard: {
    background: '#fff',
    borderRadius: 16,
    boxShadow: '0 20px 60px rgba(0,0,0,0.2)',
    maxWidth: 700,
    width: '100%',
    maxHeight: '90vh',
    overflow: 'hidden',
    display: 'flex',
    flexDirection: 'column',
  },
  reportCardHeader: {
    padding: '16px 24px',
    borderBottom: '1px solid #e2e8f0',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  reportCardTitle: {
    margin: 0,
    fontSize: 18,
    fontWeight: 600,
    color: '#0f172a',
  },
  reportClose: {
    background: 'none',
    border: 'none',
    fontSize: 24,
    color: '#64748b',
    cursor: 'pointer',
    lineHeight: 1,
    padding: 0,
  },
  reportCardBody: {
    padding: 24,
    overflow: 'auto',
    fontSize: 14,
    lineHeight: 1.7,
    color: '#334155',
    whiteSpace: 'pre-wrap',
  },
  loadingPage: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    height: '100vh',
    background: '#f8fafc',
    fontSize: 16,
    color: '#64748b',
  },
};

function DiscoveryChat() {
  const navigate = useNavigate();
  const [session, setSession] = useState(null);
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [inputValue, setInputValue] = useState('');
  const [sending, setSending] = useState(false);
  const [endingPhase, setEndingPhase] = useState(false);
  const [summaryForApproval, setSummaryForApproval] = useState(null);
  const [approvalMode, setApprovalMode] = useState(null);
  const [approvalFeedback, setApprovalFeedback] = useState('');
  const [submittingApproval, setSubmittingApproval] = useState(false);
  const [reportContent, setReportContent] = useState(null);
  const [loadingReport, setLoadingReport] = useState(false);
  const [showEndPhaseConfirm, setShowEndPhaseConfirm] = useState(false);
  const [toolbarHover, setToolbarHover] = useState(null);
  const [awaitingPhaseStart, setAwaitingPhaseStart] = useState(false);
  const chatEndRef = useRef(null);
  const chatAreaRef = useRef(null);
  const hasInitializedRef = useRef(false);
  const draftTimeoutRef = useRef(null);

  const DRAFT_STORAGE_KEY = 'discovery_chat_draft';
  const urlParams = new URLSearchParams(window.location.search);
  const isDemoMode = urlParams.get('demo') === 'true';

  // Restore draft on mount
  useEffect(() => {
    try {
      const draft = localStorage.getItem(DRAFT_STORAGE_KEY);
      if (draft) {
        setInputValue(draft);
      }
    } catch {
      // Ignore storage errors
    }
  }, []);

  // Debounced auto-save of draft as user types
  useEffect(() => {
    try {
      if (draftTimeoutRef.current) {
        clearTimeout(draftTimeoutRef.current);
      }
      draftTimeoutRef.current = setTimeout(() => {
        if (inputValue) {
          localStorage.setItem(DRAFT_STORAGE_KEY, inputValue);
        } else {
          localStorage.removeItem(DRAFT_STORAGE_KEY);
        }
      }, 500);
    } catch {
      // Ignore storage errors
    }

    return () => {
      if (draftTimeoutRef.current) {
        clearTimeout(draftTimeoutRef.current);
      }
    };
  }, [inputValue]);

  const loadSession = async () => {
    setError('');
    try {
      const res = await getSession();
      const data = res.data;
      setSession(data);
      if (Array.isArray(data.all_messages) && data.all_messages.length > 0) {
        setMessages(data.all_messages);
      }
      if (data.pending_phase_summary) {
        setSummaryForApproval({ summary: data.pending_phase_summary });
      }
    } catch (err) {
      const detail = err.response?.data?.detail;
      setError(Array.isArray(detail) ? detail.join(' ') : detail || 'Failed to load session.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadSession();
  }, []);

  useEffect(() => {
    if (!session || hasInitializedRef.current) return;
    hasInitializedRef.current = true;

    if (session.status === 'COMPLETED') return;

    const hasMessages = Array.isArray(session.all_messages) && session.all_messages.length > 0;

    if (session.status === 'NOT_STARTED') {
      if (hasMessages) return;
      setSending(true);
      setError('');
      setMessages((prev) => [...prev, { role: 'user', content: 'BEGIN_SESSION' }]);
      sendMessage('BEGIN_SESSION')
        .then((res) => {
          const { assistant_message } = res.data;
          setMessages((prev) => [...prev, { role: 'assistant', content: assistant_message }]);
          return loadSession();
        })
        .catch((err) => {
          const detail = err.response?.data?.detail;
          setError(Array.isArray(detail) ? detail.join(' ') : detail || 'Failed to start session.');
          setMessages((prev) => prev.slice(0, -1));
          hasInitializedRef.current = false;
        })
        .finally(() => setSending(false));
      return;
    }
  }, [session]);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, sending]);

  // Trigger phase-end flow when a new assistant message contains phase-end phrases
  const triggerEndPhaseIfNeeded = useCallback(async () => {
    if (sending || endingPhase || !session || session.status === 'COMPLETED' || summaryForApproval) return;
    setEndingPhase(true);
    setError('');
    try {
      const res = await sendMessage('next');
      const { assistant_message: nextMsg, phase_completed: pc, summary: sum } = res.data;
      if (nextMsg) setMessages((prev) => [...prev, { role: 'assistant', content: nextMsg }]);
      if (pc && sum) setSummaryForApproval({ summary: sum });
      await loadSession();
    } catch (err) {
      const detail = err.response?.data?.detail;
      setError(Array.isArray(detail) ? detail.join(' ') : detail || 'Failed to end phase.');
    } finally {
      setEndingPhase(false);
    }
  }, [session, summaryForApproval, sending, endingPhase]);

  useEffect(() => {
    if (!messages.length) return;
    const last = messages[messages.length - 1];
    if (!last || last.role !== 'assistant') return;
    const content = (last.content || '').toLowerCase();
    const triggerPhrases = [
      'compile a summary',
      'generate a summary',
      'i have what i need for this phase',
      'summary for your review',
      'summary should be appearing',
      'compile a summary for your review',
      'generate a summary for your review',
      'presenting the summary for your review',
    ];
    const shouldTrigger = triggerPhrases.some((phrase) => content.includes(phrase));
    console.log('[DiscoveryChat] New AI message received:', content.substring(0, 80) + (content.length > 80 ? '...' : ''));
    console.log('[DiscoveryChat] Trigger check:', shouldTrigger, 'summaryForApproval:', !!summaryForApproval, 'sending:', sending, 'endingPhase:', endingPhase);
    if (shouldTrigger && !summaryForApproval && !sending && !endingPhase) {
      console.log('[DiscoveryChat] Triggering end phase flow...');
      triggerEndPhaseIfNeeded();
    }
  }, [messages, summaryForApproval, sending, endingPhase, triggerEndPhaseIfNeeded]);

  const handleSend = async (e) => {
    e?.preventDefault();
    const text = inputValue.trim();
    console.log('[DiscoveryChat] handleSend called, text:', text?.substring(0, 50));
    if (!text || sending || !session) return;
    if (session.status === 'COMPLETED') return;
    setMessages((prev) => [...prev, { role: 'user', content: text }]);
    setSending(true);
    setError('');
    try {
      const res = await sendMessage(text);
      const { assistant_message, phase_completed, summary, phase_complete_suggested } = res.data;
      console.log('[DiscoveryChat] API response received:', {
        hasAssistant: !!assistant_message,
        phase_completed,
        hasSummary: !!summary,
        phase_complete_suggested,
      });
      setMessages((prev) => [...prev, { role: 'assistant', content: assistant_message }]);

      // Auto-trigger phase summary modal when AI signals readiness
      const triggerPhrases = [
        'compile a summary for your review',
        'generate a summary for your review',
        'compile a summary for you to review',
        'generate a summary for you to review',
        'presenting the summary for your review',
      ];
      const lowerMsg = (assistant_message || '').toLowerCase();
      const shouldTriggerSummary =
        phase_complete_suggested === true || triggerPhrases.some((p) => lowerMsg.includes(p));

      if (shouldTriggerSummary && !phase_completed && !summary) {
        const nextRes = await sendMessage('next');
        const { assistant_message: nextMsg, phase_completed: pc, summary: sum } = nextRes.data;
        if (nextMsg) setMessages((prev) => [...prev, { role: 'assistant', content: nextMsg }]);
        if (pc && sum) setSummaryForApproval({ summary: sum });
      } else if (phase_completed && summary) {
        setSummaryForApproval({ summary });
      }

      await loadSession();
      setInputValue('');
      try {
        localStorage.removeItem(DRAFT_STORAGE_KEY);
      } catch {
        // Ignore storage errors
      }
    } catch (err) {
      const detail = err.response?.data?.detail;
      const detailMessage = Array.isArray(detail) ? detail.join(' ') : detail;
      setError(detailMessage || 'Failed to send. Please try again.');
      setMessages((prev) => prev.slice(0, -1));
    } finally {
      setSending(false);
    }
  };

  const handleApprove = async (action, feedback = null) => {
    setSubmittingApproval(true);
    setError('');
    try {
      const res = await approveSummary(action, feedback);
      const newSession = res.data;
      const prevPhase = session?.current_phase ?? 1;
      setSession(newSession);
      if (action === 'approve') {
        setSummaryForApproval(null);
        setApprovalMode(null);
        setApprovalFeedback('');
        if (newSession.status === 'COMPLETED') {
          setMessages((prev) => [
            ...prev,
            {
              role: 'assistant',
              content: "Discovery Complete! You've finished all four phases. You can view your discovery report below.",
            },
          ]);
        } else if (newSession.current_phase > prevPhase) {
          setMessages((prev) => [
            ...prev,
            { type: 'phase_complete', phase: prevPhase },
          ]);
          setAwaitingPhaseStart(true);
        }
      } else {
        setSummaryForApproval({
          summary: newSession.pending_phase_summary ?? summaryForApproval?.summary ?? '',
          isRevised: true,
        });
        setApprovalMode(null);
        setApprovalFeedback('');
      }
    } catch (err) {
      const detail = err.response?.data?.detail;
      setError(Array.isArray(detail) ? detail.join(' ') : detail || 'Failed to submit.');
    } finally {
      setSubmittingApproval(false);
    }
  };

  const handleViewReport = async () => {
    setLoadingReport(true);
    setError('');
    try {
      const res = await getReport();
      setReportContent(res.data.report_content || '');
    } catch (err) {
      const detail = err.response?.data?.detail;
      setError(Array.isArray(detail) ? detail.join(' ') : detail || 'Failed to load report.');
    } finally {
      setLoadingReport(false);
    }
  };

  const closeReport = () => setReportContent(null);

  const handlePauseSession = () => navigate('/stakeholder-dashboard');
  const handleBeginPhaseClick = async () => {
    if (sending || endingPhase || !session || session.status === 'COMPLETED') return;
    setSending(true);
    setError('');
    try {
      const res = await sendMessage('BEGIN_PHASE');
      const { assistant_message } = res.data;
      setMessages((prev) => [...prev, { role: 'assistant', content: assistant_message }]);
      await loadSession();
      setAwaitingPhaseStart(false);
    } catch (err) {
      const detail = err.response?.data?.detail;
      setError(Array.isArray(detail) ? detail.join(' ') : detail || 'Failed to start next phase.');
    } finally {
      setSending(false);
    }
  };
  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    navigate('/', { replace: true });
  };

  const handleEndPhaseClick = () => {
    if (sending || endingPhase || !session || session.status === 'COMPLETED') return;
    setShowEndPhaseConfirm(true);
  };

  const handleEndPhaseConfirm = async () => {
    setShowEndPhaseConfirm(false);
    if (sending || endingPhase || !session || session.status === 'COMPLETED') return;
    setEndingPhase(true);
    setError('');
    setMessages((prev) => [...prev, { role: 'user', content: 'next' }]);
    try {
      const res = await sendMessage('next');
      const { assistant_message, phase_completed, summary } = res.data;
      setMessages((prev) => [...prev, { role: 'assistant', content: assistant_message }]);
      if (phase_completed && summary) {
        setSummaryForApproval({ summary });
      }
      await loadSession();
    } catch (err) {
      const detail = err.response?.data?.detail;
      setError(Array.isArray(detail) ? detail.join(' ') : detail || 'Failed to end phase.');
      setMessages((prev) => prev.slice(0, -1));
    } finally {
      setEndingPhase(false);
    }
  };

  // Reset awaitingPhaseStart when session resets or completes
  useEffect(() => {
    if (!session || session.status === 'COMPLETED') {
      setAwaitingPhaseStart(false);
    }
  }, [session]);

  if (loading) {
    return <div style={styles.loadingPage}>Loading session…</div>;
  }

  if (error && !session) {
    return (
      <div style={styles.page}>
        <div style={styles.error}>{error}</div>
      </div>
    );
  }

  const phase = session?.current_phase ?? 1;
  const phaseProgress = Math.min(4, Math.max(1, phase));
  const isComplete = session?.status === 'COMPLETED';

  return (
    <div style={styles.page}>
      <header style={styles.header}>
        <div style={styles.headerRow}>
          <button type="button" style={styles.headerBtn} onClick={() => navigate('/stakeholder-dashboard')}>
            ← Back
          </button>
          <span style={styles.phaseCenter}>
            Phase {phaseProgress} of 4: {PHASE_HEADER_NAMES[phaseProgress] || 'Discovery'}
          </span>
          <button type="button" style={styles.headerBtn} onClick={handleLogout}>
            Logout
          </button>
        </div>
      </header>

      {error && <div style={styles.error}>{error}</div>}

      <div ref={chatAreaRef} style={styles.chatArea}>
        {messages.length === 0 && !isComplete && (
          <div style={{ ...styles.bubble, ...styles.bubbleAssistant }}>
            Start the conversation below. Share your context and we'll work through the discovery phases together.
          </div>
        )}
        {messages.map((msg, i) =>
          msg.type === 'phase_complete' ? (
            <div key={i} style={styles.phaseDivider}>
              <p style={styles.phaseDividerText}>Phase {msg.phase} Complete ✓</p>
              <p style={styles.phaseDividerLabel}>
                {PHASE_HEADER_NAMES[msg.phase] || 'Discovery'}
              </p>
            </div>
          ) : (
            <div
              key={i}
              style={{
                ...styles.bubble,
                ...(msg.role === 'user' ? styles.bubbleUser : styles.bubbleAssistant),
              }}
            >
              {msg.content}
            </div>
          )
        )}
        {sending && <div style={styles.loadingRow}>Thinking…</div>}
        <div ref={chatEndRef} />
      </div>

      {!isComplete && (
        <>
          <div style={styles.toolbar}>
            <div style={styles.toolbarInner}>
              <button
                type="button"
                style={{
                  ...styles.toolbarBtnPause,
                  ...(toolbarHover === 'pause' ? { background: '#e2e8f0', borderColor: '#94a3b8' } : {}),
                }}
                onClick={awaitingPhaseStart ? handleBeginPhaseClick : handlePauseSession}
                onMouseEnter={() => setToolbarHover('pause')}
                onMouseLeave={() => setToolbarHover(null)}
              >
                {awaitingPhaseStart ? 'Begin Phase' : 'Pause Session'}
              </button>
              {isDemoMode && (
                <button
                  type="button"
                  style={{
                    ...styles.toolbarBtnEndPhase,
                    ...(toolbarHover === 'endPhase' ? { background: '#eff6ff', borderColor: '#1d4ed8' } : {}),
                    ...(sending || endingPhase ? { opacity: 0.7, cursor: 'not-allowed' } : {}),
                  }}
                  onClick={handleEndPhaseClick}
                  onMouseEnter={() => !sending && !endingPhase && setToolbarHover('endPhase')}
                  onMouseLeave={() => setToolbarHover(null)}
                  disabled={sending || endingPhase}
                >
                  {endingPhase ? 'Ending phase…' : 'End Phase'}
                </button>
              )}
            </div>
          </div>
          <div style={styles.inputBar}>
            <form style={styles.inputInner} onSubmit={handleSend}>
              <textarea
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    handleSend();
                  }
                }}
                style={styles.input}
                placeholder="Type your message…"
                disabled={sending || endingPhase}
                rows={1}
              />
              <button
                type="submit"
                style={{
                  ...styles.sendBtn,
                  ...(sending || endingPhase ? styles.sendBtnDisabled : {}),
                }}
                disabled={sending || endingPhase || !inputValue.trim()}
              >
                Send
              </button>
            </form>
          </div>
        </>
      )}

      {isComplete && (
        <div style={styles.completeCard}>
          <h2 style={styles.completeTitle}>Discovery Complete!</h2>
          <p style={styles.completeSub}>
            You've finished all four phases. Review your discovery report or return to your dashboard.
          </p>
          <button
            type="button"
            style={styles.viewReportBtn}
            onClick={handleViewReport}
            disabled={loadingReport}
          >
            {loadingReport ? 'Loading…' : 'View Report'}
          </button>
          <button
            type="button"
            style={styles.returnDashboardBtn}
            onClick={() => navigate('/stakeholder-dashboard')}
          >
            Return to Dashboard
          </button>
        </div>
      )}

      {summaryForApproval && (
        <div style={styles.summaryOverlay}>
          <div style={styles.summaryCard}>
            <div style={styles.summaryCardHeader}>
              {summaryForApproval.isRevised ? 'Updated Summary' : 'Phase summary – review and approve'}
            </div>
            {submittingApproval ? (
              <div style={styles.summaryCardLoading}>Generating updated summary…</div>
            ) : (
              <div style={styles.summaryCardBody}>{summaryForApproval.summary}</div>
            )}
            <div style={styles.summaryCardActions}>
              <button
                type="button"
                style={{ ...styles.summaryBtn, ...styles.summaryBtnApprove }}
                onClick={() => handleApprove('approve')}
                disabled={submittingApproval}
              >
                Approve
              </button>
              {approvalMode !== 'request_changes' && (
                <button
                  type="button"
                  style={{ ...styles.summaryBtn, ...styles.summaryBtnSecondary }}
                  onClick={() => setApprovalMode('request_changes')}
                  disabled={submittingApproval}
                >
                  Request Updates
                </button>
              )}
              {(approvalMode === 'request_changes') && (
                <>
                  <textarea
                    value={approvalFeedback}
                    onChange={(e) => setApprovalFeedback(e.target.value)}
                    style={styles.summaryFeedback}
                    placeholder={
                      approvalMode === 'request_changes'
                        ? 'Describe what you’d like changed…'
                        : 'Describe changes, additions, or corrections'
                    }
                    disabled={submittingApproval}
                  />
                  <button
                    type="button"
                    style={{ ...styles.summaryBtn, ...styles.summaryBtnApprove }}
                    onClick={() => handleApprove('request_changes', approvalFeedback.trim() || null)}
                    disabled={submittingApproval}
                  >
                    Submit Updates
                  </button>
                  <button
                    type="button"
                    style={{ ...styles.summaryBtn, ...styles.summaryBtnSecondary }}
                    onClick={() => {
                      setApprovalMode(null);
                      setApprovalFeedback('');
                    }}
                    disabled={submittingApproval}
                  >
                    Cancel
                  </button>
                </>
              )}
            </div>
          </div>
        </div>
      )}

      {showEndPhaseConfirm && (
        <div style={styles.endPhaseConfirmOverlay} onClick={() => setShowEndPhaseConfirm(false)}>
          <div style={styles.endPhaseConfirmCard} onClick={(e) => e.stopPropagation()}>
            <h3 style={styles.endPhaseConfirmTitle}>End Phase {phaseProgress}?</h3>
            <p style={styles.endPhaseConfirmMessage}>
              Are you ready to move on to the next phase?
            </p>
            <div style={styles.endPhaseConfirmActions}>
              <button
                type="button"
                style={styles.endPhaseConfirmCancel}
                onClick={() => setShowEndPhaseConfirm(false)}
              >
                Cancel
              </button>
              <button
                type="button"
                style={styles.endPhaseConfirmYes}
                onClick={handleEndPhaseConfirm}
              >
                Yes, Continue
              </button>
            </div>
          </div>
        </div>
      )}

      {reportContent !== null && (
        <div style={styles.reportOverlay} onClick={closeReport}>
          <div style={styles.reportCard} onClick={(e) => e.stopPropagation()}>
            <div style={styles.reportCardHeader}>
              <h2 style={styles.reportCardTitle}>Discovery Report</h2>
              <button type="button" style={styles.reportClose} onClick={closeReport} aria-label="Close">
                ×
              </button>
            </div>
            <div style={styles.reportCardBody}>{reportContent}</div>
          </div>
        </div>
      )}
    </div>
  );
}

export default DiscoveryChat;
