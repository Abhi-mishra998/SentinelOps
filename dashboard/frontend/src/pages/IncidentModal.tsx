import { Incident } from '../types'
import { useIncidents } from '../hooks/useIncidents'

interface IncidentModalProps {
  incident: Incident | null
  onClose: () => void
}

function timeAgo(iso: string): string {
  const diff = Math.floor((Date.now() - new Date(iso).getTime()) / 1000)
  if (diff < 60) return `${diff}s ago`
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`
  return `${Math.floor(diff / 3600)}h ago`
}

const CONFIDENCE_COLOR: Record<string, string> = {
  high: '#f87171',
  medium: '#fbbf24',
  low: '#64748b',
}

const TYPE_LABEL: Record<string, string> = {
  pod_crashloop: '🔄 CrashLoopBackOff',
  image_pull_error: '📦 ImagePullError',
  oom_killed: '💥 OOMKilled',
  pending_pod: '⏳ PodPending',
  config_error: '⚙️ ConfigError',
}

export const IncidentModal = ({ incident, onClose }: IncidentModalProps) => {
  const { handleAction } = useIncidents()

  if (!incident) return null

  const cmds = incident.recommended_action.split('\n').filter(Boolean)

  return (
    <div
      className="modal-overlay"
      onClick={onClose}
      role="dialog"
      aria-modal="true"
      aria-labelledby="modal-title"
    >
      <div className="modal-content" onClick={e => e.stopPropagation()}>
        {/* Header */}
        <div className="modal-header">
          <div>
            <div className="modal-title" id="modal-title">{incident.pod_name}</div>
            <div className="modal-subtitle">
              namespace: <strong style={{ color: 'var(--text-dim)' }}>{incident.namespace}</strong>
              &nbsp;•&nbsp;{timeAgo(incident.created_at)}
              &nbsp;•&nbsp;{new Date(incident.created_at).toLocaleString()}
            </div>
          </div>
          <button className="modal-close" onClick={onClose} aria-label="Close modal">✕</button>
        </div>

        {/* Body */}
        <div className="modal-body">
          {/* Badges row */}
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, marginBottom: 24 }}>
            <span className="badge badge-info">
              {TYPE_LABEL[incident.incident_type] || incident.incident_type.replace(/_/g, ' ')}
            </span>
            <span
              className="badge"
              style={{
                background: `${CONFIDENCE_COLOR[incident.confidence]}22`,
                borderColor: `${CONFIDENCE_COLOR[incident.confidence]}55`,
                color: CONFIDENCE_COLOR[incident.confidence],
              }}
            >
              {incident.confidence.toUpperCase()} CONFIDENCE
            </span>
            <span className="badge badge-purple">{incident.source}</span>
            <span className={`badge ${incident.status === 'active' ? 'badge-danger' : incident.status === 'pending' ? 'badge-warning' : 'badge-success'}`}>
              {(incident.status || 'active').toUpperCase()}
            </span>
          </div>

          {/* Root Cause */}
          <div style={{ marginBottom: 20 }}>
            <div style={{ fontSize: '0.72rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 8 }}>
              🔍 Root Cause Analysis
            </div>
            <p style={{ color: 'var(--text-dim)', fontSize: '0.9rem', lineHeight: 1.7, background: 'var(--bg-secondary)', borderRadius: 'var(--radius)', padding: '14px 16px', border: '1px solid var(--border)' }}>
              {incident.root_cause}
            </p>
          </div>

          {/* Explanation */}
          {incident.explanation && (
            <div style={{ marginBottom: 20 }}>
              <div style={{ fontSize: '0.72rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 8 }}>
                💡 AI Explanation
              </div>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', lineHeight: 1.7, fontStyle: 'italic', background: 'var(--bg-secondary)', borderRadius: 'var(--radius)', padding: '14px 16px', border: '1px solid var(--border)' }}>
                "{incident.explanation}"
              </p>
            </div>
          )}

          {/* Recommended Action */}
          <div>
            <div style={{ fontSize: '0.72rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 8 }}>
              🛠 Recommended Remediation
            </div>
            <div className="code-block">
              <div className="code-header">
                <span className="code-lang">bash</span>
                <button
                  className="btn btn-ghost btn-sm"
                  style={{ fontSize: '0.7rem', padding: '2px 8px' }}
                  onClick={() => navigator.clipboard?.writeText(incident.recommended_action)}
                  title="Copy to clipboard"
                >
                  📋 Copy
                </button>
              </div>
              {cmds.map((cmd, i) => (
                <div key={i} style={{ lineHeight: '1.8' }}>
                  {cmd.startsWith('#') ? (
                    <span style={{ color: 'var(--text-muted)', fontStyle: 'italic' }}>{cmd}</span>
                  ) : (
                    <span>
                      <span style={{ color: 'var(--text-muted)', userSelect: 'none' }}>$ </span>
                      {cmd}
                    </span>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="modal-footer">
          <button
            id="modal-execute-btn"
            className="btn btn-primary btn-lg"
            style={{ flex: 1 }}
            onClick={() => { handleAction(incident, true); onClose(); }}
          >
            ⚡ Execute Auto-Fix
          </button>
          <button
            id="modal-review-btn"
            className="btn btn-secondary btn-lg"
            style={{ flex: 1 }}
            onClick={() => { handleAction(incident, false); onClose(); }}
          >
            👁 Queue for Review
          </button>
          <button
            className="btn btn-ghost btn-lg"
            onClick={onClose}
          >
            Close
          </button>
        </div>
      </div>
    </div>
  )
}
