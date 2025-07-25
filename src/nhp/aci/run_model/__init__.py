"""Create a model run in Azure Container Instances."""

import logging

from azure.core.credentials import TokenCredential
from azure.identity import DefaultAzureCredential

from nhp.aci.config import Config
from nhp.aci.run_model.aci import create_and_start_container
from nhp.aci.run_model.helpers import prepare_params
from nhp.aci.run_model.storage import upload_params_to_blob


def create_model_run(
    params: dict,
    app_version: str,
    save_full_model_results: bool = False,
    credential: TokenCredential = DefaultAzureCredential(),
    config=Config.create_from_envvars(),
) -> dict:
    """Create a model run.

    :param params: The parameters for the model run.
    :type params: dict
    :param app_version: Which version of the model to run.
    :type app_version: str
    :param save_full_model_results: Whether to save full model results, defaults to False
    :type save_full_model_results: bool, optional
    :param credential: Credential for authenticating with Azure,
        defaults to DefaultAzureCredential()
    :type credential: TokenCredential, optional
    :param config: Configuration object, defaults to creating from envvars
    :type config: Config, optional
    :return: A dictionary with metadata for the model run.
    :rtype: dict
    """
    # 1. prepare params and metadata
    params_str, metadata = prepare_params(params, app_version)

    logging.info(
        "received request for model run %s (%s)",
        metadata["id"],
        metadata["app_version"],
    )

    # 2. upload params to blob storage
    upload_params_to_blob(params_str, metadata, credential, config)

    # 3. create a new container instance
    create_and_start_container(metadata, save_full_model_results, credential, config)

    return metadata
