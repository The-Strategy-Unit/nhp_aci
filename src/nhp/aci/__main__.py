"""NHP ACI CLI.

Provides command line interface tools for working with Azure Container Interfaces to run the model.
"""

import argparse
import json

from nhp.aci.clean_up import clean_up_model_run
from nhp.aci.run_model import create_model_run
from nhp.aci.status import get_current_model_runs, get_model_run_status


def _arg_parser() -> argparse.ArgumentParser:
    """Parse the command line arguments.

    :returns: an ArgumentParser object containing the parsed command line arguments.
    :rtype: argparse.ArgumentParser
    """
    parser = argparse.ArgumentParser(description="NHP Azure Container Instance CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Run model command
    run_parser = subparsers.add_parser("run", help="Start a model run in ACI")
    run_parser.add_argument("params", help="Path to model params JSON")
    run_parser.add_argument(
        "--app-version",
        required=False,
        default=None,
        help="Model version (optional, defaults to whats inside the params, or 'dev')",
    )
    run_parser.add_argument(
        "--dataset",
        required=False,
        default=None,
        help="Dataset (optional, defaults to whats inside the params)",
    )
    run_parser.add_argument(
        "--save-full-model-results", action="store_true", help="Save full model results"
    )
    run_parser.add_argument("--timeout", default="60m", help="Container timeout (default: 60m)")

    # Status command
    status_parser = subparsers.add_parser("status", help="Check container status")
    status_parser.add_argument("model_id", nargs="?", help="Model run ID")

    # Clean command
    clean_parser = subparsers.add_parser("clean", help="Clean up model runs")
    clean_parser.add_argument("model_id", help="Model run ID")

    return parser


def _run(args: argparse.Namespace) -> None:
    """Run the model.

    :param args: the parsed CLI arguments.
    :type args: argparse.Namespace
    """
    # load the params
    with open(args.params, "r", encoding="UTF-8") as f:
        params = json.load(f)

    # handle the app_version
    app_version = args.app_version or params.get("app_version", "dev")
    # push the app version back into the params, in case it has changed
    params["app_version"] = app_version

    # handle the dataset override
    if args.dataset:
        params["dataset"] = args.dataset

    # create the model run
    metadata = create_model_run(
        params,
        app_version,
        args.save_full_model_results,
        args.timeout,
    )
    print(f"Model run started: {metadata['id']}")


def _status_single_model_run(model_id: str) -> None:
    """Print the status of a single model run.

    :param model_id: The model id to get the status of.
    :type model_id: str
    """
    status = get_model_run_status(model_id)
    if not status:
        print(f"Unknown model id: {model_id}")
        return

    state = status["state"]

    complete = status["complete"]
    model_runs = status["model_runs"]
    if complete["outpatients"] >= model_runs:
        complete_str = f"aae: {complete['aae']}"
    elif complete["inpatients"] >= model_runs:
        complete_str = f"op: {complete['outpatients']}"
    else:
        complete_str = f"ip: {complete['inpatients']}"

    print(f"{model_id}: {state} [{complete_str}/{model_runs}]")


def _status_all_model_runs() -> None:
    """Print the status of all of the current model runs."""
    current_runs = get_current_model_runs()

    if not current_runs:
        print("There are currently no model runs")
        return

    print("Current Model Runs:")
    for k, v in current_runs.items():
        state = v["state"] if v else "unknown"
        print(f"{k}: {state}")


def _status(args: argparse.Namespace) -> None:
    """Status subcommand.

    :param args: the parsed CLI arguments.
    :type args: argparse.Namespace
    """
    if args.model_id:
        _status_single_model_run(args.model_id)
    else:
        _status_all_model_runs()


def main() -> None:
    """Main method."""
    parser = _arg_parser()
    args = parser.parse_args()

    match args.command:
        case "run":
            _run(args)
        case "status":
            _status(args)
        case "clean":
            clean_up_model_run(args.model_id)
        case _:
            parser.print_help()


def init() -> None:
    """Init method."""
    if __name__ == "__main__":
        main()


init()
