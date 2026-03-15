import asyncio
from typing import List
from fastapi import WebSocket, WebSocketDisconnect
import structlog

logger = structlog.get_logger(__name__)

class IncidentFeedManager:
    def __init__(self):
        self.connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.connections.append(websocket)
        logger.info("WebSocket client connected", total=len(self.connections))

    def disconnect(self, websocket: WebSocket):
        if websocket in self.connections:
            self.connections.remove(websocket)
        logger.info("WebSocket client disconnected", total=len(self.connections))

    async def broadcast(self, message: dict):
        dead = []
        for ws in self.connections:
            try:
                await ws.send_json(message)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(ws)

feed_manager = IncidentFeedManager()
