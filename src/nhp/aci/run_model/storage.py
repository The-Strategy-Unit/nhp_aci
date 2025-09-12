"""Methods for uploading model parameters to Azure Blob Storage."""

import logging

from azure.core.credentials import TokenCredential
from azure.core.exceptions import ResourceExistsError
from azure.storage.blob import BlobServiceClient

from nhp.aci.config import Config


def upload_params_to_blob(
    params_str: str,
    metadata: dict,
    credential: TokenCredential,
    config: Config,
) -> None:
    """Upload the parameters to Azure Blob Storage.

    :param params_str: The parameters as a JSON string.
    :type params_str: str
    :param metadata: The metadata of the model run.
    :type metadata: dict
    :param credential: Credential for authenticating with Azure
    :type credential: TokenCredential, optional
    :param config: Configuration object, defaults to creating from envvars
    :type config: Config, optional
    """
    client = BlobServiceClient(config.storage_endpoint, credential)
    container = client.get_container_client("queue")
    try:
        container.upload_blob(f"{metadata['id']}.json", params_str, metadata=metadata)
        logging.info("params uploaded to queue")
    except ResourceExistsError:
        logging.warning("file already exists, skipping upload")
