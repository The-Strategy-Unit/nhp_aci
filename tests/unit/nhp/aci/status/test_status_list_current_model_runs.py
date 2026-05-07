"""Test the list_current_model_runs module in the nhp.aci.status package."""

from unittest.mock import Mock, call

from nhp.aci.status.list_current_model_runs import get_current_model_runs


def test_get_current_model_runs(mocker, config):
    # arrange
    m_cimc = mocker.patch(
        "nhp.aci.status.list_current_model_runs.ContainerInstanceManagementClient"
    )

    m_gcgis = mocker.patch(
        "nhp.aci.status.list_current_model_runs.get_container_group_current_state",
        return_value="state",
    )

    m_cred = mocker.patch("nhp.aci.clean_up.DefaultAzureCredential", return_value="cred")
    m_config = mocker.patch("nhp.aci.clean_up.Config.create_from_envvars", return_value=config)

    ma = Mock()
    ma.name = "a"
    mb = Mock()
    mb.name = "b"

    m_lbyg = m_cimc().container_groups.list_by_resource_group
    m_lbyg.return_value = [ma, mb]
    m_cimc.reset_mock()

    # act
    actual = get_current_model_runs("cred", config)  # ty: ignore[invalid-argument-type]

    # assert
    assert actual == {"a": "state", "b": "state"}

    m_cimc.assert_called_once_with("cred", "subscription_id")
    m_lbyg.assert_called_once_with("resource_group")
    assert m_gcgis.call_args_list == [
        call("a", m_cimc(), "resource_group", config),
        call("b", m_cimc(), "resource_group", config),
    ]

    m_cred.assert_not_called()
    m_config.assert_not_called()


def test_get_current_model_runs_creates_credential_and_config_if_none(mocker, config):
    # arrange
    m_cimc = mocker.patch(
        "nhp.aci.status.list_current_model_runs.ContainerInstanceManagementClient"
    )

    m_gcgis = mocker.patch(
        "nhp.aci.status.list_current_model_runs.get_container_group_current_state",
        return_value="state",
    )

    m_cred = mocker.patch(
        "nhp.aci.status.list_current_model_runs.DefaultAzureCredential", return_value="cred"
    )
    m_config = mocker.patch(
        "nhp.aci.status.list_current_model_runs.Config.create_from_envvars", return_value=config
    )

    ma = Mock()
    ma.name = "a"
    mb = Mock()
    mb.name = "b"

    m_lbyg = m_cimc().container_groups.list_by_resource_group
    m_lbyg.return_value = [ma, mb]
    m_cimc.reset_mock()

    # act
    actual = get_current_model_runs()

    # assert
    assert actual == {"a": "state", "b": "state"}

    m_cimc.assert_called_once_with("cred", "subscription_id")
    m_lbyg.assert_called_once_with("resource_group")
    assert m_gcgis.call_args_list == [
        call("a", m_cimc(), "resource_group", config),
        call("b", m_cimc(), "resource_group", config),
    ]

    m_cred.assert_called_once_with()
    m_config.assert_called_once_with()
