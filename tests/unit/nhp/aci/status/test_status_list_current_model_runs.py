"""Test the list_current_model_runs module in the nhp.aci.status package."""

from unittest.mock import Mock, call

from nhp.aci.status.list_current_model_runs import get_current_model_runs


def test_get_current_model_runs(mocker, config):
    # arrange
    m_cimc = mocker.patch(
        "nhp.aci.status.list_current_model_runs.ContainerInstanceManagementClient"
    )

    m_gcgis = mocker.patch(
        "nhp.aci.status.list_current_model_runs.get_container_group_instance_state",
        return_value="state",
    )

    ma = Mock()
    ma.name = "a"
    mb = Mock()
    mb.name = "b"

    m_lbyg = m_cimc().container_groups.list_by_resource_group
    m_lbyg.return_value = [ma, mb]
    m_cimc.reset_mock()

    # act
    actual = get_current_model_runs("credential", config)  # type: ignore

    # assert
    assert actual == {"a": "state", "b": "state"}

    m_cimc.assert_called_once_with("credential", "subscription_id")
    m_lbyg.assert_called_once_with("resource_group")
    assert m_gcgis.call_args_list == [
        call("a", m_cimc(), "resource_group", config),
        call("b", m_cimc(), "resource_group", config),
    ]
