"""Model run helpers."""

import json
import logging
import re
import zlib
from datetime import datetime, timezone
from typing import Any

import requests
from jsonschema import validate

logger = logging.getLogger(__name__)


def generate_id(params: str, metadata: dict[str, Any]) -> str:
    """Generate an ID for the model run.

    Uses the dataset and the scenario, and a CRC32 hash of the parameters to generate an ID for the
    model run.

    Args:
        params (str): The parameters (as a JSON string) for the model run.
        metadata (dict[str, Any]): The metadata for the model run.

    Returns:
        str: An ID for the model run.
    """
    crc32 = f"{zlib.crc32(params.encode('utf-8')):x}"
    scenario_sanitized = re.sub("[^a-z0-9]+", "-", metadata["scenario"])
    # id needs to be of length 1-63, but the last 9 characters are a - and the hash
    return (f"{metadata['dataset']}-{scenario_sanitized}"[0:54] + "-" + crc32).lower()


def get_metadata(params: dict[str, Any]) -> dict[str, Any]:
    """Extract metadata from the parameters dictionary.

    Args:
        params (dict[str, Any]): The parameters dictionary.

    Returns:
        dict[str, Any]: A dictionary with metadata extracted from the parameters.
    """
    return {k: v for k, v in params.items() if not isinstance(v, dict) and not isinstance(v, list)}


def prepare_params(params: dict[str, Any], app_version: str) -> tuple[str, dict[str, Any]]:
    """Prepare the parameters for the model run.

    Args:
        params (dict[str, Any]): The parameters for the model run.
        app_version (str): Which version of the model to run.

    Returns:
        tuple[str, dict[str, Any]]: The parameters as a JSON string and the metadata dictionary.
    """
    # check that the params are valid according to the schema
    validate_params(params, app_version)

    # the id paramerter used to be submitted, but is now generated here to prevent issues with the
    # containers being created with invalid ids.
    if "id" in params:
        params.pop("id")
    # force the create_datetime to be the current time, do not accept values from the user
    params["create_datetime"] = f"{datetime.now(timezone.utc):%Y%m%d_%H%M%S}"

    # get the metadata from the params
    metadata = get_metadata(params)
    # set the app_version in the params and metadata
    params["app_version"] = metadata["app_version"] = app_version

    # convert params to a JSON string
    params_str = json.dumps(params)
    # generate the id based on the params and metadata
    metadata["id"] = generate_id(params_str, metadata)

    return params_str, metadata


def validate_params(params: dict[str, Any], app_version: str) -> None:
    """Validate the parameters against the schema for the given app version.

    Args:
        params (dict[str, Any]): The parameters to validate.
        app_version (str): The version of the model to validate against.
    """
    uri = f"https://the-strategy-unit.github.io/nhp_model/{app_version}/params-schema.json"
    req = requests.get(uri)
    if req.status_code != 200:  # noqa: PLR2004
        logger.warning("Unable to validate schema for app_version %s", app_version)
        return
    schema = req.json()
    validate(params, schema)
