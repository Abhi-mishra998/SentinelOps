export interface Incident {
  incident_id: string
  pod_name: string
  namespace: string
  incident_type: string
  root_cause: string
  confidence: 'high' | 'medium' | 'low' | string
  recommended_action: string
  explanation?: string
  source: string
  created_at: string
  status?: 'active' | 'resolved' | 'pending'
}

export interface ClusterStats {
  healthy_pods: number
  failing_pods: number
  active_incidents: number
  total_pods: number
  total_nodes: number
  total_namespaces: number
  cpu_usage?: number
  memory_usage?: number
  uptime?: string
}

export interface Cluster {
  id: string
  name: string
  region: string
  status: 'healthy' | 'degraded' | 'critical'
  node_count: number
  pod_count: number
}

export interface Playbook {
  name: string
  description: string
  trigger: string
  steps: string[]
}

export type WsStatus = 'connected' | 'disconnected' | 'connecting'

export type Page = 'dashboard' | 'incidents' | 'playbooks' | 'clusters' | 'settings' | 'activity'

export interface Toast {
  id: string
  message: string
  type: 'success' | 'error' | 'warning' | 'info'
}

export interface ActivityEvent {
  id: string
  type: 'incident' | 'remediation' | 'approval' | 'alert'
  message: string
  timestamp: string
  severity: 'critical' | 'high' | 'medium' | 'low'
}
