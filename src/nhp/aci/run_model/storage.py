"""Methods for uploading model parameters to Azure Blob Storage."""

import logging
from typing import Any

from azure.core.credentials import TokenCredential
from azure.core.exceptions import ResourceExistsError
from azure.data.tables import TableClient
from azure.storage.blob import BlobServiceClient

from nhp.aci.config import Config

logger = logging.getLogger(__name__)


def upload_params_to_blob(
    params_str: str,
    metadata: dict[str, Any],
    credential: TokenCredential,
    config: Config,
) -> None:
    """Upload the parameters to Azure Blob Storage.

    Args:
        params_str (str): The parameters as a JSON string.
        metadata (dict[str, Any]): The metadata of the model run.
        credential (TokenCredential): Credential for authenticating with Azure.
        config (Config): Configuration object.
    """
    client = BlobServiceClient(config.blob_storage_endpoint, credential)
    container = client.get_container_client("queue")
    try:
        container.upload_blob(
            f"{metadata['id']}.json", params_str, metadata={k: str(v) for k, v in metadata.items()}
        )
        logger.info("params uploaded to queue")
    except ResourceExistsError:
        logger.warning("file already exists, skipping upload")


def add_table_storage_entry(
    metadata: dict[str, Any],
    model_run_id: str,
    results_viewable: bool,
    credential: TokenCredential,
    config: Config,
) -> None:
    """Add model run to table storage.

    Args:
        metadata (dict[str, Any]): The metadata for the model run.
        model_run_id (str): The model run ID.
        results_viewable (bool): Whether the results are viewable.
        credential (TokenCredential): Credential for authenticating with Azure.
        config (Config): Configuration object.
    """
    table_client = TableClient(config.table_storage_endpoint, "modelruns", credential=credential)
    entity = {
        "PartitionKey": metadata["dataset"],
        "RowKey": model_run_id,
        "status": "submitted",
        "viewable": results_viewable,
        **metadata,
    }
    table_client.create_entity(entity)
