import argparse
import json
import logging
import sys
import traceback
from typing import Callable

from cyrxnopt.apps._utilities import arg_validation as validate
from cyrxnopt.apps._utilities import common_args as parsers
from cyrxnopt.NestedVenv import NestedVenv
from cyrxnopt.OptimizerController import check_install, set_config

logger = logging.getLogger(__name__)


def main(args: argparse.Namespace) -> int:
    optimizer = validate.optimizer(args.optimizer)
    location = validate.location(args.location)
    config_path = validate.config_path(args.config, location)

    logging.basicConfig(level=args.log_level)

    # Prepare virtual environment
    venv_path = location / f"venv_{optimizer}"
    venv = NestedVenv(venv_path)

    if not venv_path.exists() and not check_install(optimizer, venv):
        print(
            (
                "No optimizer install found at the given location. Run "
                "'install_optimizer --help' for more details on how to install "
                "an optimizer."
            )
        )
        return -1
    logger.debug(f"Activating virtual environment at: {venv_path}")
    venv.activate()

    # Make sure the config file exists
    if not config_path.exists():
        print(f"Config file not found at {config_path}.")
        return -1

    with open(config_path, "r") as fin:
        logger.debug(f"Reading config to file: {config_path}")
        config_contents = json.load(fin)

    print(f"Configuring optimizer: {optimizer}")
    print("Potential output from the optimizer:")
    try:
        set_config(optimizer, venv, config_contents, str(location))
    except Exception:
        # Print error message to stdout
        print(
            (
                "Configuring the optimizer failed! "
                "See log output for more details."
            )
        )
        # As well as in the logs
        logger.critical(
            (
                "Exception occurred while configuring the optimizer:\n"
                f"{traceback.format_exc()}"
            )
        )

        return -1

    print(
        (
            "Reminder: You may need to train your optimizer now with "
            "'cyrxnopt train' or you can go straight to 'cyrxnopt predict'."
        )
    )

    return 0


def get_parser(
    create_lambda: Callable[
        ..., argparse.ArgumentParser
    ] = argparse.ArgumentParser,
) -> argparse.ArgumentParser:
    parser = create_lambda(
        parents=[
            parsers.optimizer(),
            parsers.config(),
            parsers.location(),
            parsers.logging(),
        ]
    )

    return parser


def parse_args() -> argparse.Namespace:
    """Parse command line arguments"""
    parser = get_parser()

    return parser.parse_args()


def run() -> int:
    return main(parse_args())


if __name__ == "__main__":
    sys.exit(run())
