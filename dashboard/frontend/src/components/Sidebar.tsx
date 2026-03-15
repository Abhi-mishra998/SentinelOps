import { Page, WsStatus } from '../types'

interface SidebarProps {
  page: Page
  isOpen: boolean
  onPageChange: (page: Page) => void
  onClose: () => void
  wsStatus: WsStatus
  activeIncidents: number
}

const NAV_ITEMS = [
  { id: 'dashboard' as Page, icon: '⬡', label: 'Dashboard' },
  { id: 'incidents' as Page, icon: '⚠', label: 'Incidents', hasBadge: true },
  { id: 'activity' as Page, icon: '◉', label: 'Activity Feed' },
  { id: 'playbooks' as Page, icon: '▶', label: 'Playbooks' },
  { id: 'clusters' as Page, icon: '◈', label: 'Clusters' },
  { id: 'settings' as Page, icon: '◎', label: 'Settings' },
]

export const Sidebar = ({
  page,
  isOpen,
  onPageChange,
  onClose,
  wsStatus,
  activeIncidents
}: SidebarProps) => {
  return (
    <>
      {/* Overlay */}
      <div
        className={`sidebar-overlay ${isOpen ? 'open' : ''}`}
        onClick={onClose}
        aria-hidden="true"
      />

      <aside className={`sidebar ${isOpen ? 'open' : ''}`}>
        {/* Header */}
        <div className="sidebar-header">
          <div className="sidebar-brand">
            <div className="sidebar-brand-icon">⚡</div>
            <div>
              <div className="sidebar-brand-name">AutoSRE</div>
            </div>
            <span className="sidebar-brand-version">v2.0</span>
            <button className="sidebar-close-btn" onClick={onClose} aria-label="Close sidebar">
              ✕
            </button>
          </div>
        </div>

        {/* Navigation */}
        <nav className="sidebar-nav">
          <div className="nav-section-label">Navigation</div>
          {NAV_ITEMS.map(item => (
            <button
              key={item.id}
              className={`nav-item ${page === item.id ? 'active' : ''}`}
              onClick={() => { onPageChange(item.id); onClose(); }}
              aria-current={page === item.id ? 'page' : undefined}
            >
              <span className="nav-item-icon">{item.icon}</span>
              <span className="nav-item-label">{item.label}</span>
              {item.hasBadge && activeIncidents > 0 && (
                <span className="nav-item-badge">{activeIncidents}</span>
              )}
            </button>
          ))}
        </nav>

        {/* Footer */}
        <div className="sidebar-footer">
          <div className="sidebar-status">
            <div className={`status-dot ${wsStatus}`} />
            <div className="status-text">
              <strong>
                {wsStatus === 'connected' ? 'Live' : wsStatus === 'connecting' ? 'Connecting' : 'Offline'}
              </strong>
              <span style={{ marginLeft: 4, color: 'var(--text-muted)', fontSize: '0.75rem' }}>
                {wsStatus === 'connected' ? '• WebSocket' : '• Retrying'}
              </span>
            </div>
          </div>
        </div>
      </aside>
    </>
  )
}
