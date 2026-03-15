import json
from dataclasses import dataclass
from typing import Optional
from infrastructure.evidence_collector import Evidence
from config import settings
import structlog

logger = structlog.get_logger(__name__)

@dataclass
class PatternMatch:
    root_cause:         str
    recommended_action: str
    confidence:         str
    source:             str = "pattern_db"

class PatternDetectionLayer:
    def __init__(self):
        try:
            with open(settings.PATTERNS_PATH) as f:
                self.patterns = json.load(f).get("patterns", [])
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.warning("Failed to load pattern database", error=str(e))
            self.patterns = []

    def check(self, evidence: Evidence) -> Optional[PatternMatch]:
        """Check known patterns before calling LLM. Returns None if no match."""
        for pattern in self.patterns:
            if self._matches(pattern["conditions"], evidence):
                logger.info("Pattern match found", root_cause=pattern["root_cause"])
                return PatternMatch(
                    root_cause=pattern["root_cause"],
                    recommended_action=pattern["recommended_action"],
                    confidence=pattern["confidence"],
                )
        return None  # Fall through to AI engine

    def _matches(self, conditions: dict, evidence: Evidence) -> bool:
        for key, expected_value in conditions.items():
            if key == "exit_code" and evidence.exit_code != expected_value:
                return False
            elif key == "restart_count_gte" and (evidence.restart_count or 0) < expected_value:
                return False
            elif key == "memory_limit_set" and (evidence.memory_limit is not None) != expected_value:
                return False
            elif key == "log_contains" and expected_value not in evidence.logs:
                return False
        return True
