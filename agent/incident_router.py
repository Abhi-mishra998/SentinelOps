from enum import Enum
import structlog
from detection.watcher import IncidentEvent

logger = structlog.get_logger(__name__)

class IncidentType(Enum):
    POD_CRASH          = 'pod_crash'
    IMAGE_PULL_ERROR   = 'image_pull_error'
    OOM_KILLED         = 'oom_killed'
    PENDING_POD        = 'pending_pod'
    DEPLOYMENT_FAILURE = 'deployment_failure'
    NODE_NOT_READY     = 'node_not_ready'
    NETWORK_TIMEOUT    = 'network_timeout'
    UNKNOWN            = 'unknown'

REASON_MAP = {
    'CrashLoopBackOff': IncidentType.POD_CRASH,
    'BackOff':          IncidentType.POD_CRASH,
    'Error':            IncidentType.POD_CRASH,
    'OOMKilled':        IncidentType.OOM_KILLED,
    'ImagePullBackOff': IncidentType.IMAGE_PULL_ERROR,
    'ErrImagePull':     IncidentType.IMAGE_PULL_ERROR,
    'FailedScheduling': IncidentType.PENDING_POD,
    'NodeNotReady':     IncidentType.NODE_NOT_READY,
}

class IncidentRouter:
    def classify(self, event: IncidentEvent) -> IncidentType:
        incident_type = REASON_MAP.get(event.reason, IncidentType.UNKNOWN)
        logger.info("Classified incident", reason=event.reason, type=incident_type.value)
        return incident_type

    def route(self, incident_type: IncidentType) -> str:
        return f"playbooks/{incident_type.value}.yaml"
