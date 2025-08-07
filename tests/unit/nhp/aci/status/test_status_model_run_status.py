"""Test the model_run_status module in the nhp.aci.status package."""

from azure.core.exceptions import ResourceNotFoundError

from nhp.aci.status.model_run_status import (
    _get_aci_status,
    _get_queue_metadata,
    get_model_run_status,
)


def test__get_queue_metadata(mocker, config):
    # arrange
    m_bsc = mocker.patch("nhp.aci.status.model_run_status.BlobServiceClient")
    m_cc = m_bsc().get_container_client
    m_bc = m_cc().get_blob_client

    m_bc().exists.return_value = True
    m_bc().get_blob_properties.return_value = {
        "metadata": {"model_runs": "100", "Inpatients": "100", "Outpatients": "50", "AaE": "0"}
    }
    m_bsc.reset_mock()

    # act
    actual = _get_queue_metadata("name", "credential", config)  # type: ignore

    # assert
    assert actual == {
        "complete": {"inpatients": 100, "outpatients": 50, "aae": 0},
        "model_runs": 100,
    }

    m_bsc.assert_called_once_with("https://storage_account.blob.core.windows.net", "credential")
    m_cc.assert_called_once_with("queue")
    m_bc.assert_called_once_with("name.json")


def test__get_queue_metadata_blob_missing(mocker, config):
    # arrange
    m_bsc = mocker.patch("nhp.aci.status.model_run_status.BlobServiceClient")
    m_cc = m_bsc().get_container_client
    m_bc = m_cc().get_blob_client

    m_bc().exists.return_value = False
    m_bsc.reset_mock()

    # act
    actual = _get_queue_metadata("name", "credential", config)  # type: ignore

    # assert
    assert actual == {}


def test__get_queue_metadata_metadata_progress_missing(mocker, config):
    # arrange
    m_bsc = mocker.patch("nhp.aci.status.model_run_status.BlobServiceClient")
    m_cc = m_bsc().get_container_client
    m_bc = m_cc().get_blob_client

    m_bc().exists.return_value = True
    m_bc().get_blob_properties.return_value = {"metadata": {"model_runs": "100"}}
    m_bsc.reset_mock()

    # act
    actual = _get_queue_metadata("name", "credential", config)  # type: ignore

    # assert
    assert actual == {
        "complete": {"inpatients": 0, "outpatients": 0, "aae": 0},
        "model_runs": 100,
    }


def test__get_aci_status(mocker, config):
    # arrange
    m_cimc = mocker.patch("nhp.aci.status.model_run_status.ContainerInstanceManagementClient")
    m_gcgis = mocker.patch(
        "nhp.aci.status.model_run_status.get_container_group_current_state", return_value="state"
    )

    # act
    actual = _get_aci_status("name", "credential", config)  # type: ignore

    # assert
    assert actual == "state"
    m_cimc.assert_called_once_with("credential", "subscription_id")
    m_gcgis.assert_called_once_with("name", m_cimc(), "resource_group")


def test_get_model_run_status(mocker, config):
    # arrange
    m_gqm = mocker.patch(
        "nhp.aci.status.model_run_status._get_queue_metadata",
        return_value={
            "complete": {"inpatients": 100, "outpatients": 50, "aae": 0},
            "model_runs": 100,
        },
    )
    m_gas = mocker.patch(
        "nhp.aci.status.model_run_status._get_aci_status", return_value={"state": "running"}
    )

    # act
    actual = get_model_run_status("name", "credential", config)  # type: ignore

    # assert
    assert actual == {
        "complete": {"inpatients": 100, "outpatients": 50, "aae": 0},
        "model_runs": 100,
        "state": "running",
    }
    m_gqm.assert_called_once_with("name", "credential", config)
    m_gas.assert_called_once_with("name", "credential", config)


def test_get_model_run_status_resource_not_found_with_status(mocker, config):
    # arrange
    mocker.patch(
        "nhp.aci.status.model_run_status._get_queue_metadata",
        return_value={
            "complete": {"inpatients": 100, "outpatients": 50, "aae": 0},
            "model_runs": 100,
        },
    )
    mocker.patch(
        "nhp.aci.status.model_run_status._get_aci_status",
        side_effect=ResourceNotFoundError("Not Found"),
    )

    # act
    actual = get_model_run_status("name", "credential", config)  # type: ignore

    # assert
    assert actual == {
        "complete": {"inpatients": 100, "outpatients": 50, "aae": 0},
        "model_runs": 100,
        "state": "Creating",
    }


def test_get_model_run_status_resource_not_found_without_status(mocker, config):
    # arrange
    mocker.patch(
        "nhp.aci.status.model_run_status._get_queue_metadata",
        return_value={},
    )
    mocker.patch(
        "nhp.aci.status.model_run_status._get_aci_status",
        side_effect=ResourceNotFoundError("Not Found"),
    )

    # act
    actual = get_model_run_status("name", "credential", config)  # type: ignore

    # assert
    assert actual is None
