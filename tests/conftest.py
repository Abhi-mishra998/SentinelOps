"""Shared test fixtures and helpers."""
import pytest
from infrastructure.evidence_collector import Evidence

@pytest.fixture
def sample_evidence() -> Evidence:
    return Evidence(
        pod_name="api-server-7d9f-xkq2p",
        namespace="production",
        phase="Pending",
        logs="Error: cannot start application\\nExit code 1",
        events=[{"reason": "BackOff", "message": "Back-off restarting failed container", "count": 5, "type": "Warning"}],
        metrics={},
        exit_code=1,
        restart_count=5,
        image="my-api:v2.3.1",
        node_name="worker-1",
        memory_limit="512Mi",
        owner_ref="api-server"
    )

@pytest.fixture
def oom_evidence() -> Evidence:
    return Evidence(
        pod_name="memory-heavy-pod",
        namespace="default",
        phase="Failed",
        logs="Killed\\n",
        events=[{"reason": "OOMKilled", "message": "Container exceeded memory limit", "count": 1, "type": "Warning"}],
        metrics={},
        exit_code=137,
        restart_count=1,
        image="heavy-app:latest",
        node_name="worker-2",
        memory_limit="256Mi",
        owner_ref="memory-heavy-deployment"
    )
