import httpx
import json
import structlog
from config import settings

logger = structlog.get_logger(__name__)

async def call_ollama(prompt: str) -> str:
    """Call local Ollama server and return raw text response."""
    url = f"{settings.OLLAMA_HOST}/api/generate"
    payload = {
        "model": settings.OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "format": "json"
    }
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(url, json=payload)
        response.raise_for_status()
        data = response.json()
        return data.get("response", "")
