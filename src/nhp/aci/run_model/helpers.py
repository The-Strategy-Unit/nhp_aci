"""Model run helpers."""

import json
import logging
import re
import zlib
from datetime import datetime, timezone

import requests
from jsonschema import validate


def generate_id(params: str, metadata: dict) -> str:
    """Generate an ID for the model run.

    Uses the dataset and the scenario, and a CRC32 hash of the parameters to generate an ID for the
    model run.

    :param params: the parameters (as a JSON string) for the model run
    :type params: str
    :param metadata: the metadata for the model run
    :type metadata: dict
    :return: an ID for the model run
    :rtype: str
    """
    crc32 = f"{zlib.crc32(params.encode('utf-8')):x}"
    scenario_sanitized = re.sub("[^a-z0-9]+", "-", metadata["scenario"])
    # id needs to be of length 1-63, but the last 9 characters are a - and the hash
    return (f"{metadata['dataset']}-{scenario_sanitized}"[0:54] + "-" + crc32).lower()


def get_metadata(params: dict) -> dict:
    """Extract metadata from the parameters dictionary.

    :param params: the parameters dictionary
    :type params: dict
    :return: a dictionary with metadata extracted from the parameters
    :rtype: dict
    """
    metadata = {
        k: str(v) for k, v in params.items() if not isinstance(v, dict) and not isinstance(v, list)
    }

    return metadata


def prepare_params(params: dict, app_version: str) -> tuple[str, dict]:
    """Prepare the parameters for the model run.

    :param params: The parameters for the model run.
    :type params: dict
    :param app_version: Which version of the model to run.
    :type app_version: str
    :return: The parameters as a JSON string and the metadata dictionary.
    :rtype: tuple[str, dict]
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


def validate_params(params: dict, app_version: str) -> None:
    """Validate the parameters against the schema for the given app version.

    :param params: The parameters to validate
    :type params: dict
    :param app_version: the version of the model to validate against
    :type app_version: str
    """
    uri = f"https://the-strategy-unit.github.io/nhp_model/{app_version}/params-schema.json"
    req = requests.get(uri)
    if req.status_code != 200:  # noqa: PLR2004
        logging.warning("Unable to validate schema for app_version %s", app_version)
        return
    schema = req.json()
    validate(params, schema)
