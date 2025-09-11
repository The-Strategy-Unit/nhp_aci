"""Clean up ACI/blob resources."""

from azure.core.credentials import TokenCredential
from azure.core.exceptions import ResourceNotFoundError
from azure.identity import DefaultAzureCredential
from azure.mgmt.containerinstance import ContainerInstanceManagementClient
from azure.storage.blob import BlobServiceClient

from nhp.aci.config import Config


def _delete_blob_in_queue(
    model_run_id: str,
    credential: TokenCredential = DefaultAzureCredential(),
    config: Config = Config.create_from_envvars(),
) -> None:
    """Delete params in queue.

    Clean up a model run by deleting the params file in the queue.

    :param model_run_id: The id of the model run to delete.
    :type model_run_id: str
    :param credential: Credential for authenticating with Azure,
        defaults to DefaultAzureCredential()
    :type credential: TokenCredential, optional
    :param config: Configuration object, defaults to creating from envvars
    :type config: Config, optional
    """
    filename = f"{model_run_id}.json"
    bsc = BlobServiceClient(config.storage_endpoint, credential)
    cont = bsc.get_container_client("queue")
    try:
        cont.delete_blob(filename)
        print(f"Successfully deleted {filename} from queue")
    except ResourceNotFoundError:
        print(f"{filename} does not exist, potentially already removed")


def _delete_container_group(
    model_run_id: str,
    credential: TokenCredential = DefaultAzureCredential(),
    config: Config = Config.create_from_envvars(),
) -> None:
    """Delete container group.

    Clean up a model run by deleting the compute resource in ACI.

    :param model_run_id: The id of the model run to delete.
    :type model_run_id: str
    :param credential: Credential for authenticating with Azure,
        defaults to DefaultAzureCredential()
    :type credential: TokenCredential, optional
    :param config: Configuration object, defaults to creating from envvars
    :type config: Config, optional
    """
    client = ContainerInstanceManagementClient(credential, config.subscription_id)
    try:
        client.container_groups.begin_delete(config.resource_group, model_run_id)
        print(f"Successfully deleted container group {model_run_id}")
    except ResourceNotFoundError:
        print(f"{model_run_id} does not exist, potentially already removed")


def clean_up_model_run(
    model_run_id: str,
    credential: TokenCredential = DefaultAzureCredential(),
    config: Config = Config.create_from_envvars(),
) -> None:
    """Clean up a model run.

    Clean up a model run by deleting both the params file in the queue, and the compute resource
    in ACI.

    :param model_run_id: The id of the model run to delete.
    :type model_run_id: str
    :param credential: Credential for authenticating with Azure,
        defaults to DefaultAzureCredential()
    :type credential: TokenCredential, optional
    :param config: Configuration object, defaults to creating from envvars
    :type config: Config, optional
    """
    _delete_blob_in_queue(model_run_id, credential, config)
    _delete_container_group(model_run_id, credential, config)
