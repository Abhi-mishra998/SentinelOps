import asyncio
from kubernetes import client, watch
from dataclasses import dataclass
from datetime import datetime
import structlog

from infrastructure.kubernetes_client import get_core_v1_api

logger = structlog.get_logger(__name__)

@dataclass
class IncidentEvent:
    event_type: str
    reason: str
    message: str
    pod_name: str
    namespace: str
    node_name: str
    timestamp: datetime
    raw_event: dict

class IncidentDetectionService:
    def __init__(self, queue: asyncio.Queue):
        self.queue = queue
        self.v1 = get_core_v1_api()
        self._running = False
        self._processed_pods = {} # {pod_uid: last_event_time}

    async def start(self):
        self._running = True
        backoff = 1
        main_loop = asyncio.get_running_loop()
        while self._running:
            try:
                logger.info("Starting Kubernetes pod watch stream - SRE Agent watching cluster")
                
                # Use to_thread to run the blocking stream in a separate thread
                await asyncio.to_thread(self._watch_loop, main_loop)
                
                backoff = 1
            except Exception as exc:
                logger.error("Kubernetes event stream disconnected", error=str(exc), retry_in=backoff)
                await asyncio.sleep(backoff)
                backoff = min(backoff * 2, 60)

    def _watch_loop(self, main_loop):
        """Synchronous loop to run in a separate thread."""
        w = watch.Watch()
        for raw in w.stream(self.v1.list_pod_for_all_namespaces):
            if not self._running:
                break
                
            pod = raw['object']
            uid = pod.metadata.uid
            now = datetime.utcnow().timestamp()
            
            # Deduplication: ignore if we saw this pod in the last 5 minutes
            if uid in self._processed_pods and (now - self._processed_pods[uid]) < 300:
                continue
                
            if self._is_pod_incident(pod):
                event = self._create_incident_event(pod)
                logger.info("Kubernetes incident detected", pod_name=event.pod_name, namespace=event.namespace, reason=event.reason)
                self._processed_pods[uid] = now
                # Thread-safe put into the async queue
                main_loop.call_soon_threadsafe(self.queue.put_nowait, event)

    def stop(self):
        self._running = False

    def _is_pod_incident(self, pod) -> bool:
        """Check pod container statuses for failure states per spec."""
        FAILURE_REASONS = {
            'CrashLoopBackOff', 'ImagePullBackOff', 'ErrImagePull',
            'OOMKilled', 'ContainerCreating', 'Pending'
        }
        if not pod.status or not pod.status.container_statuses:
            return False
        for container in pod.status.container_statuses:
            if container.state and container.state.waiting:
                reason = getattr(container.state.waiting, 'reason', '')
                if reason in FAILURE_REASONS:
                    return True
            if container.state and container.state.terminated:
                reason = getattr(container.state.terminated, 'reason', '')
                if reason == 'OOMKilled':
                    return True
        return pod.status.phase in ['Pending', 'Failed']

    def _create_incident_event(self, pod) -> IncidentEvent:
        """Create IncidentEvent from failing pod."""
        # Find primary failing reason
        reason = 'Unknown'
        for container in (pod.status.container_statuses or []):
            if container.state and container.state.waiting:
                reason = getattr(container.state.waiting, 'reason', 'Unknown')
                break
            if container.state and container.state.terminated:
                reason = getattr(container.state.terminated, 'reason', 'Unknown')
                break
        return IncidentEvent(
            event_type='Warning',
            reason=reason,
            message=f'Pod {pod.metadata.name} in failure state',
            pod_name=pod.metadata.name,
            namespace=pod.metadata.namespace,
            node_name=getattr(pod.status, 'node_name', 'Unknown'),
            timestamp=datetime.utcnow(),
            raw_event={'object': pod}
        )
