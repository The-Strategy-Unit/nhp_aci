"""Configuration values."""

import os
from dataclasses import dataclass

import dotenv


@dataclass
class Config:
    """Configuration class for managing NHP model runs."""

    storage_account: str
    subscription_id: str
    container_image: str
    azure_location: str
    subnet_name: str
    subnet_id: str
    user_assigned_identity: str
    container_memory: float
    container_cpu: int
    auto_delete_completed_containers: bool
    resource_group: str
    log_analytics_workspace_id: str
    log_analytics_workspace_key: str
    log_analytics_workspace_resource_id: str

    @staticmethod
    def create_from_envvars():
        """Create a Config from environment variables."""
        dotenv.load_dotenv()

        container_memory = float(os.environ["CONTAINER_MEMORY"])
        container_cpu = int(os.environ["CONTAINER_CPU"])

        match os.environ["AUTO_DELETE_COMPLETED_CONTAINERS"]:
            case "True":
                auto_delete_completed_containers = True
            case "False":
                auto_delete_completed_containers = False
            case _:
                raise ValueError("AUTO_DELETE_COMPLETED_CONTAINERS must be True or False")

        return Config(
            storage_account=os.environ["STORAGE_ACCOUNT"],
            subscription_id=os.environ["SUBSCRIPTION_ID"],
            container_image=os.environ["CONTAINER_IMAGE"],
            azure_location=os.environ["AZURE_LOCATION"],
            subnet_name=os.environ["SUBNET_NAME"],
            subnet_id=os.environ["SUBNET_ID"],
            user_assigned_identity=os.environ["USER_ASSIGNED_IDENTITY"],
            container_memory=container_memory,
            container_cpu=container_cpu,
            auto_delete_completed_containers=auto_delete_completed_containers,
            resource_group=os.environ["RESOURCE_GROUP"],
            log_analytics_workspace_id=os.environ["LOG_ANALYTICS_WORKSPACE_ID"],
            log_analytics_workspace_key=os.environ["LOG_ANALYTICS_WORKSPACE_KEY"],
            log_analytics_workspace_resource_id=os.environ["LOG_ANALYTICS_WORKSPACE_RESOURCE_ID"],
        )

    @property
    def blob_storage_endpoint(self) -> str:
        """Creates the blob storage endpoint from the storage account."""
        return f"https://{self.storage_account}.blob.core.windows.net"

    @property
    def table_storage_endpoint(self) -> str:
        """Creates the table storage endpoint from the storage account."""
        return f"https://{self.storage_account}.table.core.windows.net"
