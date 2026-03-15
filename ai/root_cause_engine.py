import json
from typing import Literal
from dataclasses import dataclass
import structlog
from config import settings
from ai.prompts import build_analysis_prompt
from infrastructure.evidence_collector import Evidence

logger = structlog.get_logger(__name__)

@dataclass
class RootCauseResult:
    root_cause:         str
    confidence:         str
    recommended_action: str
    explanation:        str
    source:             str = "ai_engine"

class AIRootCauseEngine:
    def __init__(self, backend: Literal["ollama", "openai", "anthropic"] = None):
        self.backend = backend or settings.AI_BACKEND

    async def analyze(self, evidence: Evidence) -> RootCauseResult:
        """Analyze structured evidence and return a validated root cause result."""
        prompt = build_analysis_prompt(evidence)
        logger.info("Calling LLM backend", backend=self.backend, pod=evidence.pod_name)
        
        try:
            raw = await self._call_llm(prompt)
            return self._parse_and_validate(raw)
        except Exception as e:
            logger.error("LLM call failed", error=str(e))
            return RootCauseResult(
                root_cause="LLM_CALL_FAILED",
                confidence="low",
                recommended_action="manual_review",
                explanation=f"LLM call failed: {e}"
            )

    async def _call_llm(self, prompt: str) -> str:
        if self.backend == "ollama":
            from ai.backends.ollama import call_ollama
            return await call_ollama(prompt)
        elif self.backend == "openai":
            from ai.backends.openai import call_openai
            return await call_openai(prompt)
        elif self.backend == "anthropic":
            from ai.backends.anthropic import call_anthropic
            return await call_anthropic(prompt)
        else:
            raise ValueError(f"Unknown backend: {self.backend}")

    def _parse_and_validate(self, raw: str) -> RootCauseResult:
        try:
            data = json.loads(raw.strip())
            assert "root_cause" in data, "Missing root_cause"
            assert "confidence" in data, "Missing confidence"
            assert "recommended_action" in data, "Missing recommended_action"
            assert "explanation" in data, "Missing explanation"

            return RootCauseResult(
                root_cause=str(data["root_cause"]),
                confidence=str(data["confidence"]),
                recommended_action=str(data["recommended_action"]),
                explanation=str(data["explanation"]),
            )
        except Exception as e:
            logger.warning("AI response parse error — routing to manual review", error=str(e), raw=raw[:200])
            return RootCauseResult(
                root_cause="PARSE_ERROR",
                confidence="low",
                recommended_action="manual_review",
                explanation="AI response could not be parsed — routing to manual review"
            )
