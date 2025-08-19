"""Methods for creating and starting Azure Container Instances for model runs."""

import logging
import re

from azure.core.credentials import TokenCredential
from azure.identity import DefaultAzureCredential
from azure.mgmt.containerinstance import ContainerInstanceManagementClient
from azure.mgmt.containerinstance.models import (
    Container,
    ContainerGroup,
    ContainerGroupDiagnostics,
    ContainerGroupIdentity,
    ContainerGroupSubnetId,
    EnvironmentVariable,
    LogAnalytics,
    OperatingSystemTypes,
    ResourceRequests,
    ResourceRequirements,
)

from nhp.aci.config import Config


def _build_container_command(
    model_id: str, tag: str, save_full_model_results: bool, timeout: str = "60m"
) -> list[str]:
    # before v4.0, the containers are started using /opt/docker_run.py
    match = re.match(r"^v(\d+)\.(\d)", tag)
    before_v4 = match and int(match.group(1)) < 4  # noqa: PLR2004
    command = (
        ["/opt/docker_run.py"]
        if before_v4
        else ["timeout", "-s", "SIGKILL", timeout, "/app/.venv/bin/python", "-m", "nhp.docker"]
    )

    command.append(f"{model_id}.json")
    if save_full_model_results:
        command.append("--save-full-model-results")

    return command


def create_and_start_container(
    metadata: dict,
    save_full_model_results: bool = False,
    credential: TokenCredential = DefaultAzureCredential(),
    config: Config = Config.create_from_envvars(),
) -> None:
    """Create and start a container instance for the model run.

    :param metadata: the model metadata
    :type metadata: dict
    :param save_full_model_results: whether to save the full model results, defaults to False
    :type save_full_model_results: bool, optional
    :param credential: Credential for authenticating with Azure,
        defaults to DefaultAzureCredential()
    :type credential: TokenCredential, optional
    :param config: Configuration object, defaults to creating from envvars
    :type config: Config, optional
    """
    model_id = metadata["id"]
    tag = metadata["app_version"]

    client = ContainerInstanceManagementClient(credential, config.subscription_id)

    container_resource_requests = ResourceRequests(
        memory_in_gb=config.container_memory, cpu=config.container_cpu
    )
    container_resource_requirements = ResourceRequirements(requests=container_resource_requests)

    command = _build_container_command(model_id, tag, save_full_model_results)

    container = Container(
        name=model_id,
        image=f"{config.container_image}:{tag}",
        resources=container_resource_requirements,
        environment_variables=[
            EnvironmentVariable(name="STORAGE_ACCOUNT", value=config.storage_account)
        ],
        command=command,
    )

    subnet = ContainerGroupSubnetId(id=config.subnet_id, name=config.subnet_name)

    identity = ContainerGroupIdentity(
        type="UserAssigned",
        user_assigned_identities={config.user_assigned_identity: {}},  # type: ignore
    )

    if config.log_analytics_workspace_id:
        diagnostics = ContainerGroupDiagnostics(
            log_analytics=LogAnalytics(
                workspace_id=config.log_analytics_workspace_id,
                workspace_key=config.log_analytics_workspace_key,
                workspace_resource_id=config.log_analytics_workspace_resource_id,
                log_type="ContainerInstanceLogs",
            )
        )
    else:
        diagnostics = None

    cgroup = ContainerGroup(
        identity=identity,
        location=config.azure_location,
        containers=[container],
        os_type=OperatingSystemTypes.linux,  # type: ignore
        diagnostics=diagnostics,
        restart_policy="Never",
        subnet_ids=[subnet],
        tags={"project": "nhp"},
    )

    client.container_groups.begin_create_or_update(config.resource_group, f"{model_id}", cgroup)
    logging.info("container created with command: %s", " ".join(command))
    logging.info("container created with command: %s", " ".join(command))
    logging.info("container created with command: %s", " ".join(command))
