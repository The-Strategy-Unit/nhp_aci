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
    config: Config = Config.create_from_envvars(),
) -> dict:
    bsc = BlobServiceClient(config.storage_endpoint, credential)
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
    config: Config = Config.create_from_envvars(),
) -> dict:
    client = ContainerInstanceManagementClient(credential, config.subscription_id)
    resource_group = config.resource_group

    return get_container_group_current_state(container_group_name, client, resource_group)


def get_model_run_status(
    container_group_name: str,
    credential: TokenCredential = DefaultAzureCredential(),
    config=Config.create_from_envvars(),
) -> dict | None:
    """Get the status of a model run by its container group name.

    :param container_group_name: The name of the container group.
    :type container_group_name: str
    :param credential: Credential for authenticating with Azure,
        defaults to DefaultAzureCredential()
    :type credential: TokenCredential, optional
    :param config: Configuration object, defaults to creating from envvars
    :type config: Config, optional
    :return: The status of the model run, or None if it does not exist.
    :rtype: dict | None
    """
    status = _get_queue_metadata(container_group_name, credential, config)

    try:
        return {**status, **_get_aci_status(container_group_name, credential, config)}

    except ResourceNotFoundError:
        if status:
            return {**status, "state": "Creating"}
        return None
