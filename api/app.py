from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from api.routes import incidents, approvals, clusters, playbooks
from api.auth import create_access_token
from api.schemas import TokenRequest, TokenResponse
from api.websocket import feed_manager
from infrastructure.kubernetes_client import init_k8s_client
import structlog
import asyncio

logger = structlog.get_logger(__name__)

def create_app() -> FastAPI:
    app = FastAPI(
        title="Autonomous SRE Agent API",
        description="AI-powered Kubernetes incident detection and remediation platform.",
        version="2.0.0"
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(incidents.router)
    app.include_router(approvals.router)
    app.include_router(clusters.router)
    app.include_router(playbooks.router)

    @app.post("/auth/token", response_model=TokenResponse)
    async def login(form_data: TokenRequest):
        access_token = create_access_token(form_data.username, form_data.role)
        return TokenResponse(access_token=access_token)

    @app.websocket("/ws/incidents")
    async def incident_websocket(websocket: WebSocket):
        await feed_manager.connect(websocket)
        try:
            while True:
                await asyncio.sleep(30)
                await websocket.send_json({"type": "ping"})
        except (WebSocketDisconnect, Exception):
            feed_manager.disconnect(websocket)

    @app.get("/health")
    async def health():
        return {"status": "ok"}

    return app

app = create_app()
