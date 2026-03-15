import { WsStatus } from '../types'

interface TopbarProps {
  searchTerm: string
  onSearchChange: (v: string) => void
  activeIncidents: number
  wsStatus: WsStatus
  onOpenSidebar: () => void
}

export const Topbar = ({
  searchTerm,
  onSearchChange,
  activeIncidents,
  wsStatus,
  onOpenSidebar,
}: TopbarProps) => {
  return (
    <header className="topbar">
      {/* Mobile hamburger */}
      <button
        className="topbar-hamburger"
        onClick={onOpenSidebar}
        aria-label="Open menu"
      >
        ☰
      </button>

      {/* Mobile brand */}
      <div className="topbar-brand-mobile">AutoSRE</div>

      {/* Search */}
      <div className="topbar-search">
        <span className="topbar-search-icon">🔍</span>
        <input
          id="global-search"
          className="search-input"
          type="text"
          placeholder="Search pods, namespaces, incidents…"
          value={searchTerm}
          onChange={e => onSearchChange(e.target.value)}
          autoComplete="off"
        />
      </div>

      {/* Actions */}
      <div className="topbar-actions">
        {/* WS badge */}
        <div className="topbar-badge" style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          <div
            className="status-dot"
            style={{
              width: 7,
              height: 7,
              borderRadius: '50%',
              background:
                wsStatus === 'connected' ? 'var(--success)' :
                wsStatus === 'connecting' ? 'var(--warning)' : 'var(--danger)',
              boxShadow: wsStatus === 'connected' ? '0 0 6px var(--success)' : 'none',
              animation: wsStatus !== 'disconnected' ? 'pulse-dot 2s infinite' : 'none',
            }}
          />
          <span style={{ fontSize: '0.78rem', color: 'var(--text-dim)' }}>
            {wsStatus === 'connected' ? 'Live' : wsStatus === 'connecting' ? 'Connecting…' : 'Offline'}
          </span>
        </div>

        {/* Notifications */}
        <button className="topbar-icon-btn" aria-label="Notifications" title="Notifications">
          🔔
          {activeIncidents > 0 && (
            <span className="notification-badge">{activeIncidents > 9 ? '9+' : activeIncidents}</span>
          )}
        </button>

        {/* Docs */}
        <button className="topbar-icon-btn" aria-label="Documentation" title="Documentation">
          📖
        </button>

        {/* Avatar */}
        <div className="topbar-avatar" title="SRE Admin">
          SR
        </div>
      </div>
    </header>
  )
}
