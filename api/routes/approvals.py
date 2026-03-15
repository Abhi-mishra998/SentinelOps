import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from api.schemas import ApproveRequest, ApproveResponse
from api.auth import require_role
from infrastructure.database import get_db
from models.incident import Incident
from agent.safety_guardrails import SafetyGate
from infrastructure.remediation import RemediationEngine, RemediationContext
from infrastructure.validation import ValidationEngine
import structlog

logger = structlog.get_logger(__name__)
router = APIRouter(prefix="/incident", tags=["approvals"])

safety_gate        = SafetyGate()
remediation_engine = RemediationEngine()
validation_engine  = ValidationEngine()

from models.activity import Activity

@router.post("/approve", response_model=ApproveResponse)
async def approve_action(
    req: ApproveRequest,
    user: dict = Depends(require_role("admin", "operator")),
    db: AsyncSession = Depends(get_db)
):
    """Engineer approve or reject a proposed remediation action."""
    # Fetch incident from DB
    result = await db.execute(select(Incident).where(Incident.id == req.incident_id))
    incident = result.scalar_one_or_none()
    
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    if not req.approved:
        logger.info("Action rejected by engineer", incident_id=req.incident_id, by=req.approved_by)
        incident.status = "rejected"
        
        # Log activity
        db.add(Activity(
            type="approval",
            message=f"Remediation for {incident.pod_name} rejected by {req.approved_by}",
            severity="medium",
            incident_id=req.incident_id
        ))
        
        await db.commit()
        return ApproveResponse(
            incident_id=req.incident_id,
            execution_status="rejected",
            message=f"Action '{req.action}' rejected by {req.approved_by}."
        )

    gate = safety_gate.validate(req.action)
    if not gate.approved:
        raise HTTPException(status_code=403, detail=f"Safety gate blocked: {gate.reason}")

    ctx = RemediationContext(
        pod_name=incident.pod_name,
        namespace=incident.namespace
    )

    result = await remediation_engine.execute(req.action, ctx)
    safety_gate.record_execution(req.action)

    # Log remediation attempt
    db.add(Activity(
        type="remediation",
        message=f"Executing: {req.action} on {incident.pod_name}",
        severity="high",
        incident_id=req.incident_id
    ))

    validation = await validation_engine.validate_pod_recovery(
        namespace=ctx.namespace, pod_name=ctx.pod_name
    )

    # Update incident status
    incident.status = "resolved" if validation.success else "failed"
    if validation.success:
        diff = datetime.datetime.utcnow() - incident.timestamp
        incident.resolution_time = int(diff.total_seconds())
    
    # Log validation result
    db.add(Activity(
        type="remediation",
        message=f"Remediation {'succeeded' if validation.success else 'failed'} for {incident.pod_name}",
        severity="low" if validation.success else "critical",
        incident_id=req.incident_id
    ))
    
    await db.commit()

    return ApproveResponse(
        incident_id=req.incident_id,
        execution_status="success" if result.success else "failed",
        validation_result="recovered" if validation.success else "not_recovered",
        message=result.message
    )
