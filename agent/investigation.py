import datetime
import uuid
import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from agent.incident_router import IncidentRouter
from api.websocket import feed_manager
from agent.safety_guardrails import SafetyGate
from agent.playbook_engine import PlaybookEngine
from models.incident import Incident
from models.activity import Activity
from k8s_tools import SAFE_ACTIONS
from infrastructure.evidence_collector import EvidenceCollector
from agent.pattern_layer import PatternDetectionLayer
from ai.root_cause_engine import AIRootCauseEngine

logger = structlog.get_logger(__name__)

class InvestigationService:
    def __init__(self):
        # Expanded registry with investigation tools
        self.action_registry = {
            **SAFE_ACTIONS,
            "infrastructure.evidence_collector.collect_full_evidence": EvidenceCollector().collect_full_evidence,
            "agent.pattern_layer.check": PatternDetectionLayer().check,
            "ai.root_cause_engine.analyze": AIRootCauseEngine().analyze,
        }
        self.router = IncidentRouter()
        self.safety_gate = SafetyGate()
        self.playbook_engine = PlaybookEngine(self.action_registry)

    async def investigate_and_save(
        self, 
        namespace: str, 
        pod_name: str, 
        cluster_id: str = "local",
        db: AsyncSession = None,
        reason: str = "Investigation"
    ) -> dict:
        """Centralized investigation logic orchestrated by PlaybookEngine."""
        
        logger.info("Starting investigation", pod=pod_name, namespace=namespace, reason=reason)
        
        # 1. Routing (Classification)
        from detection.watcher import IncidentEvent
        event = IncidentEvent(
            event_type="Warning",
            reason=reason,
            message=f"Investigation for {pod_name} (reason: {reason})",
            pod_name=pod_name,
            namespace=namespace,
            node_name="unknown",
            timestamp=datetime.datetime.utcnow(),
            raw_event={}
        )
        incident_type = self.router.classify(event)
        
        # 2. Playbook Execution (Evidence -> Pattern -> AI)
        context = {"namespace": namespace, "pod_name": pod_name}
        playbook_result = await self.playbook_engine.run(incident_type.value, context)
        
        # Extract findings from playbook result
        # We expect steps like 'collected_evidence', 'check_pattern', 'analyze_root_cause'
        evidence = playbook_result.evidence.get("collected_evidence", {})
        pattern_match = playbook_result.evidence.get("check_pattern")
        ai_result = playbook_result.evidence.get("analyze_root_cause")
        
        root_cause = "Unknown"
        confidence = "low"
        recommended_action = "none"
        explanation = "No root cause identified"
        source = "unknown"
        ai_used = False

        if pattern_match and hasattr(pattern_match, "root_cause"):
            root_cause = pattern_match.root_cause
            confidence = pattern_match.confidence
            recommended_action = pattern_match.recommended_action
            explanation = f"Pattern match: {root_cause}"
            source = "pattern_db"
        elif ai_result and hasattr(ai_result, "root_cause"):
            root_cause = ai_result.root_cause
            confidence = ai_result.confidence
            recommended_action = ai_result.recommended_action
            explanation = ai_result.explanation
            source = "ai_engine"
            ai_used = True

        incident_id = str(uuid.uuid4())
        incident_data = {
            "incident_id": incident_id,
            "pod_name": pod_name,
            "namespace": namespace,
            "incident_type": incident_type.value,
            "root_cause": root_cause,
            "confidence": confidence,
            "recommended_action": recommended_action,
            "explanation": explanation,
            "source": source,
            "created_at": datetime.datetime.utcnow().isoformat(),
            "status": "investigated",
            "playbook_steps": {k: (str(v) if not isinstance(v, (dict, list)) else v) for k, v in playbook_result.evidence.items()}
        }

        # 3. Remediation (Safety Gate + Playbook Execution for Remediation)
        # Note: In the new flow, the playbook itself might have remediation steps, 
        # but for now we follow the existing safety gate logic.
        gate_result = self.safety_gate.validate(recommended_action, incident_data)
        incident_data["safety_gate"] = {
            "approved": gate_result.approved,
            "reason": gate_result.reason,
            "requires_human": gate_result.requires_human
        }

        if gate_result.approved and not gate_result.requires_human and recommended_action != "none":
            logger.info("Auto-executing remediation", action=recommended_action)
            # Run specific remediation action if not already done by playbook
            remediation_result = await self.playbook_engine.run_action(recommended_action, incident_data)
            incident_data["remediation_result"] = str(remediation_result)
            incident_data["status"] = "remediated"
            self.safety_gate.record_execution(recommended_action)
        elif gate_result.requires_human:
            logger.info("Remediation requires human approval", action=recommended_action)
            incident_data["status"] = "awaiting_approval"
        elif recommended_action == "none":
            incident_data["status"] = "closed_no_action"
        else:
            logger.warning("Remediation blocked by safety gate", action=recommended_action, reason=gate_result.reason)
            incident_data["status"] = "blocked"

        # 4. Persistence
        if db:
            try:
                db_incident = Incident(
                    id=incident_id,
                    cluster_id=cluster_id,
                    namespace=namespace,
                    pod_name=pod_name,
                    incident_type=incident_type.value,
                    root_cause=root_cause,
                    confidence=confidence,
                    status=incident_data["status"],
                    ai_used=ai_used,
                    recommended_action=recommended_action
                )
                db.add(db_incident)
                
                activity = Activity(
                    type="incident",
                    message=f"Incident {incident_data['status']} on {pod_name} ({namespace}): {root_cause}",
                    severity="critical" if confidence == "high" else "high",
                    incident_id=incident_id
                )
                db.add(activity)
                
                await db.commit()
                logger.info("Incident saved to DB", incident_id=incident_id)
            except Exception as e:
                logger.error("DB save failed", error=str(e))
                await db.rollback()
            
        # 5. Broadcast
        await feed_manager.broadcast(incident_data)
        
        return incident_data

# Singleton instance
investigation_service = InvestigationService()
