"""Tests for ACI methods."""

import pytest
from azure.mgmt.containerinstance.models import OperatingSystemTypes

from nhp.aci.run_model.aci import _build_container_command, create_and_start_container


@pytest.mark.parametrize("model_run_id", ["model-run-id", "another-run-id"])
def test__build_container_command(model_run_id):
    # arrange

    # act
    actual = _build_container_command("id", model_run_id, False, "30m")

    # assert
    assert actual == [
        "timeout",
        "-s",
        "SIGKILL",
        "30m",
        "/app/.venv/bin/python",
        "-m",
        "nhp.docker",
        "id.json",
        model_run_id,
    ]


def test_create_and_start_container_raises_for_unsupported_version(mocker, config):
    # arrange
    metadata = {
        "container_group_name": "container-group-name",
        "app_version": "v4.0",
        "model_run_id": "model-run-id",
    }
    m_container_instance_management_client = mocker.patch(
        "nhp.aci.run_model.aci.ContainerInstanceManagementClient"
    )

    # act
    with pytest.raises(ValueError, match=r"version >= v5.0"):
        create_and_start_container(
            metadata,
            True,
            "30m",
            "credential",  # ty: ignore[invalid-argument-type]
            config,
        )

    # assert
    m_container_instance_management_client.assert_not_called()


def test__build_container_command_full_model_results():
    # arrange

    # act
    actual = _build_container_command("id", "model-run-id", True)

    # assert
    assert actual == [
        "timeout",
        "-s",
        "SIGKILL",
        "60m",
        "/app/.venv/bin/python",
        "-m",
        "nhp.docker",
        "id.json",
        "model-run-id",
        "--save-full-model-results",
    ]


def test_create_and_start_container_with_log_analytics(mocker, config):
    # arrange
    metadata = {
        "container_group_name": "container-group-name",
        "app_version": "v5.0",
        "model_run_id": "model-run-id",
    }
    m_container_instance_management_client = mocker.patch(
        "nhp.aci.run_model.aci.ContainerInstanceManagementClient"
    )
    m_resource_requests = mocker.patch(
        "nhp.aci.run_model.aci.ResourceRequests", return_value="resource_requests"
    )
    m_resource_requirements = mocker.patch(
        "nhp.aci.run_model.aci.ResourceRequirements", return_value="resource_requirements"
    )
    m_build_container_command = mocker.patch(
        "nhp.aci.run_model.aci._build_container_command", return_value=["command"]
    )
    m_container = mocker.patch("nhp.aci.run_model.aci.Container", return_value="container")
    m_container_group_subnet_id = mocker.patch(
        "nhp.aci.run_model.aci.ContainerGroupSubnetId", return_value="subnet"
    )
    m_environment_variable = mocker.patch(
        "nhp.aci.run_model.aci.EnvironmentVariable", return_value="env_var"
    )
    m_container_group_identity = mocker.patch(
        "nhp.aci.run_model.aci.ContainerGroupIdentity", return_value="identity"
    )
    m_container_group_diagnostics = mocker.patch(
        "nhp.aci.run_model.aci.ContainerGroupDiagnostics", return_value="diagnostics"
    )
    m_log_analtics = mocker.patch(
        "nhp.aci.run_model.aci.LogAnalytics", return_value="log_analytics"
    )
    m_container_group = mocker.patch(
        "nhp.aci.run_model.aci.ContainerGroup", return_value="container_group"
    )
    m_user_assigned_identities = mocker.patch(
        "nhp.aci.run_model.aci.UserAssignedIdentities", return_value="user_assigned_identities"
    )

    # act
    create_and_start_container(
        metadata,
        True,
        "30m",
        "credential",  # ty: ignore[invalid-argument-type]
        config,
    )

    # assert
    m_container_instance_management_client.assert_called_once_with("credential", "subscription_id")
    m_resource_requests.assert_called_once_with(memory_in_gb=4.0, cpu=2)
    m_resource_requirements.assert_called_once_with(requests="resource_requests")
    m_build_container_command.assert_called_once_with(
        "container-group-name", "model-run-id", True, "30m"
    )
    m_container.assert_called_once_with(
        name="container-group-name",
        image="container_image:v5.0",
        resources="resource_requirements",
        environment_variables=["env_var"],
        command=["command"],
    )
    m_environment_variable.assert_called_once_with(name="STORAGE_ACCOUNT", value="storage_account")
    m_container_group_subnet_id.assert_called_once_with(id="subnet_id", name="subnet_name")
    m_container_group_identity.assert_called_once_with(
        type="UserAssigned",
        user_assigned_identities={"user_assigned_identity": "user_assigned_identities"},
    )
    m_container_group_diagnostics.assert_called_once_with(log_analytics="log_analytics")
    m_log_analtics.assert_called_once_with(
        workspace_id="log_analytics_workspace_id",
        workspace_key="log_analytics_workspace_key",
        workspace_resource_id="log_analytics_workspace_resource_id",
        log_type="ContainerInstanceLogs",
    )
    m_container_group.assert_called_once_with(
        identity="identity",
        location="azure_location",
        containers=["container"],
        os_type=OperatingSystemTypes.linux,
        diagnostics="diagnostics",
        restart_policy="Never",
        subnet_ids=["subnet"],
        tags={"project": "nhp"},
    )
    m_container_instance_management_client().container_groups.begin_create_or_update.assert_called_once_with(
        "resource_group", "container-group-name", "container_group"
    )
    m_user_assigned_identities.assert_called_once_with()


