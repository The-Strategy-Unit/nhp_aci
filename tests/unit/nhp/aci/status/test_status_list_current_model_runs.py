"""Test the list_current_model_runs module in the nhp.aci.status package."""

from unittest.mock import Mock, call

from nhp.aci.status.list_current_model_runs import (
    _get_dataset_and_model_run_id_from_container_name,
    get_current_model_runs,
)


def test__get_dataset_and_model_run_id_from_container_name(mocker, config):
    # arrange
    m_table_client = mocker.patch("nhp.aci.status.list_current_model_runs.TableClient")

    entities = [{"container_group_name": "a", "dataset": "d1", "model_run_id": "m1"}]
    table_client_instance = m_table_client.return_value
    table_client_instance.query_entities.return_value = entities

    # act
    actual = _get_dataset_and_model_run_id_from_container_name("cred", config, "a")  # ty: ignore[invalid-argument-type]

    # assert
    assert actual == entities[0]
    m_table_client.assert_called_once_with(
        endpoint="https://storage_account.table.core.windows.net",
        credential="cred",
        table_name="modelruns",
    )
    table_client_instance.query_entities.assert_called_once_with("container_group_name eq 'a'")


def test__get_dataset_and_model_run_id_from_container_name_escapes_quotes(mocker, config):
    # arrange
    m_table_client = mocker.patch("nhp.aci.status.list_current_model_runs.TableClient")

    table_client_instance = m_table_client.return_value
    table_client_instance.query_entities.return_value = [{"dataset": "d1", "model_run_id": "m1"}]

    # act
    _get_dataset_and_model_run_id_from_container_name("cred", config, "a'b")  # ty: ignore[invalid-argument-type]

    # assert
    table_client_instance.query_entities.assert_called_once_with("container_group_name eq 'a''b'")


def test__get_dataset_and_model_run_id_from_container_name_no_entity_raises(mocker, config):
    # arrange
    m_table_client = mocker.patch("nhp.aci.status.list_current_model_runs.TableClient")
    m_table_client.return_value.query_entities.return_value = []

    # act / assert
    try:
        _get_dataset_and_model_run_id_from_container_name("cred", config, "a")  # ty: ignore[invalid-argument-type]
        raise AssertionError("Expected ValueError")
    except ValueError as exc:
        assert str(exc) == "No entity found for container name 'a'"


def test__get_dataset_and_model_run_id_from_container_name_multiple_entities_raises(mocker, config):
    # arrange
    m_table_client = mocker.patch("nhp.aci.status.list_current_model_runs.TableClient")
    m_table_client.return_value.query_entities.return_value = [
        {"dataset": "d1", "model_run_id": "m1"},
        {"dataset": "d2", "model_run_id": "m2"},
    ]

    # act / assert
    try:
        _get_dataset_and_model_run_id_from_container_name("cred", config, "a")  # ty: ignore[invalid-argument-type]
        raise AssertionError("Expected ValueError")
    except ValueError as exc:
        assert str(exc) == "Multiple entities found for container name 'a'"


def test_get_current_model_runs(mocker, config):
    # arrange
    m_cimc = mocker.patch(
        "nhp.aci.status.list_current_model_runs.ContainerInstanceManagementClient"
    )

    m_gcgis = mocker.patch(
        "nhp.aci.status.list_current_model_runs.get_container_group_current_state",
        side_effect=["state-a", "state-b"],
    )

    m_get_dataset = mocker.patch(
        "nhp.aci.status.list_current_model_runs._get_dataset_and_model_run_id_from_container_name",
        side_effect=[
            {"dataset": "d1", "model_run_id": "m1"},
            {"dataset": "d2", "model_run_id": "m2"},
        ],
    )

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
    assert actual == {
        "a": {"dataset": "d1", "model_run_id": "m1", "aci_status": "state-a"},
        "b": {"dataset": "d2", "model_run_id": "m2", "aci_status": "state-b"},
    }

    assert m_get_dataset.call_args_list == [
        call("cred", config, "a"),
        call("cred", config, "b"),
    ]
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

    m_get_dataset = mocker.patch(
        "nhp.aci.status.list_current_model_runs._get_dataset_and_model_run_id_from_container_name",
        return_value={"dataset": "d1", "model_run_id": "m1"},
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

    assert m_get_dataset.call_args_list == [call("cred", config, "a")]
    m_cimc.assert_called_once_with("cred", "subscription_id")
    m_lbyg.assert_called_once_with("resource_group")
    m_gcgis.assert_called_once_with("a", m_cimc(), "resource_group", config)

    m_cred.assert_called_once_with()
    m_config.assert_called_once_with()
