# NHP ACI helpers

Methods to start and run the [`nhp_model`](https://github.com/the-strategy-unit/nhp_model) docker containers in Azure Container Instances (ACI).

This is predominantly an internal tool designed to help us manage our internal infrastructure.

## Methods

### `nhp.aci.run_model.create_model_run`

Takes the parameters that you want to run the model with, and what version of the model to run, then starts running the model in ACI.

Returns a dictionary containing the metadata of the model run, including the `id` of the model run that has just been created.

### `nhp.aci.status.get_current_model_runs`

Gets the states of all of the currently running ACI container groups running.

If `AUTO_DELETE_COMPLETED_CONTAINERS` env var is set, then it will delete any ACI container instance that has successfully terminated.

### `nhp.aci.status.get_model_run_status`

Gets the state of a specific ACI container group.

If `AUTO_DELETE_COMPLETED_CONTAINERS` env var is set, then it will delete any ACI container instance that has successfully terminated.

## Set-up

In order to run this locally, you will need to install the [Azure CLI](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli?view=azure-cli-latest).
Once you have installed that, you will then need to [sign in](https://learn.microsoft.com/en-us/cli/azure/authenticate-azure-cli-interactively?view=azure-cli-latest).

The easiest way to get started is to use [uv](https://docs.astral.sh/uv/).
Create a new virtual environment (`uv venv --python 3.12`), then install dependencies with (`uv pip install -e ".[dev]"`).

You will then need to create a `.env` file. There is a sample file (`.env.sample`) which you can use as a template.
Speak to colleagues to get the correct values.