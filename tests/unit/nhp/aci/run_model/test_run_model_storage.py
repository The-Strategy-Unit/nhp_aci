"""Test the storage module in the nhp.aci.run_model package."""

from azure.core.exceptions import ResourceExistsError

from nhp.aci.run_model.storage import add_table_storage_entry, upload_params_to_blob


def test_upload_params_to_blob(mocker, config, caplog):
    # arrange
    m_bsc = mocker.patch("nhp.aci.run_model.storage.BlobServiceClient")
    m_gcc = m_bsc().get_container_client
    m_ulb = m_gcc().upload_blob
    m_bsc.reset_mock()
    m_gcc.reset_mock()

    metadata = {"id": "a"}

    caplog.set_level("INFO")

    # act
    upload_params_to_blob("params", metadata, "credential", config)  # ty: ignore[invalid-argument-type]

    # assert
    m_bsc.assert_called_once_with("https://storage_account.blob.core.windows.net", "credential")
    m_gcc.assert_called_once_with("queue")
    m_ulb.assert_called_once_with("a.json", "params", metadata=metadata)

    assert len(caplog.records) == 1
    assert caplog.records[0].levelname == "INFO"
    assert caplog.records[0].message == "params uploaded to queue"


def test_upload_params_to_blob_already_exists(mocker, config, caplog):
    # arrange
    m_bsc = mocker.patch("nhp.aci.run_model.storage.BlobServiceClient")
    m_gcc = m_bsc().get_container_client
    m_ulb = m_gcc().upload_blob
    m_ulb.side_effect = ResourceExistsError("Blob already exists")
    m_bsc.reset_mock()
    m_gcc.reset_mock()

    metadata = {"id": "a"}

    caplog.set_level("INFO")

    # act
    upload_params_to_blob("params", metadata, "credential", config)  # ty: ignore[invalid-argument-type]

    # assert
    assert len(caplog.records) == 1
    assert caplog.records[0].levelname == "WARNING"
    assert caplog.records[0].message == "file already exists, skipping upload"


def test_upload_params_to_blob_stringifies_metadata_values(mocker, config):
    # arrange
    m_bsc = mocker.patch("nhp.aci.run_model.storage.BlobServiceClient")
    metadata = {"id": "a", "attempt": 1, "results_viewable": True}

    # act
    upload_params_to_blob("params", metadata, "credential", config)  # ty: ignore[invalid-argument-type]

    # assert
    m_bsc().get_container_client().upload_blob.assert_called_once_with(
        "a.json",
        "params",
        metadata={"id": "a", "attempt": "1", "results_viewable": "True"},
    )


def test_add_table_storage_entry(mocker, config):
    # arrange
    m_table_client = mocker.patch("nhp.aci.run_model.storage.TableClient")
    metadata = {
        "id": "id",
        "dataset": "dataset",
        "scenario": "scenario",
        "app_version": "v5.0",
        "model_run_id": "model-run-id",
    }

    # act
    add_table_storage_entry(
        metadata,
        "save_full_model_results",  # ty: ignore[invalid-argument-type]
        "viewable",  # ty: ignore[invalid-argument-type]
        "credential",  # ty: ignore[invalid-argument-type]
        config,
    )

    # assert
    m_table_client.assert_called_once_with(
        "https://storage_account.table.core.windows.net",
        "modelruns",
        credential="credential",
    )
    m_table_client().create_entity.assert_called_once_with(
        {
            "PartitionKey": "dataset",
            "RowKey": "model-run-id",
            "status": "submitted",
            "save_full_model_results": "save_full_model_results",
            "viewable": "viewable",
            **metadata,
        }
    )
