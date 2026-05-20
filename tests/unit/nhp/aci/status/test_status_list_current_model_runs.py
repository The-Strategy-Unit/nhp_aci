"""Test the list_current_model_runs module in the nhp.aci.status package."""

from unittest.mock import Mock, call

from nhp.aci.status.list_current_model_runs import (
    _get_incomplete_model_runs_from_ats,
    get_current_model_runs,
)


def test_get_incomplete_model_runs_from_ats(mocker, config):
    # arrange
    m_config = mocker.patch(
        "nhp.aci.status.list_current_model_runs.Config.create_from_envvars",
        return_value=config,
    )
    m_cred = mocker.patch(
        "nhp.aci.status.list_current_model_runs.DefaultAzureCredential",
        return_value="cred",
    )
    m_table_client = mocker.patch("nhp.aci.status.list_current_model_runs.TableClient")

    entities = [{"container_group_name": "a", "dataset": "d1", "model_run_id": "m1"}]
    table_client_instance = m_table_client.return_value
    table_client_instance.query_entities.return_value = entities

    # act
    actual = _get_incomplete_model_runs_from_ats()

    # assert
    assert actual == entities
    m_config.assert_called_once_with()
    m_cred.assert_called_once_with()
    m_table_client.assert_called_once_with(
        endpoint="https://storage_account.table.core.windows.net",
        credential="cred",
        table_name="modelruns",
    )
    table_client_instance.query_entities.assert_called_once_with("status ne 'complete'")


def test_get_current_model_runs(mocker, config):
    # arrange
    m_cimc = mocker.patch(
        "nhp.aci.status.list_current_model_runs.ContainerInstanceManagementClient"
    )

    m_gcgis = mocker.patch(
        "nhp.aci.status.list_current_model_runs.get_container_group_current_state",
        side_effect=["state-a", "state-b"],
    )

    m_incomplete = mocker.patch(
        "nhp.aci.status.list_current_model_runs._get_incomplete_model_runs_from_ats",
        return_value=[
            {"container_group_name": "a", "dataset": "d1", "model_run_id": "m1"},
            {"container_group_name": None, "dataset": "ignored", "model_run_id": "ignored"},
            {"dataset": "ignored", "model_run_id": "ignored"},
        ],
    )

    ma = Mock()
    ma.name = "a"
    mb = Mock()
    mb.name = "b"
    mn = Mock()
    mn.name = None

    m_lbyg = m_cimc().container_groups.list_by_resource_group
    m_lbyg.return_value = [ma, mb, mn]
    m_cimc.reset_mock()

    # act
    actual = get_current_model_runs("cred", config)  # ty: ignore[invalid-argument-type]

    # assert
    assert actual == {
        "a": {"dataset": "d1", "model_run_id": "m1", "aci_status": "state-a"},
        "b": {"dataset": None, "model_run_id": None, "aci_status": "state-b"},
    }

    m_incomplete.assert_called_once_with()
    m_cimc.assert_called_once_with("cred", "subscription_id")
    m_lbyg.assert_called_once_with("resource_group")
    assert m_gcgis.call_args_list == [
        call("a", m_cimc(), "resource_group", config),
        call("b", m_cimc(), "resource_group", config),
    ]


def test_get_current_model_runs_creates_credential_and_config_if_none(mocker, config):
    # arrange
    m_cimc = mocker.patch(
        "nhp.aci.status.list_current_model_runs.ContainerInstanceManagementClient"
    )

    m_gcgis = mocker.patch(
        "nhp.aci.status.list_current_model_runs.get_container_group_current_state",
        return_value="state",
    )

    m_incomplete = mocker.patch(
        "nhp.aci.status.list_current_model_runs._get_incomplete_model_runs_from_ats",
        return_value=[{"container_group_name": "a", "dataset": "d1", "model_run_id": "m1"}],
    )

    m_cred = mocker.patch(
        "nhp.aci.status.list_current_model_runs.DefaultAzureCredential", return_value="cred"
    )
    m_config = mocker.patch(
        "nhp.aci.status.list_current_model_runs.Config.create_from_envvars", return_value=config
    )

    ma = Mock()
    ma.name = "a"
    m_lbyg = m_cimc().container_groups.list_by_resource_group
    m_lbyg.return_value = [ma]
    m_cimc.reset_mock()

    # act
    actual = get_current_model_runs()

    # assert
    assert actual == {
        "a": {"dataset": "d1", "model_run_id": "m1", "aci_status": "state"},
    }

    m_incomplete.assert_called_once_with()
    m_cimc.assert_called_once_with("cred", "subscription_id")
    m_lbyg.assert_called_once_with("resource_group")
    m_gcgis.assert_called_once_with("a", m_cimc(), "resource_group", config)

    m_cred.assert_called_once_with()
    m_config.assert_called_once_with()
