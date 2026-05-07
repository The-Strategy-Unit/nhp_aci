"""Create a model run in Azure Container Instances."""

import logging
import uuid
from typing import Any

from azure.core.credentials import TokenCredential
from azure.identity import DefaultAzureCredential

from nhp.aci.config import Config
from nhp.aci.run_model.aci import create_and_start_container
from nhp.aci.run_model.helpers import prepare_params
from nhp.aci.run_model.storage import add_table_storage_entry, upload_params_to_blob

logger = logging.getLogger(__name__)


def create_model_run(
    params: dict[str, Any],
    app_version: str,
    save_full_model_results: bool = False,
    results_viewable: bool = False,
    timeout: str = "60m",
    credential: TokenCredential | None = None,
    config: Config | None = None,
) -> dict[str, Any]:
    """Create a model run.

    Args:
        params (dict[str, Any]): The parameters for the model run.
        app_version (str): Which version of the model to run.
        save_full_model_results (bool, optional): Whether to save full model results, defaults to
            False
        results_viewable (bool, optional): Whether the results are viewable, defaults to False
        timeout (str, optional): The timeout for the container, defaults to "60m"
        credential (TokenCredential, optional): Credential for authenticating with Azure,
            defaults to None, and calls DefaultAzureCredential()
        config (Config, optional): Configuration object, defaults to  None, and calls
            Config.create_from_envvars()

    Returns:
        dict[str, Any]: A dictionary with metadata for the model run.
    """
    # 0. set default argument values
    if credential is None:
        credential = DefaultAzureCredential()
    if config is None:
        config = Config.create_from_envvars()
    # 1. prepare params and metadata
    params_str, metadata = prepare_params(params, app_version)
    model_run_id = str(uuid.uuid4())

    logger.info(
        "received request for model run %s (%s) from user %s [id=%s]",
        metadata["id"],
        metadata["app_version"],
        metadata["user"],
        model_run_id,
    )

    # 2. upload params to blob storage
    upload_params_to_blob(params_str, metadata, credential, config)

    # 3. add entry in table storage
    add_table_storage_entry(metadata, model_run_id, results_viewable, credential, config)

    # 4. create a new container instance
    create_and_start_container(
        metadata, model_run_id, save_full_model_results, timeout, credential, config
    )

    return metadata
