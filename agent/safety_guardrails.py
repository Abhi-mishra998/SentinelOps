from dataclasses import dataclass
from typing import Optional
import time
import structlog

logger = structlog.get_logger(__name__)

WHITELIST: dict[str, dict] = {
    "restart_pod":         {"requires_approval": True,  "max_per_hour": 10},
    "scale_deployment":    {"requires_approval": True,  "max_per_hour": 5},
    "rollback_deployment": {"requires_approval": True,  "max_per_hour": 3},
    "increase_limits":     {"requires_approval": True,  "max_per_hour": 2},
    "manual_review":       {"requires_approval": False, "max_per_hour": 999},
}

# Permanently blocked — no exceptions ever
BLOCKED: set[str] = {
    "delete_deployment",
    "delete_namespace",
    "delete_node",
    "delete_cluster"
}

@dataclass
class GateResult:
    approved:       bool
    reason:         str
    requires_human: bool = False

class SafetyGate:
    def __init__(self):
        # {action: [timestamps]}
        self._rate_window: dict[str, list[float]] = {}

    def validate(self, action: str, context: dict = None) -> GateResult:
        """Main gate — check blocked list, whitelist, and rate limits."""
        if action in BLOCKED:
            logger.warning("Safety gate: permanently blocked action attempted", action=action)
            return GateResult(approved=False, reason="PERMANENTLY_BLOCKED", requires_human=False)

        if action not in WHITELIST:
            logger.warning("Safety gate: action not in whitelist", action=action)
            return GateResult(approved=False, reason="NOT_IN_WHITELIST", requires_human=False)

        if self._rate_limit_exceeded(action):
            logger.warning("Safety gate: rate limit exceeded", action=action)
            return GateResult(approved=False, reason="RATE_LIMIT_EXCEEDED", requires_human=False)

        rules = WHITELIST[action]
        logger.info("Safety gate: action approved", action=action, requires_human=rules["requires_approval"])
        return GateResult(
            approved=True,
            reason="APPROVED",
            requires_human=rules["requires_approval"]
        )

    def record_execution(self, action: str):
        """Record an executed action for rate limiting."""
        now = time.time()
        window = self._rate_window.setdefault(action, [])
        window.append(now)

    def _rate_limit_exceeded(self, action: str) -> bool:
        now = time.time()
        one_hour_ago = now - 3600
        window = self._rate_window.get(action, [])
        # Prune old timestamps
        window = [t for t in window if t > one_hour_ago]
        self._rate_window[action] = window
        max_per_hour = WHITELIST[action]["max_per_hour"]
        return len(window) >= max_per_hour
