import { ClusterStats, Incident, ActivityEvent, WsStatus } from '../types'
import { IncidentCard } from '../components/IncidentCard'

interface DashboardProps {
  incidents: Incident[]
  stats: ClusterStats
  activity: ActivityEvent[]
  isLoading: boolean
  wsStatus: WsStatus
  activeIncidents: number
  searchTerm: string
  onSelectIncident: (inc: Incident) => void
  onExecute: (inc: Incident) => void
  onReview: (inc: Incident) => void
}

const SkeletonCard = () => (
  <div className="skeleton-card">
    <div className="skeleton" style={{ height: 20, width: '70%' }} />
    <div className="skeleton" style={{ height: 14, width: '40%' }} />
    <div style={{ display: 'flex', gap: 6 }}>
      <div className="skeleton" style={{ height: 22, width: 80, borderRadius: 20 }} />
      <div className="skeleton" style={{ height: 22, width: 90, borderRadius: 20 }} />
    </div>
    <div className="skeleton" style={{ height: 40 }} />
    <div className="skeleton" style={{ height: 36 }} />
    <div style={{ display: 'flex', gap: 8 }}>
      <div className="skeleton" style={{ height: 34, flex: 1 }} />
      <div className="skeleton" style={{ height: 34, flex: 1 }} />
    </div>
  </div>
)

