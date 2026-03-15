import datetime
import uuid
import asyncio
from typing import Optional
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from api.schemas import AnalyzeRequest, AnalyzeResponse, IncidentSummary
from api.auth import get_current_user
from api.websocket import feed_manager
from infrastructure.evidence_collector import EvidenceCollector
from infrastructure.kubernetes_client import init_k8s_client
from infrastructure.database import get_db
from models.incident import Incident
from models.activity import Activity
# from agent.investigation import InvestigationService

router = APIRouter(prefix="/incident", tags=["incidents"])

@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_incident(
    req: AnalyzeRequest, 
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Trigger a full investigation for a given pod and save the result."""
    from agent.investigation import investigation_service
    incident_data = await investigation_service.investigate_and_save(
        namespace=req.namespace,
        pod_name=req.pod_name,
        cluster_id=req.cluster_id,
        db=db
    )
    return AnalyzeResponse(**incident_data)

@router.get("/history", response_model=list[IncidentSummary])
async def incident_history(
    cluster_id: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 50,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Return paginated incident history from the database."""
    query = select(Incident).order_by(Incident.timestamp.desc()).limit(limit)
    if cluster_id:
        query = query.where(Incident.cluster_id == cluster_id)
    if status:
        query = query.where(Incident.status == status)
        
    result = await db.execute(query)
    incidents = result.scalars().all()
    
    return [
        IncidentSummary(
            id=i.id,
            timestamp=i.timestamp,
            cluster_id=i.cluster_id,
            namespace=i.namespace,
            pod_name=i.pod_name,
            incident_type=i.incident_type,
            root_cause=i.root_cause,
            confidence=i.confidence,
            status=i.status,
            resolution_time=i.resolution_time,
            ai_used=i.ai_used
        ) for i in incidents
    ]

@router.get("/activity")
async def get_activity(
    limit: int = 50,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Return latest activity events."""
    result = await db.execute(select(Activity).order_by(Activity.timestamp.desc()).limit(limit))
    return result.scalars().all()

@router.get("/{incident_id}")
async def get_incident(
    incident_id: str, 
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Return full incident details by ID."""
    result = await db.execute(select(Incident).where(Incident.id == incident_id))
    incident = result.scalar_one_or_none()
    if not incident:
        return {"incident_id": incident_id, "status": "not_found"}
    return incident
