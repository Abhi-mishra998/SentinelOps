from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class AnalyzeRequest(BaseModel):
    cluster_id: str
    namespace: str
    pod_name: str

class AnalyzeResponse(BaseModel):
    incident_id: str
    pod_name: str
    namespace: str
    incident_type: str
    root_cause: str
    confidence: str
    recommended_action: str
    explanation: str
    source: str
    created_at: datetime

class ApproveRequest(BaseModel):
    incident_id: str
    action: str
    approved_by: str
    approved: bool = True

class ApproveResponse(BaseModel):
    incident_id: str
    execution_status: str
    validation_result: Optional[str] = None
    message: str

class IncidentSummary(BaseModel):
    id: str
    timestamp: datetime
    cluster_id: str
    namespace: str
    pod_name: str
    incident_type: str
    root_cause: Optional[str]
    confidence: Optional[str]
    status: str
    resolution_time: Optional[int]
    ai_used: bool

class ClusterStatusResponse(BaseModel):
    cluster_id: str
    healthy_pods: int
    failing_pods: int
    active_incidents: int
    total_nodes: int = 1
    total_namespaces: int = 1
    cpu_usage_pct: float = 0.0
    memory_usage_pct: float = 0.0

class PlaybookDetails(BaseModel):
    name: str
    description: str
    trigger: str
    steps: List[str]

class PlaybookResponse(BaseModel):
    name: str
    content: str
    details: Optional[PlaybookDetails] = None

class TokenRequest(BaseModel):
    username: str
    role: str = "viewer"

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 3600
