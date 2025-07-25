"""Test the storage module in the nhp.aci.run_model package."""

from azure.core.exceptions import ResourceExistsError

from nhp.aci.run_model.storage import upload_params_to_blob


def test_upload_params_to_blob(mocker, config):
    # arrange
    m_l_i = mocker.patch("logging.info")
    m_l_w = mocker.patch("logging.warning")

    m_bsc = mocker.patch("nhp.aci.run_model.storage.BlobServiceClient")
    m_gcc = m_bsc().get_container_client
    m_ulb = m_gcc().upload_blob
    m_bsc.reset_mock()
    m_gcc.reset_mock()

    metadata = {"id": "a"}

    # act
    upload_params_to_blob("params", metadata, "credential", config)  # type: ignore

    # assert
    m_bsc.assert_called_once_with("https://storage_account.blob.core.windows.net", "credential")
    m_gcc.assert_called_once_with("queue")
    m_ulb.assert_called_once_with("a.json", "params", metadata=metadata)
    m_l_i.assert_called_once_with("params uploaded to queue")
    m_l_w.assert_not_called()


def test_upload_params_to_blob_already_exists(mocker, config):
    # arrange
    m_l_i = mocker.patch("logging.info")
    m_l_w = mocker.patch("logging.warning")

    m_bsc = mocker.patch("nhp.aci.run_model.storage.BlobServiceClient")
    m_gcc = m_bsc().get_container_client
    m_ulb = m_gcc().upload_blob
    m_ulb.side_effect = ResourceExistsError("Blob already exists")
    m_bsc.reset_mock()
    m_gcc.reset_mock()

    metadata = {"id": "a"}

    # act
    upload_params_to_blob("params", metadata, "credential", config)  # type: ignore

    # assert
    m_l_i.assert_not_called()
    m_l_w.assert_called_once_with("file already exists, skipping upload")
