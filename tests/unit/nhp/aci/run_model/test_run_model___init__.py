"""Test for the __init__ module in the nhp.aci.run_model package."""

from nhp.aci.run_model import create_model_run


def test_create_model_run(mocker):
    # arrange
    metadata = {"id": "id", "app_version": "app_version"}
    m_prepare_params = mocker.patch(
        "nhp.aci.run_model.prepare_params", return_value=("params_str", metadata)
    )
    m_upload_params_to_blob = mocker.patch("nhp.aci.run_model.upload_params_to_blob")
    m_create_and_start_container = mocker.patch("nhp.aci.run_model.create_and_start_container")

    # act
    actual = create_model_run("params", "v1.0", True, "30m", "credential", "config")  # type: ignore

    # assert
    assert actual == metadata
    m_prepare_params.assert_called_once_with("params", "v1.0")
    m_upload_params_to_blob.assert_called_once_with("params_str", metadata, "credential", "config")
    m_create_and_start_container.assert_called_once_with(
        metadata, True, "30m", "credential", "config"
    )
