"""Get the status of a model run."""

import json
from typing import Any

from azure.core.credentials import TokenCredential
from azure.core.exceptions import ResourceNotFoundError
from azure.data.tables import TableClient
from azure.identity import DefaultAzureCredential
from azure.mgmt.containerinstance import ContainerInstanceManagementClient

from nhp.aci.config import Config
from nhp.aci.status.helpers import get_container_group_current_state


def _get_progress_from_ats(
    dataset: str,
    model_run_id: str,
    credential: TokenCredential,
    config: Config,
) -> dict[str, Any]:
    table_client = TableClient(
        endpoint=config.table_storage_endpoint,
        credential=credential,
        table_name="modelruns",
    )

    try:
        entity = table_client.get_entity(partition_key=dataset, row_key=model_run_id)

        res = {
            "complete": json.loads(entity.get("progress", "{}")),
            "model_runs": entity["model_runs"],
            "container_group_name": None,
        }

        if entity["status"] == "complete":
            res["status"] = "complete"
        else:
            res["container_group_name"] = entity.get("container_group_name", None)

        return res
    except ResourceNotFoundError:
        return {}


def _get_aci_status(
    container_group_name: str,
    credential: TokenCredential,
    config: Config,
) -> dict:
    client = ContainerInstanceManagementClient(credential, config.subscription_id)
    resource_group = config.resource_group

    return get_container_group_current_state(container_group_name, client, resource_group, config)


def get_model_run_status(
    dataset: str,
    model_run_id: str,
    credential: TokenCredential | None = None,
    config: Config | None = None,
) -> dict | None:
    """Get the status of a model run by its container group name.

    Args:
        dataset (str): The dataset of the model run.
        model_run_id (str): The ID of the model run.
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

    status = _get_progress_from_ats(dataset, model_run_id, credential, config)
    if not status:
        return None

    container_group_name = status.pop("container_group_name")
    if not container_group_name:
        return status

    try:
        return {**status, **_get_aci_status(container_group_name, credential, config)}

    except ResourceNotFoundError:
        return {**status, "state": "Creating"}
