import asyncio
import structlog
import uvicorn

from api.app import app
from infrastructure.kubernetes_client import init_k8s_client
from detection.watcher import IncidentDetectionService, IncidentEvent
from agent.incident_router import IncidentRouter
# from agent.pattern_layer import PatternDetectionLayer
from infrastructure.evidence_collector import EvidenceCollector
# from ai.root_cause_engine import AIRootCauseEngine
from notifications.slack import SlackNotifier
# from agent.investigation import InvestigationService
from infrastructure.database import SessionLocal

logger = structlog.get_logger()


async def process_incident(event: IncidentEvent):
    """Full incident investigation pipeline using shared investigation_service"""
    from agent.investigation import investigation_service
    from config import settings
    async with SessionLocal() as db:
        incident_data = await investigation_service.investigate_and_save(
            namespace=event.namespace,
            pod_name=event.pod_name,
            cluster_id=settings.CLUSTER_ID,
            db=db,
            reason=event.reason
        )

    logger.info("Incident processed", **incident_data)

    notifier = SlackNotifier()
    await notifier.send_incident_alert(incident_data)


async def incident_loop():
    """Watch Kubernetes events continuously"""

    queue: asyncio.Queue[IncidentEvent] = asyncio.Queue(maxsize=100)

    detector = IncidentDetectionService(queue)

    asyncio.create_task(detector.start())

    logger.info("SRE Agent watching cluster")

    semaphore = asyncio.Semaphore(5)  # Worker pool: max 5 concurrent incidents

    while True:
        event = await queue.get()

        logger.info(
            "Processing incident",
            pod=event.pod_name,
            namespace=event.namespace
        )

        async def limited_process():
            async with semaphore:
                await process_incident(event)

        asyncio.create_task(limited_process())


async def start_api():
    config = uvicorn.Config(
        app,
        host="0.0.0.0",
        port=8080,
        log_level="info"
    )

    server = uvicorn.Server(config)
    await server.serve()


async def main():

    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer()
        ]
    )

    logger.info("Starting Kubernetes SRE Agent")

    init_k8s_client()

    await asyncio.gather(
        incident_loop(),
        start_api()
    )


if __name__ == "__main__":
    asyncio.run(main())