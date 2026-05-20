"""List current model runs in Azure Container Instances."""

from typing import Any

from azure.core.credentials import TokenCredential
from azure.data.tables import TableClient
from azure.identity import DefaultAzureCredential
from azure.mgmt.containerinstance import ContainerInstanceManagementClient

from nhp.aci.config import Config
from nhp.aci.status.helpers import get_container_group_current_state


def _get_incomplete_model_runs_from_ats() -> list[dict[str, Any]]:
    config = Config.create_from_envvars()
    table_client = TableClient(
        endpoint=config.table_storage_endpoint,
        credential=DefaultAzureCredential(),
        table_name="modelruns",
    )

    return list(table_client.query_entities("status ne 'complete'"))


def get_current_model_runs(
    credential: TokenCredential | None = None,
    config: Config | None = None,
) -> dict[str, Any]:
    """Get the status of all current model runs.

    Args:
        credential (TokenCredential, optional): Credential for authenticating with Azure,
            defaults to None, and calls DefaultAzureCredential()
        config (Config, optional): Configuration object, defaults to  None, and calls
            Config.create_from_envvars()

    Returns:
        dict[str, Any]: A dictionary with the status of all current model runs.
    """
    if credential is None:
        credential = DefaultAzureCredential()
    if config is None:
        config = Config.create_from_envvars()

    incomplete_runs = {
        i["container_group_name"]: (i["dataset"], i["model_run_id"])
        for i in _get_incomplete_model_runs_from_ats()
        if "container_group_name" in i and i["container_group_name"] is not None
    }

    client = ContainerInstanceManagementClient(credential, config.subscription_id)
    resource_group = config.resource_group

    containers = {
        i.name: {
            "dataset": incomplete_runs[i.name][0] if i.name in incomplete_runs else None,
            "model_run_id": incomplete_runs[i.name][1] if i.name in incomplete_runs else None,
            "aci_status": get_container_group_current_state(i.name, client, resource_group, config),
        }
        for i in client.container_groups.list_by_resource_group(resource_group)
        if i.name is not None
    }

    return containers
