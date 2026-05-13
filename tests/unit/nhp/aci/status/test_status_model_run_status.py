"""Test the model_run_status module in the nhp.aci.status package."""

from azure.core.exceptions import ResourceNotFoundError

from nhp.aci.status.model_run_status import (
    _get_aci_status,
    _get_progress_from_ats,
    get_model_run_status,
)


def test__get_progress_from_ats(mocker, config):
    # arrange
    m_tc = mocker.patch("nhp.aci.status.model_run_status.TableClient")

    m_tc.return_value.get_entity.return_value = {
        "progress": '{"inpatients": 100, "outpatients": 50, "aae": 0}',
        "model_runs": 100,
        "status": "running",
        "container_group_name": "name",
    }

    m_tc.reset_mock()

    # act
    actual = _get_progress_from_ats("dataset", "id", "credential", config)  # ty: ignore[invalid-argument-type]

    # assert
    assert actual == {
        "complete": {"inpatients": 100, "outpatients": 50, "aae": 0},
        "model_runs": 100,
        "container_group_name": "name",
    }

    m_tc.assert_called_once_with(
        endpoint="https://storage_account.table.core.windows.net",
        credential="credential",
        table_name="modelruns",
    )
    m_tc.return_value.get_entity.assert_called_once_with(partition_key="dataset", row_key="id")


def test__get_progress_from_ats_not_found(mocker, config):
    # arrange
    m_tc = mocker.patch("nhp.aci.status.model_run_status.TableClient")
    m_tc.return_value.get_entity.side_effect = ResourceNotFoundError("Not Found")

    # act
    actual = _get_progress_from_ats("name", "id", "credential", config)  # ty: ignore[invalid-argument-type]

    # assert
    assert actual == {}
    m_tc.assert_called_once_with(
        endpoint="https://storage_account.table.core.windows.net",
        credential="credential",
        table_name="modelruns",
    )
    m_tc.return_value.get_entity.assert_called_once_with(partition_key="name", row_key="id")


def test__get_progress_from_ats_complete_status_without_container_group_name(mocker, config):
    # arrange
    m_tc = mocker.patch("nhp.aci.status.model_run_status.TableClient")

    m_tc.return_value.get_entity.return_value = {
        "model_runs": 100,
        "status": "complete",
    }

    # act
    actual = _get_progress_from_ats("dataset", "id", "credential", config)  # ty: ignore[invalid-argument-type]

    # assert
    assert actual == {
        "complete": {},
        "model_runs": 100,
        "container_group_name": None,
        "status": "complete",
    }
    m_tc.return_value.get_entity.assert_called_once_with(partition_key="dataset", row_key="id")


def test__get_aci_status(mocker, config):
    # arrange
    m_cimc = mocker.patch("nhp.aci.status.model_run_status.ContainerInstanceManagementClient")
    m_gcgis = mocker.patch(
        "nhp.aci.status.model_run_status.get_container_group_current_state", return_value="state"
    )

    # act
    actual = _get_aci_status("name", "credential", config)  # ty: ignore[invalid-argument-type]

    # assert
    assert actual == "state"
    m_cimc.assert_called_once_with("credential", "subscription_id")
    m_gcgis.assert_called_once_with("name", m_cimc(), "resource_group", config)


def test_get_model_run_status(mocker, config):
    # arrange
    m_cred = mocker.patch(
        "nhp.aci.status.model_run_status.DefaultAzureCredential", return_value="credential"
    )
    m_config = mocker.patch(
        "nhp.aci.status.model_run_status.Config.create_from_envvars", return_value=config
    )

    m_gpa = mocker.patch(
        "nhp.aci.status.model_run_status._get_progress_from_ats",
        return_value={
            "complete": {"inpatients": 100, "outpatients": 50, "aae": 0},
            "model_runs": 100,
            "container_group_name": "name",
        },
    )
    m_gas = mocker.patch(
        "nhp.aci.status.model_run_status._get_aci_status", return_value={"state": "running"}
    )

    # act
    actual = get_model_run_status("dataset", "id", "credential", config)  # ty: ignore[invalid-argument-type]

    # assert
    assert actual == {
        "complete": {"inpatients": 100, "outpatients": 50, "aae": 0},
        "model_runs": 100,
        "state": "running",
    }
    m_gpa.assert_called_once_with("dataset", "id", "credential", config)
    m_gas.assert_called_once_with("name", "credential", config)

    m_cred.assert_not_called()
    m_config.assert_not_called()


