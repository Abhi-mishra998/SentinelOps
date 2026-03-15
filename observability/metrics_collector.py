from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi import APIRouter
from fastapi.responses import Response

router = APIRouter(tags=["observability"])

# Counters
incidents_detected_total = Counter(
    "sre_incidents_detected_total",
    "Total incidents detected",
    ["cluster_id", "incident_type"]
)
incidents_resolved_total = Counter(
    "sre_incidents_resolved_total",
    "Total incidents resolved",
    ["cluster_id", "incident_type", "action"]
)
remediation_actions_total = Counter(
    "sre_remediation_actions_total",
    "Total remediation actions attempted",
    ["action", "result"]
)
safety_gate_blocked_total = Counter(
    "sre_safety_gate_blocked_total",
    "Total actions blocked by safety gate",
    ["action", "reason"]
)

# Histograms
mttr_seconds = Histogram(
    "sre_mttr_seconds",
    "Mean time to recovery in seconds",
    ["cluster_id", "incident_type"],
    buckets=[5, 10, 30, 60, 120, 300, 600]
)
ai_response_latency = Histogram(
    "sre_ai_response_latency_seconds",
    "AI root cause analysis latency",
    ["backend"]
)

# Gauges
active_incidents = Gauge(
    "sre_active_incidents",
    "Currently open incidents",
    ["cluster_id"]
)

@router.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
