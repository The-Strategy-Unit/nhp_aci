from unittest.mock import Mock

from azure.core.exceptions import ResourceNotFoundError

from nhp.aci.clean_up import _delete_blob_in_queue, _delete_container_group, clean_up_model_run


def test_delete_blob_in_queue(mocker):
    # arrange
    m = mocker.patch("nhp.aci.clean_up.BlobServiceClient")

    print_mock = mocker.patch("builtins.print")

    config = Mock()
    config.storage_endpoint = "ep"

    # act
    _delete_blob_in_queue("id", "credential", config)  # type: ignore

    # assert
    m.assert_called_once_with("ep", "credential")
    m().get_container_client.assert_called_once_with("queue")
    m().get_container_client().delete_blob.assert_called_once_with("id.json")
    print_mock.assert_called_once_with("Successfully deleted id.json from queue")


def test_delete_blob_in_queue_not_found(mocker):
    # arrange
    m = mocker.patch("nhp.aci.clean_up.BlobServiceClient")
    m().get_container_client().delete_blob.side_effect = ResourceNotFoundError()
    m.reset_mock()

    print_mock = mocker.patch("builtins.print")

    config = Mock()
    config.storage_endpoint = "ep"

    # act
    _delete_blob_in_queue("id", "credential", config)  # type: ignore

    # assert
    m.assert_called_once_with("ep", "credential")
    m().get_container_client.assert_called_once_with("queue")
    m().get_container_client().delete_blob.assert_called_once_with("id.json")
    print_mock.assert_called_once_with("id.json does not exist, potentially already removed")


def test_delete_container_group(mocker):
    # arrange
    m = mocker.patch("nhp.aci.clean_up.ContainerInstanceManagementClient")

    print_mock = mocker.patch("builtins.print")

    config = Mock()
    config.resource_group = "resource_group"
    config.subscription_id = "subscription_id"

    # act
    _delete_container_group("id", "credential", config)  # type: ignore

    # assert
    m.assert_called_once_with("credential", "subscription_id")
    m().container_groups.begin_delete.assert_called_once_with("resource_group", "id")
    print_mock.assert_called_once_with("Successfully deleted container group id")


def test_delete_container_group_not_found(mocker):
    # arrange
    m = mocker.patch("nhp.aci.clean_up.ContainerInstanceManagementClient")
    m().container_groups.begin_delete.side_effect = ResourceNotFoundError()
    m.reset_mock()

    print_mock = mocker.patch("builtins.print")

    config = Mock()
    config.resource_group = "resource_group"
    config.subscription_id = "subscription_id"

    # act
    _delete_container_group("id", "credential", config)  # type: ignore

    # assert
    m.assert_called_once_with("credential", "subscription_id")
    m().container_groups.begin_delete.assert_called_once_with("resource_group", "id")
    print_mock.assert_called_once_with("id does not exist, potentially already removed")


def test_clean_up_model_run(mocker):
    # arrange
    m1 = mocker.patch("nhp.aci.clean_up._delete_blob_in_queue")
    m2 = mocker.patch("nhp.aci.clean_up._delete_container_group")

    # act
    clean_up_model_run("id", "credential", "config")  # type: ignore

    # assert
    m1.assert_called_once_with("id", "credential", "config")
    m2.assert_called_once_with("id", "credential", "config")