def test_get_model_run_status_creates_credential_and_config_if_none(mocker, config):
    # arrange
    m_cred = mocker.patch(
        "nhp.aci.status.model_run_status.DefaultAzureCredential", return_value="credential"
    )
    m_config = mocker.patch(
        "nhp.aci.status.model_run_status.Config.create_from_envvars", return_value=config
    )

    m_gpa = mocker.patch(
        "nhp.aci.status.model_run_status._get_progress_from_ats",
        return_value={
            "complete": {"inpatients": 100, "outpatients": 50, "aae": 0},
            "model_runs": 100,
            "container_group_name": "name",
        },
    )
    m_gas = mocker.patch(
        "nhp.aci.status.model_run_status._get_aci_status", return_value={"state": "running"}
    )

    # act
    actual = get_model_run_status("dataset", "id")

    # assert
    assert actual == {
        "complete": {"inpatients": 100, "outpatients": 50, "aae": 0},
        "model_runs": 100,
        "state": "running",
    }
    m_gpa.assert_called_once_with("dataset", "id", "credential", config)
    m_gas.assert_called_once_with("name", "credential", config)

    m_cred.assert_called_once_with()
    m_config.assert_called_once_with()


def test_get_model_run_status_resource_not_found_with_status(mocker, config):
    # arrange
    mocker.patch(
        "nhp.aci.status.model_run_status._get_progress_from_ats",
        return_value={
            "complete": {"inpatients": 100, "outpatients": 50, "aae": 0},
            "model_runs": 100,
            "container_group_name": "name",
        },
    )
    mocker.patch(
        "nhp.aci.status.model_run_status._get_aci_status",
        side_effect=ResourceNotFoundError("Not Found"),
    )

    # act
    actual = get_model_run_status(
        "dataset",
        "id",
        "credential",  # ty: ignore[invalid-argument-type]
        config,
    )

    # assert
    assert actual == {
        "complete": {"inpatients": 100, "outpatients": 50, "aae": 0},
        "model_runs": 100,
        "state": "Creating",
    }


def test_get_model_run_status_resource_not_found_without_status(mocker, config):
    # arrange
    mocker.patch(
        "nhp.aci.status.model_run_status._get_progress_from_ats",
        return_value={},
    )
    mocker.patch(
        "nhp.aci.status.model_run_status._get_aci_status",
        side_effect=ResourceNotFoundError("Not Found"),
    )

    # act
    actual = get_model_run_status(
        "dataset",
        "id",
        "credential",  # ty: ignore[invalid-argument-type]
        config,
    )

    # assert
    assert actual is None


def test_get_model_run_status_returns_progress_without_aci_when_no_container_group_name(
    mocker, config
):
    # arrange
    m_gas = mocker.patch("nhp.aci.status.model_run_status._get_aci_status")
    mocker.patch(
        "nhp.aci.status.model_run_status._get_progress_from_ats",
        return_value={
            "complete": {"inpatients": 100, "outpatients": 50, "aae": 0},
            "model_runs": 100,
            "container_group_name": None,
            "status": "complete",
        },
    )

    # act
    actual = get_model_run_status(
        "dataset",
        "id",
        "credential",  # ty: ignore[invalid-argument-type]
        config,
    )

    # assert
    assert actual == {
        "complete": {"inpatients": 100, "outpatients": 50, "aae": 0},
        "model_runs": 100,
        "status": "complete",
    }
    m_gas.assert_not_called()
