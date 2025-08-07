"""Helpers for Azure Container Instance status operations."""

from azure.mgmt.containerinstance import ContainerInstanceManagementClient

from nhp.aci.config import Config


def get_container_group_current_state(
    container_group_name: str,
    client: ContainerInstanceManagementClient,
    resource_group: str,
    config: Config = Config.create_from_envvars(),
) -> dict:
    """Get the state of a container group instance.

    :param container_group_name: The name of the container group.
    :type container_group_name: str
    :param client: a ContainerInstanceManagementClient instance.
    :type client: ContainerInstanceManagementClient
    :param resource_group: Which resource group the container group is in.
    :type resource_group: str
    :param config: Configuration object, defaults to creating from envvars
    :type config: Config, optional
    :return: dictionary with the state of the container group instance.
    :rtype: dict
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
