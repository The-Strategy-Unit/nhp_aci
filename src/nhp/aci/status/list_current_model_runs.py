"""List current model runs in Azure Container Instances."""

from typing import Any

from azure.core.credentials import TokenCredential
from azure.data.tables import TableClient
from azure.identity import DefaultAzureCredential
from azure.mgmt.containerinstance import ContainerInstanceManagementClient

from nhp.aci.config import Config
from nhp.aci.status.helpers import get_container_group_current_state


def _get_dataset_and_model_run_id_from_container_name(
    credential: TokenCredential, config: Config, container_name: str
) -> dict[str, Any]:
    table_client = TableClient(
        endpoint=config.table_storage_endpoint,
        credential=credential,
        table_name="modelruns",
    )

    container_name_escaped = container_name.replace("'", "''")

    names_filter = f"container_group_name eq '{container_name_escaped}'"
    entities = list(table_client.query_entities(names_filter))

    if len(entities) == 0:
        raise ValueError(f"No entity found for container name '{container_name}'")
    if len(entities) > 1:
        raise ValueError(f"Multiple entities found for container name '{container_name}'")

    return entities[0]


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

    client = ContainerInstanceManagementClient(credential, config.subscription_id)
    resource_group = config.resource_group

    containers = {}
    for i in client.container_groups.list_by_resource_group(resource_group):
        container_group_name = str(i.name)
        ats = _get_dataset_and_model_run_id_from_container_name(
            credential, config, container_group_name
        )
        containers[container_group_name] = {
            "dataset": ats["dataset"],
            "model_run_id": ats["model_run_id"],
            "aci_status": get_container_group_current_state(
                container_group_name, client, resource_group, config
            ),
        }

    return containers
