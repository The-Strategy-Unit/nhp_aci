"""Test the helpers module in the nhp.aci.status package."""

from unittest.mock import Mock

from nhp.aci.status.helpers import get_container_group_current_state


def test_get_container_group_current_state_not_complete(config):
    # arrange
    m1 = Mock()
    m2 = Mock()
    m1.container_groups.get().containers = [m2]
    m1.container_groups.get.reset_mock()

    m2.instance_view.current_state.as_dict.return_value = "current_state"

    # act
    actual = get_container_group_current_state("name", m1, "resource_group", config)

    # assert
    assert actual == "current_state"

    m1.container_groups.get.assert_called_once_with("resource_group", "name")
    m1.container_groups.begin_delete.assert_not_called()


def test_get_container_group_current_state_not_started_1(config):
    # arrange
    m1 = Mock()
    m2 = Mock()
    m1.container_groups.get().containers = [m2]
    m1.container_groups.get.reset_mock()

    m2.instance_view = None

    # act
    actual = get_container_group_current_state("name", m1, "resource_group", config)

    # assert
    assert actual == {}


def test_get_container_group_current_state_not_started_2(config):
    # arrange
    m1 = Mock()
    m2 = Mock()
    m1.container_groups.get().containers = [m2]
    m1.container_groups.get.reset_mock()

    m2.instance_view.current_state = None

    # act
    actual = get_container_group_current_state("name", m1, "resource_group", config)

    # assert
    assert actual == {}


def test_get_container_group_current_state_complete_and_delete(config):
    # arrange
    m1 = Mock()
    m2 = Mock()
    m1.container_groups.get().containers = [m2]
    m1.container_groups.get.reset_mock()

    m2.instance_view.current_state.as_dict.return_value = "current_state"
    m2.instance_view.current_state.state = "Terminated"
    m2.instance_view.current_state.detail_status = "Completed"

    config.auto_delete_completed_containers = True

    # act
    get_container_group_current_state("name", m1, "resource_group", config)

    # assert
    m1.container_groups.get.assert_called_once_with("resource_group", "name")
    m1.container_groups.begin_delete.assert_called_once_with("resource_group", "name")


def test_get_container_group_current_state_complete_dont_delete(config):
    # arrange
    m1 = Mock()
    m2 = Mock()
    m1.container_groups.get().containers = [m2]
    m1.container_groups.get.reset_mock()

    m2.instance_view.current_state.as_dict.return_value = "current_state"
    m2.instance_view.current_state.state = "Terminated"
    m2.instance_view.current_state.detail_status = "Completed"

    config.auto_delete_completed_containers = False

    # act
    get_container_group_current_state("name", m1, "resource_group", config)

    # assert
    m1.container_groups.get.assert_called_once_with("resource_group", "name")
    m2.container_groups.begin_delete.assert_not_called()
