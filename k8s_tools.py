import structlog
from kubernetes import client
from infrastructure.kubernetes_client import get_core_v1_api, get_apps_v1_api

logger = structlog.get_logger(__name__)


def get_pod_status(pod_name, namespace='default'):
    """Get pod status summary."""
    v1 = get_core_v1_api()
    try:
        pod = v1.read_namespaced_pod(pod_name, namespace)
        status = f"Phase: {pod.status.phase}, IP: {getattr(pod.status, 'pod_ip', 'None')}, Node: {getattr(pod.spec, 'node_name', 'None')}"
        return status
    except Exception as e:
        logger.error("Failed to get pod status", pod=pod_name, error=str(e))
        return f"ERROR: {str(e)}"

def get_pod_logs(pod_name, namespace='default', tail_lines=100):
    """Get recent pod logs."""
    v1 = get_core_v1_api()
    try:
        logs = v1.read_namespaced_pod_log(name=pod_name, namespace=namespace, tail_lines=tail_lines, timestamps=True)
        return logs
    except Exception as e:
        logger.error("Failed to get logs", pod=pod_name, error=str(e))
        return f"ERROR getting logs: {str(e)}"

def list_unhealthy_pods_all_namespaces():
    """List unhealthy pods across all namespaces."""
    v1 = get_core_v1_api()
    try:
        pods = v1.list_pod_for_all_namespaces()
        unhealthy = []
        for pod in pods.items:
            reason = None
            phase = getattr(pod.status, 'phase', '')
            if phase in ('Failed', 'Pending', 'Unknown'):
                reason = phase
            else:
                for cs in (pod.status.container_statuses or []):
                    if getattr(cs.state, 'waiting', None) and getattr(cs.state.waiting, 'reason', None):
                        reason = cs.state.waiting.reason
                        break
                    if getattr(cs.state, 'terminated', None) and getattr(cs.state.terminated, 'reason', None):
                        reason = cs.state.terminated.reason
                        break
            if reason:
                unhealthy.append({
                    'name': pod.metadata.name, 
                    'namespace': pod.metadata.namespace, 
                    'reason': reason
                })
        return unhealthy
    except Exception as e:
        logger.error("Failed to list unhealthy pods", error=str(e))
        return []

def restart_pod(pod_name, namespace='default'):
    """Restart pod by delete (safe for managed)."""
    v1 = get_core_v1_api()
    try:
        pod = v1.read_namespaced_pod(pod_name, namespace)
        is_managed = pod.metadata.owner_references and any(ref.kind in ['ReplicaSet', 'StatefulSet', 'DaemonSet'] for ref in pod.metadata.owner_references)
        
        if is_managed:
            v1.delete_namespaced_pod(name=pod_name, namespace=namespace)
            return f"Safe restart of managed pod {pod_name}"
        else:
            return f"SAFETY: Manual pod {pod_name} - requires approval (not managed)"
    except Exception as e:
        return f"Restart failed: {str(e)}"

def delete_pod(namespace, pod_name):
    """Delete pod."""
    v1 = get_core_v1_api()
    try:
        v1.delete_namespaced_pod(name=pod_name, namespace=namespace)
        return f"Pod {pod_name} deleted successfully"
    except Exception as e:
        return f"Delete failed: {str(e)}"

def validate_pod(namespace, pod_name):
    """Validate pod recovery."""
    v1 = get_core_v1_api()
    try:
        pod = v1.read_namespaced_pod(pod_name, namespace)
        if pod.status.phase == 'Running' and all(cs.ready for cs in (pod.status.container_statuses or [])):
            return "SUCCESS: Pod healthy"
        else:
            return f"FAILED: {pod.status.phase}"
    except Exception as e:
        return f"FAILED: {str(e)}"

def scale_deployment(namespace, deployment_name, replicas):
    """Scale deployment."""
    apps_v1 = get_apps_v1_api()
    try:
        body = {"spec": {"replicas": int(replicas)}}
        apps_v1.patch_namespaced_deployment(name=deployment_name, namespace=namespace, body=body)
        return f"Scaled {deployment_name} to {replicas}"
    except Exception as e:
        logger.error("Scale failed", deployment=deployment_name, error=str(e))
        return f"Scale failed: {e}"

SAFE_ACTIONS = {
    'restart_pod': restart_pod,
    'scale_deployment': scale_deployment,
    'delete_pod': delete_pod,
    'validate_pod': validate_pod
}

def execute_remediation(action, params):
    """Dispatch to safe action."""
    if action in SAFE_ACTIONS:
        return SAFE_ACTIONS[action](**params)
    return f"Unknown action: {action}"
