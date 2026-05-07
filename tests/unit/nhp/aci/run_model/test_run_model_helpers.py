"""Test the helpers module in the nhp.aci.run_model package."""

from datetime import datetime

import pytest

from nhp.aci.run_model.helpers import generate_id, get_metadata, prepare_params, validate_params


def test_generate_id():
    # arrange
    params = '{"param1": "value1", "param2": "value2"}'
    metadata = {"dataset": "dataset1", "scenario": "scenario1"}

    # act
    actual = generate_id(params, metadata)

    # assert
    assert actual == "dataset1-scenario1-fa571aea"


def test_get_metadata():
    # arrange
    params = {
        "param1": "value1",
        "param2": 42,
        "param3": {"nested": "value"},
        "param4": ["list", "of", "values"],
    }

    # act
    actual = get_metadata(params)

    # assert
    assert actual == {"param1": "value1", "param2": 42}


@pytest.mark.parametrize("params_with_id", [True, False])
def test_prepare_params(mocker, params_with_id):
    # arrange
    params = {"param1": "value1", "param2": 42, "create_datetime": "20231001_120000"}
    if params_with_id:
        params["id"] = "id"
    app_version = "v1.0"
    m_validate_params = mocker.patch("nhp.aci.run_model.helpers.validate_params")
    m_get_metadata = mocker.patch(
        "nhp.aci.run_model.helpers.get_metadata", return_value={"param1": "value1", "param2": 42}
    )
    m_datetime = mocker.patch("nhp.aci.run_model.helpers.datetime")
    m_datetime.now.return_value = datetime(2025, 1, 2, 3, 4, 5)
    m_generate_id = mocker.patch(
        "nhp.aci.run_model.helpers.generate_id", return_value="generated_id"
    )
    expected_params_str = '{"param1": "value1", "param2": 42, "create_datetime": "20250102_030405", "app_version": "v1.0"}'  # noqa: E501

    # act
    actual_params, actual_metadata = prepare_params(params, app_version)

    # assert
    assert actual_params == expected_params_str
    assert actual_metadata == {
        "param1": "value1",
        "param2": 42,
        "app_version": "v1.0",
        "id": "generated_id",
    }
    m_validate_params.assert_called_once_with(params, app_version)

    m_get_metadata.assert_called_once_with(
        {
            "param1": "value1",
            "param2": 42,
            "create_datetime": "20250102_030405",
            "app_version": "v1.0",
        }
    )
    m_generate_id.assert_called_once()


def test_validate_params(mocker):
    # arrange
    m_get = mocker.patch("requests.get")
    m_validate = mocker.patch("nhp.aci.run_model.helpers.validate")

    m_get().status_code = 200
    m_get().json.return_value = "schema"
    m_get.reset_mock()

    # act
    validate_params("params", "dev")  # type: ignore

    # assert
    m_get.assert_called_once_with(
        "https://the-strategy-unit.github.io/nhp_model/dev/params-schema.json"
    )

    m_validate.assert_called_once_with("params", "schema")


def test_validate_params_no_schema(mocker):
    # arrange
    m_get = mocker.patch("requests.get")
    m_validate = mocker.patch("nhp.aci.run_model.helpers.validate")

    m_get().status_code = 404
    m_get.reset_mock()

    # act
    validate_params("params", "dev")  # type: ignore

    # assert
    m_validate.assert_not_called()