function timeAgo(iso: string): string {
  const diff = Math.floor((Date.now() - new Date(iso).getTime()) / 1000)
  if (diff < 60) return `${diff}s ago`
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`
  return `${Math.floor(diff / 3600)}h ago`
}

const ACTIVITY_COLORS: Record<string, string> = {
  incident: '#ef4444',
  remediation: '#10b981',
  approval: '#6366f1',
  alert: '#f59e0b',
}
const ACTIVITY_ICONS: Record<string, string> = {
  incident: '⚠',
  remediation: '⚡',
  approval: '✅',
  alert: '🔔',
}

export const Dashboard = ({
  incidents, stats, activity, isLoading, wsStatus,
  activeIncidents, searchTerm, onSelectIncident, onExecute, onReview
}: DashboardProps) => {
  const filtered = incidents.filter(inc =>
    inc.pod_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    inc.namespace.toLowerCase().includes(searchTerm.toLowerCase()) ||
    inc.root_cause.toLowerCase().includes(searchTerm.toLowerCase())
  )

  const healthPct = stats.total_pods > 0
    ? Math.round((stats.healthy_pods / stats.total_pods) * 100)
    : 100

  return (
    <div>
      {/* Page Header */}
      <div className="page-header">
        <h1 className="page-title gradient-text">Operations Dashboard</h1>
        <p className="page-subtitle">
          Real-time Kubernetes incident monitoring & AI-powered auto-remediation
        </p>
      </div>

      {/* Cluster Health Center */}
      <div className="ops-hub-header">
        <h2 className="ops-hub-title">
          <span style={{ color: 'var(--accent)' }}>◈</span>
          Cluster Health Center
        </h2>
        <div className="ops-hub-badge">Live Infrastructure</div>
      </div>

      <div className="health-center-grid">
        {/* Core Reliability */}
        <div className="health-card">
          <div className="health-card-glow" />
          <div className="health-card-header">
            <span className="health-card-title">Core Reliability</span>
            <div className="health-card-icon" title="Aggregated cluster health">◉</div>
          </div>
          <div className="health-card-main">
            <div className="health-card-value">{healthPct}%</div>
            <div className="health-card-label">Overall Health Score</div>
          </div>
          <div className="health-card-footer">
            <div className="health-status-bar">
              <div className="health-status-fill" style={{ width: `${healthPct}%`, background: healthPct > 90 ? 'var(--success)' : healthPct > 70 ? 'var(--warning)' : 'var(--danger)' }} />
            </div>
            <div className="health-meta">
              <span className="health-meta-item">
                <span className="health-meta-dot" style={{ background: 'var(--success)' }} />
                {stats.healthy_pods} Healthy
              </span>
              <span className="health-meta-item">
                <span className="health-meta-dot" style={{ background: 'var(--danger)' }} />
                {stats.failing_pods} Failing
              </span>
            </div>
          </div>
        </div>

        {/* Incident Management */}
        <div className="health-card">
          <div className="health-card-glow" style={{ background: 'radial-gradient(circle, var(--danger-glow) 0%, transparent 70%)' } as any} />
          <div className="health-card-header">
            <span className="health-card-title">Incidents</span>
            <div className="health-card-icon" style={{ color: 'var(--danger)' }}>⚠</div>
          </div>
          <div className="health-card-main">
            <div className="health-card-value" style={{ color: activeIncidents > 0 ? 'var(--danger)' : 'var(--text)' }}>
              {activeIncidents}
            </div>
            <div className="health-card-label">Active Investigations</div>
          </div>
          <div className="health-card-footer">
             <div className="btn btn-ghost btn-sm btn-full" style={{ justifyContent: 'flex-start', padding: '0', height: 'auto' }}>
               <span style={{ fontSize: '0.72rem', color: 'var(--text-dim)' }}>
                 MTTR Performance: <span style={{ color: activeIncidents > 5 ? 'var(--danger)' : 'var(--success)' }}>
                   {activeIncidents > 0 ? (activeIncidents * 4.5).toFixed(1) + 'm' : 'Optimal'}
                 </span>
               </span>
             </div>
          </div>
        </div>

        {/* Resources: CPU */}
        <div className="health-card">
          <div className="health-card-header">
            <span className="health-card-title">CPU Utilization</span>
            <div className="health-card-icon">⬡</div>
          </div>
          <div className="health-card-main">
            <div className="health-card-value">{(stats.cpu_usage || 0).toFixed(1)}%</div>
          </div>
          <div className="health-card-footer">
            <div className="gauge-container">
               <div className="gauge-track">
                  <div className="gauge-thumb" style={{ left: `${stats.cpu_usage || 0}%`, background: (stats.cpu_usage || 0) > 80 ? 'var(--danger)' : 'var(--accent)' }} />
               </div>
               <div className="health-meta">
                 <span>{stats.total_nodes} Virtual Nodes</span>
               </div>
            </div>
          </div>
        </div>

        {/* Resources: Memory */}
        <div className="health-card">
          <div className="health-card-header">
            <span className="health-card-title">Memory Allocation</span>
            <div className="health-card-icon">▦</div>
          </div>
          <div className="health-card-main">
            <div className="health-card-value">{(stats.memory_usage || 0).toFixed(1)}%</div>
          </div>
          <div className="health-card-footer">
            <div className="gauge-container">
               <div className="gauge-track">
                  <div className="gauge-thumb" style={{ left: `${stats.memory_usage || 0}%`, background: (stats.memory_usage || 0) > 85 ? 'var(--danger)' : 'var(--purple)' }} />
               </div>
               <div className="health-meta">
                 <span>{stats.total_namespaces} Namespaces | {stats.uptime || '99.9%'} Uptime</span>
               </div>
            </div>
          </div>
        </div>
      </div>

      {/* Two-column: Incidents + Activity */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 340px', gap: 20 }}>

        {/* Incidents */}
        <div>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 16 }}>
            <h2 style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--text)' }}>
              Recent Incidents
              {filtered.length > 0 && (
                <span style={{ marginLeft: 8, fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 400 }}>
                  {filtered.length} shown
                </span>
              )}
            </h2>
          </div>

          {isLoading ? (
            <div className="incidents-grid">
              {Array(4).fill(0).map((_, i) => <SkeletonCard key={i} />)}
            </div>
          ) : filtered.length === 0 ? (
            <div className="section">
              <div className="empty-state">
                <div className="empty-state-icon">✅</div>
                <div className="empty-state-title">All Systems Operational</div>
                <div className="empty-state-text">
                  No incidents detected. AutoSRE is actively monitoring your clusters.
                </div>
              </div>
            </div>
          ) : (
            <div className="incidents-grid">
              {filtered.slice(0, 6).map(inc => (
                <IncidentCard
                  key={inc.incident_id}
                  incident={inc}
                  onClick={() => onSelectIncident(inc)}
                  onExecute={() => onExecute(inc)}
                  onReview={() => onReview(inc)}
                />
              ))}
            </div>
          )}
        </div>

        {/* Activity Feed */}
        <div>
          <div style={{ marginBottom: 16 }}>
            <h2 style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--text)' }}>Activity Feed</h2>
          </div>
          <div className="section" style={{ maxHeight: 600, overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>
            <div className="section-header" style={{ padding: '12px 16px' }}>
              <span className="section-title">
                <span className="section-title-icon" style={{ '--icon-bg': 'rgba(99,102,241,0.15)', '--icon-color': 'var(--accent)' } as any}>◉</span>
                Live Events
              </span>
              <span style={{ fontSize: '0.7rem', color: 'var(--success)', display: 'flex', alignItems: 'center', gap: 4 }}>
                <span className="status-dot connected" style={{ width: 6, height: 6, margin: 0, display: 'inline-block' }} />
                Live
              </span>
            </div>
            <div className="activity-list" style={{ overflowY: 'auto', flex: 1 }}>
              {activity.map(ev => (
                <div key={ev.id} className="activity-item">
                  <div
                    className="activity-icon"
                    style={{ background: `${ACTIVITY_COLORS[ev.type]}20`, color: ACTIVITY_COLORS[ev.type] }}
                  >
                    {ACTIVITY_ICONS[ev.type]}
                  </div>
                  <div className="activity-body">
                    <div className="activity-msg">{ev.message}</div>
                    <div className="activity-time">{timeAgo(ev.timestamp)}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
