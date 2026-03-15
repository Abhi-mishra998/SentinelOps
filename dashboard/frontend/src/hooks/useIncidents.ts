import { useState, useEffect, useCallback, useRef } from 'react'
import { Incident, Toast, WsStatus, ClusterStats, ActivityEvent, Playbook, Cluster } from '../types'

export const useIncidents = () => {
  const [apiUrl, setApiUrl] = useState(() => localStorage.getItem('autosre_api_url') || 'http://localhost:8080')
  const [wsUrl, setWsUrl] = useState(() => localStorage.getItem('autosre_ws_url') || 'ws://localhost:8080/ws/incidents')
  
  const [incidents, setIncidents] = useState<Incident[]>([])
  const [wsStatus, setWsStatus] = useState<WsStatus>('connecting')
  const [isLoading, setIsLoading] = useState(true)
  const [toasts, setToasts] = useState<Toast[]>([])
  const [stats, setStats] = useState<ClusterStats>({
    healthy_pods: 0,
    failing_pods: 0,
    active_incidents: 0,
    total_pods: 0,
    total_nodes: 0,
    total_namespaces: 0,
    cpu_usage: 0,
    memory_usage: 0,
    uptime: '100%'
  })
  const [activity, setActivity] = useState<ActivityEvent[]>([])
  const [playbooks, setPlaybooks] = useState<Playbook[]>([])
  const [clusters, setClusters] = useState<Cluster[]>([])
  const wsRef = useRef<WebSocket | null>(null)
  const reconnectTimeoutRef = useRef<number | null>(null)

  const addToast = useCallback((message: string, type: Toast['type'] = 'success') => {
    const id = Math.random().toString(36).slice(2)
    setToasts(prev => [...prev, { id, message, type }])
    setTimeout(() => setToasts(prev => prev.filter(t => t.id !== id)), 4000)
  }, [])

  const fetchData = useCallback(async () => {
    try {
      const authHeader = { 'Authorization': 'Bearer demo-token' }
      
      // Fetch incidents
      const incRes = await fetch(`${apiUrl}/incident/history`, { headers: authHeader })
      if (!incRes.ok) throw new Error('Failed to fetch incidents')
      const incData = await incRes.json()
      const formatted = incData.map((i: any) => ({
        incident_id: i.id,
        pod_name: i.pod_name,
        namespace: i.namespace,
        incident_type: i.incident_type,
        root_cause: i.root_cause || 'Analyzing...',
        confidence: i.confidence || 'low',
        recommended_action: i.recommended_action || 'kubectl describe pod ' + i.pod_name,
        explanation: i.explanation || 'Root cause investigation in progress.',
        source: i.ai_used ? 'AI Engine' : 'Pattern DB',
        created_at: i.timestamp,
        status: i.status === 'open' ? 'active' : (i.status as any)
      }))
      setIncidents(formatted)

      // Fetch cluster stats
      const statsRes = await fetch(`${apiUrl}/cluster/status`, { headers: authHeader })
      if (statsRes.ok) {
        const statsData = await statsRes.json()
        setStats({
          healthy_pods: statsData.healthy_pods,
          failing_pods: statsData.failing_pods,
          active_incidents: statsData.active_incidents,
          total_pods: statsData.healthy_pods + statsData.failing_pods,
          total_nodes: statsData.total_nodes,
          total_namespaces: statsData.total_namespaces,
          cpu_usage: statsData.cpu_usage_pct,
          memory_usage: statsData.memory_usage_pct,
          uptime: '99.9%'
        })
      }

      // Fetch real activity
      const activityRes = await fetch(`${apiUrl}/incident/activity`, { headers: authHeader })
      if (activityRes.ok) {
        const activityData = await activityRes.json()
        setActivity(activityData.map((a: any) => ({
          id: a.id,
          type: a.type,
          message: a.message,
          timestamp: a.timestamp,
          severity: a.severity
        })))
      }

      // Fetch playbooks
      const pbRes = await fetch(`${apiUrl}/playbooks`, { headers: authHeader })
      if (pbRes.ok) {
        const pbData = await pbRes.json()
        setPlaybooks(pbData.map((p: any) => p.details || {
          name: p.name,
          description: 'No description available',
          trigger: 'manual',
          steps: []
        }))
      }

      // Fetch clusters
      const clRes = await fetch(`${apiUrl}/cluster/status`, { headers: authHeader })
      if (clRes.ok) {
        const clData = await clRes.json()
        setClusters([{
          id: clData.cluster_id,
          name: 'Local Cluster',
          region: 'internal',
          status: clData.failing_pods > 0 ? 'degraded' : 'healthy',
          node_count: clData.total_nodes,
          pod_count: clData.healthy_pods + clData.failing_pods
        }])
      }

      setIsLoading(false)
    } catch (err) {
      console.error('Failed to fetch data:', err)
      setIsLoading(false)
    }
  }, [apiUrl])

  useEffect(() => {
    // Listen for storage changes (settings updates)
    const handleStorage = () => {
      setApiUrl(localStorage.getItem('autosre_api_url') || 'http://localhost:8080')
      setWsUrl(localStorage.getItem('autosre_ws_url') || 'ws://localhost:8080/ws/incidents')
    }
    window.addEventListener('storage', handleStorage)
    
    fetchData()

    let retryCount = 0
    const connectWS = () => {
      if (wsRef.current) wsRef.current.close()
      
      const ws = new WebSocket(wsUrl)
      wsRef.current = ws

      ws.onopen = () => {
        setWsStatus('connected')
        retryCount = 0
      }
      ws.onclose = () => {
        setWsStatus('disconnected')
        const delay = Math.min(1000 * Math.pow(2, retryCount), 10000)
        reconnectTimeoutRef.current = window.setTimeout(() => {
          retryCount++
          connectWS()
        }, delay)
      }
      ws.onerror = () => setWsStatus('disconnected')
      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          if (data.type === 'ping') return
          
          if (data.incident_id) {
            const mapped: Incident = {
              incident_id: data.incident_id,
              pod_name: data.pod_name,
              namespace: data.namespace,
              incident_type: data.incident_type,
              root_cause: data.root_cause,
              confidence: data.confidence,
              recommended_action: data.recommended_action,
              explanation: data.explanation,
              source: data.source,
              created_at: data.created_at,
              status: 'active'
            }
            setIncidents(prev => {
              if (prev.find(i => i.incident_id === mapped.incident_id)) return prev
              return [mapped, ...prev]
            })
            addToast(`New incident detected: ${data.pod_name}`, 'warning')
            // Update stats
            setStats(prev => ({ ...prev, active_incidents: prev.active_incidents + 1, failing_pods: prev.failing_pods + 1 }))
            
            // Add to activity feed
            setActivity(prev => [{
               id: Math.random().toString(),
               type: 'incident',
               message: `Incident detected: ${data.pod_name} (${data.incident_type})`,
               timestamp: new Date().toISOString(),
               severity: 'high'
            }, ...prev])
          }
        } catch { /* ignore */ }
      }
    }

    connectWS()
    return () => {
      window.removeEventListener('storage', handleStorage)
      if (reconnectTimeoutRef.current) window.clearTimeout(reconnectTimeoutRef.current)
      wsRef.current?.close()
    }
  }, [fetchData, addToast, wsUrl])

  const removeToast = useCallback((id: string) => {
    setToasts(prev => prev.filter(t => t.id !== id))
  }, [])

  const handleAction = useCallback(async (incident: Incident, approved: boolean) => {
    try {
      const res = await fetch(`${apiUrl}/incident/approve`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': 'Bearer demo-token' },
        body: JSON.stringify({
          incident_id: incident.incident_id,
          action: incident.recommended_action,
          approved: approved,
          approved_by: 'dashboard-user'
        })
      })

      if (res.ok) {
        if (approved) {
          addToast(`✅ Auto-fix executed for ${incident.pod_name}`, 'success')
          setIncidents(prev => prev.map(i => 
            i.incident_id === incident.incident_id ? { ...i, status: 'resolved' } : i
          ))
          setStats(prev => ({ ...prev, active_incidents: Math.max(0, prev.active_incidents - 1) }))
        } else {
          addToast(`⏸ Internal review requested: ${incident.pod_name}`, 'info')
          setIncidents(prev => prev.map(i =>
            i.incident_id === incident.incident_id ? { ...i, status: 'pending' } : i
          ))
        }
      } else {
        const error = await res.json()
        addToast(`❌ Action failed: ${error.detail || 'Server error'}`, 'error')
      }
    } catch (err) {
      addToast(`❌ Network error connecting to backend`, 'error')
    }
  }, [apiUrl, addToast])

  const dismissIncident = useCallback((incidentId: string) => {
    setIncidents(prev => prev.filter(i => i.incident_id !== incidentId))
    addToast('Incident view dismissed', 'info')
  }, [addToast])

  const executePlaybook = useCallback(async (name: string, namespace: string, podName: string) => {
    try {
      const res = await fetch(`${apiUrl}/playbooks/${name}/execute?namespace=${namespace}&pod_name=${podName}`, {
        method: 'POST',
        headers: { 'Authorization': 'Bearer demo-token' }
      })
      if (res.ok) {
        addToast(`Successfully triggered playbook: ${name}`, 'success')
      } else {
        addToast(`Failed to trigger playbook: ${name}`, 'error')
      }
    } catch (err) {
      addToast(`Network error triggering playbook`, 'error')
    }
  }, [apiUrl, addToast])

  return {
    incidents,
    wsStatus,
    isLoading,
    toasts,
    stats,
    activity,
    playbooks,
    clusters,
    activeIncidents: incidents.filter(i => i.status === 'active').length,
    handleAction,
    addToast,
    removeToast,
    dismissIncident,
    executePlaybook
  }
}
