"""Test the config module in the nhp.aci package."""

import os
from unittest.mock import patch

import pytest

from nhp.aci.config import Config

mock_envvars = {
    "STORAGE_ACCOUNT": "STORAGE_ACCOUNT",
    "SUBSCRIPTION_ID": "SUBSCRIPTION_ID",
    "CONTAINER_IMAGE": "CONTAINER_IMAGE",
    "AZURE_LOCATION": "AZURE_LOCATION",
    "SUBNET_NAME": "SUBNET_NAME",
    "SUBNET_ID": "SUBNET_ID",
    "USER_ASSIGNED_IDENTITY": "USER_ASSIGNED_IDENTITY",
    "CONTAINER_MEMORY": "4.0",
    "CONTAINER_CPU": "2",
    "AUTO_DELETE_COMPLETED_CONTAINERS": "True",
    "RESOURCE_GROUP": "RESOURCE_GROUP",
    "LOG_ANALYTICS_WORKSPACE_ID": "LOG_ANALYTICS_WORKSPACE_ID",
    "LOG_ANALYTICS_WORKSPACE_KEY": "LOG_ANALYTICS_WORKSPACE_KEY",
    "LOG_ANALYTICS_WORKSPACE_RESOURCE_ID": "LOG_ANALYTICS_WORKSPACE_RESOURCE_ID",
}


def test_create_from_envvars(mocker):
    # arrange
    mocker.patch("nhp.aci.config.Config.get_config_file_path")

    # act
    with patch.dict(os.environ, mock_envvars):
        actual = Config.create_from_envvars()

    # assert
    assert actual.storage_account == "STORAGE_ACCOUNT"
    assert actual.subscription_id == "SUBSCRIPTION_ID"
    assert actual.container_image == "CONTAINER_IMAGE"
    assert actual.azure_location == "AZURE_LOCATION"
    assert actual.subnet_name == "SUBNET_NAME"
    assert actual.subnet_id == "SUBNET_ID"
    assert actual.user_assigned_identity == "USER_ASSIGNED_IDENTITY"
    assert actual.container_memory == 4.0
    assert actual.container_cpu == 2
    assert actual.auto_delete_completed_containers
    assert actual.resource_group == "RESOURCE_GROUP"
    assert actual.log_analytics_workspace_id == "LOG_ANALYTICS_WORKSPACE_ID"
    assert actual.log_analytics_workspace_key == "LOG_ANALYTICS_WORKSPACE_KEY"
    assert actual.log_analytics_workspace_resource_id == "LOG_ANALYTICS_WORKSPACE_RESOURCE_ID"


def test_create_from_envvars_validates_auto_delete(mocker):
    # arrange
    mocker.patch("nhp.aci.config.Config.get_config_file_path")

    dt = mock_envvars.copy()
    dt["AUTO_DELETE_COMPLETED_CONTAINERS"] = "True"

    df = mock_envvars.copy()
    df["AUTO_DELETE_COMPLETED_CONTAINERS"] = "False"

    de = mock_envvars.copy()
    de["AUTO_DELETE_COMPLETED_CONTAINERS"] = "something else"

    # act
    with patch.dict(os.environ, dt):
        actual_true = Config.create_from_envvars()

    with patch.dict(os.environ, df):
        actual_false = Config.create_from_envvars()

    with pytest.raises(ValueError, match="AUTO_DELETE_COMPLETED_CONTAINERS must be True or False"):
        with patch.dict(os.environ, de):
            actual_false = Config.create_from_envvars()

    # assert
    assert actual_true.auto_delete_completed_containers
    assert not actual_false.auto_delete_completed_containers


def test_create_from_envvars_passes_config_dir(mocker):
    """Test that create_from_envvars passes the config_dir to get_config_file_path."""
    # arrange
    get_config_file_path_mock = mocker.patch("nhp.aci.config.Config.get_config_file_path")

    # act
    with patch.dict(os.environ, mock_envvars):
        Config.create_from_envvars(config_dir="custom_dir")

    # assert
    get_config_file_path_mock.assert_called_once_with(config_dir="custom_dir")


def test_config_storage_endpoint(config):
    # assert
    assert config.storage_endpoint == "https://storage_account.blob.core.windows.net"