def test_create_and_start_container_without_log_analytics(mocker, config):
    # arrange
    config.log_analytics_workspace_id = None

    metadata = {
        "container_group_name": "container-group-name",
        "app_version": "v5.0",
        "model_run_id": "model-run-id",
    }
    m_container_instance_management_client = mocker.patch(
        "nhp.aci.run_model.aci.ContainerInstanceManagementClient"
    )
    m_resource_requests = mocker.patch(
        "nhp.aci.run_model.aci.ResourceRequests", return_value="resource_requests"
    )
    m_resource_requirements = mocker.patch(
        "nhp.aci.run_model.aci.ResourceRequirements", return_value="resource_requirements"
    )
    m_build_container_command = mocker.patch(
        "nhp.aci.run_model.aci._build_container_command", return_value=["command"]
    )
    m_container = mocker.patch("nhp.aci.run_model.aci.Container", return_value="container")
    m_container_group_subnet_id = mocker.patch(
        "nhp.aci.run_model.aci.ContainerGroupSubnetId", return_value="subnet"
    )
    m_environment_variable = mocker.patch(
        "nhp.aci.run_model.aci.EnvironmentVariable", return_value="env_var"
    )
    m_container_group_identity = mocker.patch(
        "nhp.aci.run_model.aci.ContainerGroupIdentity", return_value="identity"
    )
    m_container_group_diagnostics = mocker.patch(
        "nhp.aci.run_model.aci.ContainerGroupDiagnostics", return_value="diagnostics"
    )
    m_log_analtics = mocker.patch(
        "nhp.aci.run_model.aci.LogAnalytics", return_value="log_analytics"
    )
    m_container_group = mocker.patch(
        "nhp.aci.run_model.aci.ContainerGroup", return_value="container_group"
    )
    m_user_assigned_identities = mocker.patch(
        "nhp.aci.run_model.aci.UserAssignedIdentities", return_value="user_assigned_identities"
    )

    # act
    create_and_start_container(
        metadata,
        True,
        "30m",
        "credential",  # ty: ignore[invalid-argument-type]
        config,
    )

    # assert
    m_container_instance_management_client.assert_called_once_with("credential", "subscription_id")
    m_resource_requests.assert_called_once_with(memory_in_gb=4.0, cpu=2)
    m_resource_requirements.assert_called_once_with(requests="resource_requests")
    m_build_container_command.assert_called_once_with(
        "container-group-name", "model-run-id", True, "30m"
    )
    m_container.assert_called_once_with(
        name="container-group-name",
        image="container_image:v5.0",
        resources="resource_requirements",
        environment_variables=["env_var"],
        command=["command"],
    )
    m_environment_variable.assert_called_once_with(name="STORAGE_ACCOUNT", value="storage_account")
    m_container_group_subnet_id.assert_called_once_with(id="subnet_id", name="subnet_name")
    m_container_group_identity.assert_called_once_with(
        type="UserAssigned",
        user_assigned_identities={"user_assigned_identity": "user_assigned_identities"},
    )
    m_container_group_diagnostics.assert_not_called()
    m_log_analtics.assert_not_called()
    m_container_group.assert_called_once_with(
        identity="identity",
        location="azure_location",
        containers=["container"],
        os_type=OperatingSystemTypes.linux,
        diagnostics=None,
        restart_policy="Never",
        subnet_ids=["subnet"],
        tags={"project": "nhp"},
    )
    m_container_instance_management_client().container_groups.begin_create_or_update.assert_called_once_with(
        "resource_group", "container-group-name", "container_group"
    )
    m_user_assigned_identities.assert_called_once_with()
