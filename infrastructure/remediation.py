from dataclasses import dataclass
from typing import Optional
from kubernetes import client
import asyncio
import structlog

logger = structlog.get_logger(__name__)

@dataclass
class RemediationContext:
    pod_name:        str
    namespace:       str
    deployment_name: Optional[str] = None
    target_replicas: Optional[int] = None
    new_memory_limit: Optional[str] = None

@dataclass
class RemediationResult:
    action:  str
    success: bool
    message: str = ""

class RemediationEngine:
    ACTION_HANDLERS = {
        "restart_pod":         "_restart_pod",
        "rollback_deployment": "_rollback_deployment",
        "scale_deployment":    "_scale_deployment",
        "increase_limits":     "_increase_resource_limits",
    }

    def __init__(self):
        self.v1      = client.CoreV1Api()
        self.apps_v1 = client.AppsV1Api()

    async def execute(self, action: str, context: RemediationContext) -> RemediationResult:
        """Execute the given approved action. Must only be called after safety gate approval."""
        handler_name = self.ACTION_HANDLERS.get(action)
        if not handler_name:
            raise ValueError(f"Unknown remediation action: {action}")
        handler = getattr(self, handler_name)
        logger.info("Executing remediation", action=action, pod=context.pod_name, ns=context.namespace)
        return await handler(context)

    async def _restart_pod(self, ctx: RemediationContext) -> RemediationResult:
        await asyncio.to_thread(
            self.v1.delete_namespaced_pod,
            name=ctx.pod_name,
            namespace=ctx.namespace
        )
        logger.info("Pod deleted for restart", pod=ctx.pod_name, ns=ctx.namespace)
        return RemediationResult(action="restart_pod", success=True, message=f"Deleted pod {ctx.pod_name}; controller will recreate it.")

    async def _rollback_deployment(self, ctx: RemediationContext) -> RemediationResult:
        dep_name = ctx.deployment_name or ctx.pod_name.rsplit("-", 2)[0]
        deployment = await asyncio.to_thread(
            self.apps_v1.read_namespaced_deployment,
            name=dep_name, namespace=ctx.namespace
        )
        # Trigger rollback by bumping the rollback annotation
        if not deployment.metadata.annotations:
            deployment.metadata.annotations = {}
        deployment.metadata.annotations["kubectl.kubernetes.io/last-applied-configuration"] = ""
        await asyncio.to_thread(
            self.apps_v1.patch_namespaced_deployment,
            name=dep_name, namespace=ctx.namespace, body=deployment
        )
        logger.info("Deployment rollback triggered", deployment=dep_name, ns=ctx.namespace)
        return RemediationResult(action="rollback_deployment", success=True, message=f"Rollback triggered for {dep_name}.")

    async def _scale_deployment(self, ctx: RemediationContext) -> RemediationResult:
        dep_name = ctx.deployment_name or ctx.pod_name.rsplit("-", 2)[0]
        replicas = ctx.target_replicas or 2
        await asyncio.to_thread(
            self.apps_v1.patch_namespaced_deployment_scale,
            name=dep_name, namespace=ctx.namespace,
            body={"spec": {"replicas": replicas}}
        )
        logger.info("Deployment scaled", deployment=dep_name, replicas=replicas)
        return RemediationResult(action="scale_deployment", success=True, message=f"Scaled {dep_name} to {replicas} replicas.")

    async def _increase_resource_limits(self, ctx: RemediationContext) -> RemediationResult:
        dep_name = ctx.deployment_name or ctx.pod_name.rsplit("-", 2)[0]
        new_limit = ctx.new_memory_limit or "512Mi"
        patch_body = {
            "spec": {
                "template": {
                    "spec": {
                        "containers": [
                            {"name": dep_name, "resources": {"limits": {"memory": new_limit}}}
                        ]
                    }
                }
            }
        }
        await asyncio.to_thread(
            self.apps_v1.patch_namespaced_deployment,
            name=dep_name, namespace=ctx.namespace, body=patch_body
        )
        logger.info("Resource limits increased", deployment=dep_name, new_limit=new_limit)
        return RemediationResult(action="increase_limits", success=True, message=f"Memory limit for {dep_name} updated to {new_limit}.")
