import asyncio
import time
from dataclasses import dataclass
from kubernetes import client
import structlog

logger = structlog.get_logger(__name__)

@dataclass
class ValidationResult:
    success: bool
    message: str
    elapsed_seconds: float = 0.0

class ValidationEngine:
    def __init__(self):
        self.v1 = client.CoreV1Api()

    async def validate_pod_recovery(
        self, namespace: str, pod_name: str, timeout: int = 120
    ) -> ValidationResult:
        """Poll pod status with exponential backoff until ready or timeout."""
        start   = time.time()
        backoff = 2.0
        logger.info("Validating pod recovery", pod=pod_name, ns=namespace, timeout=timeout)

        while time.time() - start < timeout:
            try:
                pod = await asyncio.to_thread(
                    self.v1.read_namespaced_pod, name=pod_name, namespace=namespace
                )
                if pod.status.phase == "Running":
                    container_statuses = pod.status.container_statuses or []
                    all_ready = all(c.ready for c in container_statuses)
                    if all_ready:
                        elapsed = round(time.time() - start, 1)
                        logger.info("Pod recovered successfully", pod=pod_name, elapsed=elapsed)
                        return ValidationResult(
                            success=True,
                            message=f"Pod {pod_name} is Running and all containers are ready.",
                            elapsed_seconds=elapsed
                        )
            except Exception as e:
                logger.debug("Pod not yet found (may be recreating)", pod=pod_name, error=str(e))

            await asyncio.sleep(backoff)
            backoff = min(backoff * 1.5, 15.0)

        elapsed = round(time.time() - start, 1)
        logger.warning("Pod validation timed out", pod=pod_name, elapsed=elapsed)
        return ValidationResult(
            success=False,
            message=f"Validation timeout after {timeout}s — manual check required for pod {pod_name}.",
            elapsed_seconds=elapsed
        )

    async def validate_deployment_health(
        self, namespace: str, deployment_name: str, timeout: int = 120
    ) -> ValidationResult:
        """Poll deployment until all replicas are available or timeout."""
        start   = time.time()
        backoff = 2.0

        while time.time() - start < timeout:
            try:
                dep = await asyncio.to_thread(
                    self.v1._api_client.call_api,
                    f"/apis/apps/v1/namespaces/{namespace}/deployments/{deployment_name}",
                    "GET", response_type="object"
                )
                status = dep[0].get("status", {})
                desired   = status.get("replicas", 0)
                available = status.get("availableReplicas", 0)
                if desired > 0 and desired == available:
                    elapsed = round(time.time() - start, 1)
                    return ValidationResult(
                        success=True,
                        message=f"Deployment {deployment_name}: {available}/{desired} replicas available.",
                        elapsed_seconds=elapsed
                    )
            except Exception as e:
                logger.debug("Deployment status check failed", deployment=deployment_name, error=str(e))

            await asyncio.sleep(backoff)
            backoff = min(backoff * 1.5, 15.0)

        elapsed = round(time.time() - start, 1)
        return ValidationResult(
            success=False,
            message=f"Deployment {deployment_name} not fully healthy after {timeout}s.",
            elapsed_seconds=elapsed
        )
