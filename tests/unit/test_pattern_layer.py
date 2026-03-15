"""Unit tests for Pattern Detection Layer — covers acceptance criteria #2."""
import pytest
from agent.pattern_layer import PatternDetectionLayer
from infrastructure.evidence_collector import Evidence

def make_evidence(**kwargs) -> Evidence:
    defaults = dict(
        pod_name="test-pod", namespace="default",
        phase="Running",
        logs="", events=[], metrics={},
        exit_code=None, restart_count=0,
        image="nginx:latest", node_name="node-1",
        memory_limit=None, owner_ref=None
    )
    defaults.update(kwargs)
    return Evidence(**defaults)

def test_exit_code_1_crash_pattern():
    """Criteria #2: exit_code=1 + restart_count≥3 → fast path, no LLM."""
    layer = PatternDetectionLayer()
    ev = make_evidence(exit_code=1, restart_count=5)
    match = layer.check(ev)
    assert match is not None
    assert match.recommended_action == "restart_pod"
    assert match.confidence == "high"

def test_exit_code_137_oom_pattern():
    """exit_code=137 → increase_limits fast path."""
    layer = PatternDetectionLayer()
    ev = make_evidence(exit_code=137, memory_limit="256Mi")
    match = layer.check(ev)
    assert match is not None
    assert match.recommended_action == "increase_limits"

def test_no_match_returns_none():
    """Criteria #2: No matching pattern → returns None (go to AI engine)."""
    layer = PatternDetectionLayer()
    ev = make_evidence(exit_code=0, restart_count=0)
    match = layer.check(ev)
    assert match is None
