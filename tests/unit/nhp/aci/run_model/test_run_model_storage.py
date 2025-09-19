"""Test the storage module in the nhp.aci.run_model package."""

from azure.core.exceptions import ResourceExistsError

from nhp.aci.run_model.storage import upload_params_to_blob


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
    upload_params_to_blob("params", metadata, "credential", config)  # type: ignore

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
    upload_params_to_blob("params", metadata, "credential", config)  # type: ignore

    # assert
    assert len(caplog.records) == 1
    assert caplog.records[0].levelname == "WARNING"
    assert caplog.records[0].message == "file already exists, skipping upload"
