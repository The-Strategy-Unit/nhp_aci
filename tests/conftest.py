import pytest

from nhp.aci.config import Config


@pytest.fixture
def config():
    return Config(
        "storage_account",
        "subscription_id",
        "container_image",
        "azure_location",
        "subnet_name",
        "subnet_id",
        "user_assigned_identity",
        4.0,
        2,
        True,
        "resource_group",
        "log_analytics_workspace_id",
        "log_analytics_workspace_key",
        "log_analytics_workspace_resource_id",
    )
