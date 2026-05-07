"""Get the status of a model run."""

from azure.core.credentials import TokenCredential
from azure.core.exceptions import ResourceNotFoundError
from azure.identity import DefaultAzureCredential
from azure.mgmt.containerinstance import ContainerInstanceManagementClient
from azure.storage.blob import BlobServiceClient

from nhp.aci.config import Config
from nhp.aci.status.helpers import get_container_group_current_state


def _get_queue_metadata(
    container_group_name: str,
    credential: TokenCredential,
    config: Config,
) -> dict:
    bsc = BlobServiceClient(config.blob_storage_endpoint, credential)
    cc = bsc.get_container_client("queue")
    bc = cc.get_blob_client(f"{container_group_name}.json")

    if not bc.exists():
        return {}

    m = bc.get_blob_properties()["metadata"]

    model_runs = int(m["model_runs"])

    def get_progress(key):
        return min(int(m.get(key, 0)), model_runs)

    return {
        "complete": {
            "inpatients": get_progress("Inpatients"),
            "outpatients": get_progress("Outpatients"),
            "aae": get_progress("AaE"),
        },
        "model_runs": model_runs,
    }


def _get_aci_status(
    container_group_name: str,
    credential: TokenCredential,
    config: Config,
) -> dict:
    client = ContainerInstanceManagementClient(credential, config.subscription_id)
    resource_group = config.resource_group

    return get_container_group_current_state(container_group_name, client, resource_group, config)


def get_model_run_status(
    container_group_name: str,
    credential: TokenCredential | None = None,
    config: Config | None = None,
) -> dict | None:
    """Get the status of a model run by its container group name.

    Args:
        container_group_name (str): The name of the container group.
        credential (TokenCredential, optional): Credential for authenticating with Azure,
            defaults to None, and calls DefaultAzureCredential()
        config (Config, optional): Configuration object, defaults to  None, and calls
            Config.create_from_envvars()

    Returns:
        dict | None: The status of the model run, or None if it does not exist.
    """
    if credential is None:
        credential = DefaultAzureCredential()
    if config is None:
        config = Config.create_from_envvars()

    status = _get_queue_metadata(container_group_name, credential, config)

    try:
        return {**status, **_get_aci_status(container_group_name, credential, config)}

    except ResourceNotFoundError:
        if status:
            return {**status, "state": "Creating"}
        return None
