"""Unit tests for AI Root Cause Engine — covers acceptance criteria #4."""
import pytest
from ai.root_cause_engine import AIRootCauseEngine
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_valid_json_returns_result():
    """Criteria #4: Valid JSON from LLM -> parsed correctly."""
    engine = AIRootCauseEngine(backend="ollama")
    valid_response = '''{
        "root_cause": "Container OOM killed",
        "confidence": "high",
        "recommended_action": "increase_limits",
        "explanation": "The container exceeded its memory limit."
    }'''
    with patch.object(engine, "_call_llm", new=AsyncMock(return_value=valid_response)):
        from infrastructure.evidence_collector import Evidence
        ev = Evidence(
            pod_name="test", 
            namespace="default",
            phase="Failed",
            logs="", 
            events=[], 
            metrics={},
            exit_code=137, 
            restart_count=2,
            image="myapp:v1", 
            node_name="node-1",
            memory_limit="256Mi", 
            owner_ref=None
        )
        result = await engine.analyze(ev)
        assert result.root_cause == "Container OOM killed"
        assert result.confidence == "high"
        assert result.recommended_action == "increase_limits"

@pytest.mark.asyncio
async def test_invalid_json_returns_manual_review():
    """Criteria #4: Garbage from LLM -> PARSE_ERROR + manual_review, no crash."""
    engine = AIRootCauseEngine(backend="ollama")
    with patch.object(engine, "_call_llm", new=AsyncMock(return_value="this is not json at all !!!")):
        from infrastructure.evidence_collector import Evidence
        ev = Evidence(
            pod_name="test", 
            namespace="default",
            phase="Running",
            logs="", 
            events=[], 
            metrics={},
            exit_code=None, 
            restart_count=0,
            image="myapp:v1", 
            node_name="node-1",
            memory_limit=None, 
            owner_ref=None
        )
        result = await engine.analyze(ev)
        assert result.root_cause == "PARSE_ERROR"
        assert result.recommended_action == "manual_review"
        assert result.confidence == "low"

@pytest.mark.asyncio
async def test_llm_failure_returns_manual_review():
    """LLM call failure -> returns manual_review gracefully."""
    engine = AIRootCauseEngine(backend="ollama")
    with patch.object(engine, "_call_llm", new=AsyncMock(side_effect=RuntimeError("connection refused"))):
        from infrastructure.evidence_collector import Evidence
        ev = Evidence(
            pod_name="test", 
            namespace="default",
            phase="Running",
            logs="", 
            events=[], 
            metrics={},
            exit_code=None, 
            restart_count=0,
            image="myapp:v1", 
            node_name="node-1",
            memory_limit=None, 
            owner_ref=None
        )
        result = await engine.analyze(ev)
        assert result.recommended_action == "manual_review"
