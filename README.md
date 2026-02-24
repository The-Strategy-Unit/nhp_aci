# NHP ACI helpers

Methods to start and run the [`nhp_model`](https://github.com/the-strategy-unit/nhp_model) docker containers in Azure Container Instances (ACI).

This is predominantly an internal tool designed to help us manage our internal infrastructure.

## Set-up

1. Install the [Azure CLI](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli?view=azure-cli-latest) and [sign in](https://learn.microsoft.com/en-us/cli/azure/authenticate-azure-cli-interactively?view=azure-cli-latest).
2. Use [uv](https://docs.astral.sh/uv/) to create barebones environment: `uv init --bare`. This creates a `pyproject.toml` that you can add packages to.
3. Add nhp_aci to your environment, `uv add git+https://github.com/The-Strategy-Unit/nhp_aci`. You should see nhp_aci now listed in the `pyproject.toml`
4. Create an environment using your `pyproject.toml` with `uv venv` and then activate it with `.venv\Scripts\activate`
5. To install from the `pyproject.toml`, use `uv sync`

You will then need to create a `.env` file. There is a sample file (`.env.sample`) which you can use as a template. Speak to colleagues to get the correct values.

Once you have installed nhp_aci and got a valid `.env` files, you should be able to run the following commands:

- `nhp_aci run`
- `nhp_aci status`
- `nhp_aci clean`

for each of these commands, append `-h` to see the usage.

## For developers

### Methods

#### `nhp.aci.run_model.create_model_run`

Takes the parameters that you want to run the model with, and what version of the model to run, then starts running the model in ACI.

Returns a dictionary containing the metadata of the model run, including the `id` of the model run that has just been created.

#### `nhp.aci.status.get_current_model_runs`

Gets the states of all of the currently running ACI container groups running.

If `AUTO_DELETE_COMPLETED_CONTAINERS` env var is set, then it will delete any ACI container instance that has successfully terminated.

#### `nhp.aci.status.get_model_run_status`

Gets the state of a specific ACI container group.

If `AUTO_DELETE_COMPLETED_CONTAINERS` env var is set, then it will delete any ACI container instance that has successfully terminated.

