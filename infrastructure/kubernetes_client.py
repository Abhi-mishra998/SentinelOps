from kubernetes import client, config
import structlog

logger = structlog.get_logger(__name__)

def init_k8s_client():
    """Initializes the Kubernetes client. Tries in-cluster config first, then kubeconfig."""
    try:
        config.load_incluster_config()
        logger.info("Loaded in-cluster Kubernetes configuration")
    except config.ConfigException:
        try:
            config.load_kube_config()
            logger.info("Loaded local kubeconfig configuration")
        except config.ConfigException as e:
            logger.error("Failed to load any Kubernetes configuration", error=str(e))
            raise e

def get_core_v1_api() -> client.CoreV1Api:
    # ApiClient() by default uses the configuration set by load_kube_config()
    api_client = client.ApiClient()
    api_client.timeout = 10.0
    return client.CoreV1Api(api_client)

def get_apps_v1_api() -> client.AppsV1Api:
    api_client = client.ApiClient()
    api_client.timeout = 10.0
    return client.AppsV1Api(api_client)
