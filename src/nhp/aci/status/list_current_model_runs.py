"""List current model runs in Azure Container Instances."""

from azure.core.credentials import TokenCredential
from azure.identity import DefaultAzureCredential
from azure.mgmt.containerinstance import ContainerInstanceManagementClient

from nhp.aci.config import Config
from nhp.aci.status.helpers import get_container_group_current_state


def get_current_model_runs(
    credential: TokenCredential | None = None,
    config: Config | None = None,
) -> dict:
    """Get the status of all current model runs.

    :param credential: Credential for authenticating with Azure,
        defaults to None, and calls DefaultAzureCredential()
    :type credential: TokenCredential, optional
    :param config: Configuration object, defaults to  None, and calls Config.create_from_envvars()
    :type config: Config, optional
    :return: A dictionary with the status of all current model runs.
    :rtype: dict
    """
    if credential is None:
        credential = DefaultAzureCredential()
    if config is None:
        config = Config.create_from_envvars()

    client = ContainerInstanceManagementClient(credential, config.subscription_id)
    resource_group = config.resource_group

    containers = {
        i.name: get_container_group_current_state(i.name, client, resource_group, config)  # type: ignore
        for i in client.container_groups.list_by_resource_group(resource_group)
    }

    return containers
