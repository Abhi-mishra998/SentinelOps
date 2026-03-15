from kubernetes import client
from dataclasses import dataclass
from typing import Optional
import asyncio
import structlog

from infrastructure.kubernetes_client import (
    get_core_v1_api, 
    get_apps_v1_api
)

logger = structlog.get_logger(__name__)

@dataclass
class Evidence:
    pod_name:      str
    namespace:     str
    phase:         str
    logs:          str
    events:        list[dict]
    metrics:       dict
    exit_code:     Optional[int]
    restart_count: int
    image:         str
    node_name:     str
    memory_limit:  Optional[str]
    owner_ref:     Optional[str]

class EvidenceCollector:
    def __init__(self):
        self.v1   = get_core_v1_api()
        self.apps = get_apps_v1_api()
        # For custom objects, we'll just use the default client for now as we don't have a helper
        self.custom = client.CustomObjectsApi()

    async def collect_full_evidence(self, namespace: str, pod_name: str) -> Evidence:
        """Collect all evidence in parallel for maximum speed."""
        logger.info("Starting parallel evidence collection", namespace=namespace, pod_name=pod_name)
        
        pod_task, logs_task, events_task, metrics_task = await asyncio.gather(
            asyncio.wait_for(self.get_pod_spec(pod_name, namespace), timeout=30.0),
            asyncio.wait_for(self.get_pod_logs(pod_name, namespace), timeout=30.0),
            asyncio.wait_for(self.get_pod_events(pod_name, namespace), timeout=10.0),
            asyncio.wait_for(self.get_resource_metrics(pod_name, namespace), timeout=10.0),
            return_exceptions=True
        )

        pod = pod_task if not isinstance(pod_task, Exception) else None
        phase = getattr(pod, 'status', {}).phase if pod else 'Unknown'
        container_status = self._extract_container_status(pod_task)

        return Evidence(
            pod_name      = pod_name,
            namespace     = namespace,
            phase         = phase,
            logs          = logs_task if not isinstance(logs_task, Exception) else "",
            events        = events_task if not isinstance(events_task, Exception) else [],
            metrics       = metrics_task if not isinstance(metrics_task, Exception) else {},
            exit_code     = container_status.get("exit_code"),
            restart_count = container_status.get("restart_count", 0),
            image         = container_status.get("image", ""),
            node_name     = getattr(pod.status, 'node_name', 'Unknown') if pod else 'Unknown',
            memory_limit  = self._get_memory_limit(pod_task),
            owner_ref     = self._get_owner(pod_task),
        )

    async def get_pod_spec(self, pod_name: str, namespace: str):
        return await asyncio.to_thread(self.v1.read_namespaced_pod, pod_name, namespace)

    async def get_pod_logs(self, pod_name: str, namespace: str, tail_lines: int = 100) -> str:
        return await asyncio.to_thread(
            self.v1.read_namespaced_pod_log,
            name=pod_name,
            namespace=namespace,
            tail_lines=tail_lines,
            timestamps=True
        )

    async def get_pod_events(self, pod_name: str, namespace: str) -> list:
        field_selector = f"involvedObject.name={pod_name}"
        events = await asyncio.to_thread(
            self.v1.list_namespaced_event,
            namespace=namespace,
            field_selector=field_selector
        )
        return [{"reason": e.reason, "message": e.message, "count": getattr(e, "count", 1), "type": e.type} for e in events.items]

    async def get_resource_metrics(self, pod_name: str, namespace: str) -> dict:
        try:
            metrics = await asyncio.to_thread(
                self.custom.get_namespaced_custom_object,
                group="metrics.k8s.io",
                version="v1beta1",
                namespace=namespace,
                plural="pods",
                name=pod_name
            )
            return metrics
        except Exception as e:
            logger.debug("Metrics server might be unavailable", error=str(e))
            return {}

    def _extract_container_status(self, pod) -> dict:
        if isinstance(pod, Exception) or not pod:
            return {}
        statuses = pod.status.container_statuses
        if not statuses:
            return {}
        # Pick the first failing container
        for st in statuses:
            if not st.ready:
                state = st.state.terminated or st.state.waiting
                return {
                    "exit_code": getattr(state, "exit_code", None),
                    "restart_count": st.restart_count,
                    "image": st.image
                }
        return {"restart_count": statuses[0].restart_count, "image": statuses[0].image, "exit_code": None}

    def _get_memory_limit(self, pod) -> Optional[str]:
        if isinstance(pod, Exception) or not pod:
            return None
        containers = pod.spec.containers
        if containers and containers[0].resources and containers[0].resources.limits:
            return containers[0].resources.limits.get("memory")
        return None

    def _get_owner(self, pod) -> Optional[str]:
        if isinstance(pod, Exception) or not pod:
            return None
        owners = pod.metadata.owner_references
        if owners:
            return owners[0].name
        return None
