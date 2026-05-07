"""Methods for creating and starting Azure Container Instances for model runs."""

import logging
import re
from typing import Any
from uuid import UUID

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

logger = logging.getLogger(__name__)


def _build_container_command(
    container_name: str,
    model_run_id: str,
    save_full_model_results: bool,
    timeout: str = "60m",
) -> list[str]:
    command = [
        "timeout",
        "-s",
        "SIGKILL",
        timeout,
        "/app/.venv/bin/python",
        "-m",
        "nhp.docker",
        f"{container_name}.json",
        model_run_id,
    ]

    if save_full_model_results:
        command.append("--save-full-model-results")

    return command


def create_and_start_container(
    metadata: dict[str, Any],
    model_run_id: str,
    save_full_model_results: bool,
    timeout: str,
    credential: TokenCredential,
    config: Config,
) -> None:
    """Create and start a container instance for the model run.

    Args:
        metadata (dict[str, Any]): The model metadata.
        model_run_id (str): The ID of the model run.
        save_full_model_results (bool): Whether to save the full model results.
        timeout (str): The timeout for the container.
        credential (TokenCredential): Credential for authenticating with Azure,
            defaults to DefaultAzureCredential().
        config (Config): Configuration object, defaults to creating from envvars.
    """
    container_name = metadata["id"]
    tag = metadata["app_version"]

    if re.match(r"^v[0-4]\.", tag):
        raise ValueError(f"App version {tag} is not supported. Please use a version >= v5.0.")

    client = ContainerInstanceManagementClient(credential, config.subscription_id)

    container_resource_requests = ResourceRequests(
        memory_in_gb=config.container_memory, cpu=config.container_cpu
    )
    container_resource_requirements = ResourceRequirements(requests=container_resource_requests)

    command = _build_container_command(
        container_name, model_run_id, save_full_model_results, timeout
    )

    container = Container(
        name=container_name,
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

    client.container_groups.begin_create_or_update(
        config.resource_group, f"{container_name}", cgroup
    )
    logger.info("container created with command: %s", " ".join(command))
