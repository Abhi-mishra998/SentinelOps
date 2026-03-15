import yaml
import asyncio
from pathlib import Path
from dataclasses import dataclass
import structlog
from typing import Any
from config import settings

logger = structlog.get_logger(__name__)

@dataclass
class PlaybookResult:
    evidence: dict
    fast_path: bool = False

class PlaybookEngine:
    def __init__(self, action_registry: dict):
        self.playbooks_dir = Path(settings.PLAYBOOKS_PATH)
        self._action_registry = action_registry

    def _load(self, incident_type: str) -> dict:
        path = self.playbooks_dir / f"{incident_type}.yaml"
        if not path.exists():
            path = self.playbooks_dir / "unknown.yaml"
        with open(path) as f:
            return yaml.safe_load(f)

    async def run(self, incident_type: str, context: dict) -> PlaybookResult:
        logger.info("Starting playbook evaluation", incident_type=incident_type)
        playbook = self._load(incident_type)
        collected = {}

        for step in playbook.get("steps", []):
            try:
                result = await self._execute_step(step, context, collected)
                collected[step["id"]] = result

                if isinstance(result, dict) and result.get("early_return") or (hasattr(result, "source") and result.source == "pattern_db"):
                    logger.info("Fast path triggered, exiting playbook early", step=step["id"])
                    return PlaybookResult(evidence=collected, fast_path=True)
            except Exception as e:
                logger.error("Playbook step failed", step=step["id"], error=str(e))
                collected[step["id"]] = {"error": str(e)}

        return PlaybookResult(evidence=collected, fast_path=False)

    async def _execute_step(self, step: dict, ctx: dict, collected: dict) -> Any:
        action_name = step["action"]
        if action_name not in self._action_registry:
            raise ValueError(f"Action '{action_name}' not found in registry")
            
        action_fn = self._action_registry[action_name]
        resolved_args = self._resolve_args(step.get("args", {}), ctx, collected)
        
        logger.debug("Executing step", step=step["id"], action=action_name)
        
        if asyncio.iscoroutinefunction(action_fn):
            return await action_fn(**resolved_args)
        else:
            return action_fn(**resolved_args)

    async def execute_manual(self, playbook_name: str, namespace: str, pod_name: str) -> dict:
        """Manually trigger a specific playbook."""
        logger.info("Executing manual playbook", playbook=playbook_name, pod=pod_name)
        # For manual execution, we skip the automated run logic and call the specific function if it exists
        # or load the yaml and run it.
        context = {"namespace": namespace, "pod_name": pod_name}
        return await self.run(playbook_name, context)

    async def run_action(self, action_name: str, context: dict) -> Any:
        """Execute a single action directly from the registry."""
        if action_name not in self._action_registry:
            logger.warning("Action not found in registry", action=action_name)
            return f"Action {action_name} not available"
            
        action_fn = self._action_registry[action_name]
        # Resolve common args from context
        args = {k: v for k, v in context.items() if k in ["namespace", "pod_name", "pod"]}
        
        logger.info("Executing direct action", action=action_name)
        if asyncio.iscoroutinefunction(action_fn):
            return await action_fn(**args)
        else:
            return action_fn(**args)

    def _resolve_args(self, args: dict, ctx: dict, collected: dict) -> dict:
        resolved = {}
        for k, v in args.items():
            if isinstance(v, str) and v.startswith("{{") and v.endswith("}}"):
                var_name = v.strip("{}").strip()
                if var_name in ctx:
                    resolved[k] = ctx[var_name]
                elif var_name in collected:
                    resolved[k] = collected[var_name]
                elif var_name == "collected_evidence":
                    resolved[k] = collected
                else:
                    resolved[k] = None
            else:
                resolved[k] = v
        return resolved
