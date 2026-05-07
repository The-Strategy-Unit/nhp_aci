"""Helpers for Azure Container Instance status operations."""

from typing import Any

from azure.mgmt.containerinstance import ContainerInstanceManagementClient

from nhp.aci.config import Config


def get_container_group_current_state(
    container_group_name: str,
    client: ContainerInstanceManagementClient,
    resource_group: str,
    config: Config,
) -> dict[str, Any]:
    """Get the state of a container group instance.

    Args:
        container_group_name (str): The name of the container group.
        client (ContainerInstanceManagementClient): A ContainerInstanceManagementClient instance.
        resource_group (str): Which resource group the container group is in.
        config (Config): Configuration object

    Returns:
        dict[str, Any]: Dictionary with the state of the container group instance.
    """
    container = client.container_groups.get(resource_group, container_group_name).containers[0]
    instance_view = container.instance_view

    if instance_view is None:
        return {}

    current_state = instance_view.current_state
    if current_state is None:
        return {}

    if (
        config.auto_delete_completed_containers
        and current_state.state == "Terminated"
        and current_state.detail_status == "Completed"
    ):
        client.container_groups.begin_delete(resource_group, container_group_name)

    return current_state.as_dict()
