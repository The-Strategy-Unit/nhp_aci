"""Test for the __init__ module in the nhp.aci.run_model package."""

from nhp.aci.run_model import create_model_run


def test_create_model_run(mocker):
    # arrange
    metadata = {"id": "id", "app_version": "app_version", "user": "user"}
    m_prepare_params = mocker.patch(
        "nhp.aci.run_model.prepare_params", return_value=("params_str", metadata)
    )
    m_upload_params_to_blob = mocker.patch("nhp.aci.run_model.upload_params_to_blob")
    m_add_table_storage_entry = mocker.patch("nhp.aci.run_model.add_table_storage_entry")
    m_create_and_start_container = mocker.patch("nhp.aci.run_model.create_and_start_container")
    m_uuid4 = mocker.patch("nhp.aci.run_model.uuid.uuid4", return_value="model-run-id")

    m_cred = mocker.patch("nhp.aci.run_model.DefaultAzureCredential", return_value="credential")
    m_config = mocker.patch("nhp.aci.run_model.Config.create_from_envvars", return_value="config")

    # act
    actual = create_model_run(
        "params",  # ty: ignore[invalid-argument-type]
        "v1.0",
        save_full_model_results=True,
        results_viewable=True,
        timeout="30m",
        credential="credential",  # ty: ignore[invalid-argument-type]
        config="config",  # ty: ignore[invalid-argument-type]
    )

    # assert
    assert actual == metadata
    m_prepare_params.assert_called_once_with("params", "v1.0")
    m_upload_params_to_blob.assert_called_once_with("params_str", metadata, "credential", "config")
    m_add_table_storage_entry.assert_called_once_with(
        metadata,
        "model-run-id",
        True,
        "credential",
        "config",
    )
    m_create_and_start_container.assert_called_once_with(
        metadata,
        "model-run-id",
        True,
        "30m",
        "credential",
        "config",
    )
    m_uuid4.assert_called_once_with()
    m_cred.assert_not_called()
    m_config.assert_not_called()


def test_create_model_run_creates_credential_and_config_if_none(mocker):
    # arrange
    metadata = {"id": "id", "app_version": "app_version", "user": "user"}
    m_prepare_params = mocker.patch(
        "nhp.aci.run_model.prepare_params", return_value=("params_str", metadata)
    )
    m_upload_params_to_blob = mocker.patch("nhp.aci.run_model.upload_params_to_blob")
    m_add_table_storage_entry = mocker.patch("nhp.aci.run_model.add_table_storage_entry")
    m_create_and_start_container = mocker.patch("nhp.aci.run_model.create_and_start_container")
    m_uuid4 = mocker.patch("nhp.aci.run_model.uuid.uuid4", return_value="model-run-id")

    m_cred = mocker.patch("nhp.aci.run_model.DefaultAzureCredential", return_value="credential")
    m_config = mocker.patch("nhp.aci.run_model.Config.create_from_envvars", return_value="config")

    # act
    actual = create_model_run(
        "params",  # ty: ignore[invalid-argument-type]
        "v1.0",
        save_full_model_results=True,
        results_viewable=True,
        timeout="30m",
    )

    # assert
    assert actual == metadata
    m_prepare_params.assert_called_once_with("params", "v1.0")
    m_upload_params_to_blob.assert_called_once_with("params_str", metadata, "credential", "config")
    m_add_table_storage_entry.assert_called_once_with(
        metadata,
        "model-run-id",
        True,
        "credential",
        "config",
    )
    m_create_and_start_container.assert_called_once_with(
        metadata,
        "model-run-id",
        True,
        "30m",
        "credential",
        "config",
    )
    m_uuid4.assert_called_once_with()
    m_cred.assert_called_once_with()
    m_config.assert_called_once_with()
