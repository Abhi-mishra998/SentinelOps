import { Incident } from '../types'

interface IncidentCardProps {
  incident: Incident
  onClick: () => void
  onExecute: () => void
  onReview: () => void
}

const TYPE_LABEL: Record<string, string> = {
  pod_crashloop: 'CrashLoop',
  image_pull_error: 'ImagePull',
  oom_killed: 'OOMKilled',
  pending_pod: 'Pending',
  config_error: 'ConfigErr',
}

const CONFIDENCE_BADGE: Record<string, string> = {
  high: 'badge-danger',
  medium: 'badge-warning',
  low: 'badge-neutral',
}

const TYPE_BADGE: Record<string, string> = {
  pod_crashloop: 'badge-danger',
  image_pull_error: 'badge-warning',
  oom_killed: 'badge-danger',
  pending_pod: 'badge-warning',
  config_error: 'badge-warning',
}

const STATUS_BADGE: Record<string, string> = {
  active: 'badge-danger',
  pending: 'badge-warning',
  resolved: 'badge-success',
}

function timeAgo(iso: string): string {
  const diff = Math.floor((Date.now() - new Date(iso).getTime()) / 1000)
  if (diff < 60) return `${diff}s ago`
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`
  return `${Math.floor(diff / 3600)}h ago`
}

export const IncidentCard = ({ incident, onClick, onExecute, onReview }: IncidentCardProps) => {
  const typeBadge = TYPE_BADGE[incident.incident_type] || 'badge-neutral'
  const confBadge = CONFIDENCE_BADGE[incident.confidence] || 'badge-neutral'
  const statusBadge = STATUS_BADGE[incident.status || 'active'] || 'badge-neutral'

  return (
    <div
      className="incident-card animate-in"
      onClick={onClick}
      role="button"
      tabIndex={0}
      onKeyDown={e => e.key === 'Enter' && onClick()}
      aria-label={`Incident: ${incident.pod_name}`}
    >
      {/* Header */}
      <div className="incident-card-header">
        <div style={{ flex: 1, minWidth: 0 }}>
          <div className="incident-pod-name">{incident.pod_name}</div>
          <div className="incident-namespace">ns: {incident.namespace}</div>
        </div>
        <div className="incident-time">{timeAgo(incident.created_at)}</div>
      </div>

      {/* Badges */}
      <div className="incident-badges">
        <span className={`badge ${typeBadge}`}>
          {TYPE_LABEL[incident.incident_type] || incident.incident_type.replace('_', ' ')}
        </span>
        <span className={`badge ${confBadge}`}>
          {incident.confidence} confidence
        </span>
        <span className={`badge ${statusBadge}`}>
          {incident.status || 'active'}
        </span>
        <span className="badge badge-info">{incident.source}</span>
      </div>

      {/* Root cause */}
      <p className="incident-root-cause">{incident.root_cause}</p>

      {/* Recommended action */}
      <div className="incident-cmd" title={incident.recommended_action}>
        $ {incident.recommended_action.split('\n')[0]}
      </div>

      {/* Action buttons */}
      <div className="incident-actions" onClick={e => e.stopPropagation()}>
        <button
          id={`execute-${incident.incident_id}`}
          className="btn btn-primary btn-sm"
          style={{ flex: 1 }}
          onClick={e => { e.stopPropagation(); onExecute(); }}
          title="Execute auto-fix for this incident"
        >
          ⚡ Execute Fix
        </button>
        <button
          id={`review-${incident.incident_id}`}
          className="btn btn-secondary btn-sm"
          style={{ flex: 1 }}
          onClick={e => { e.stopPropagation(); onReview(); }}
          title="Queue for human review"
        >
          👁 Review
        </button>
      </div>
    </div>
  )
}
