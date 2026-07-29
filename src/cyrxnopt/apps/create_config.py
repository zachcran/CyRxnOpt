import argparse
import json
import logging
import os
import sys
from typing import Callable

from cyrxnopt.apps._utilities import arg_validation as validate
from cyrxnopt.apps._utilities import common_args as parsers
from cyrxnopt.NestedVenv import NestedVenv
from cyrxnopt.OptimizerController import check_install, get_config

logger = logging.getLogger(__name__)


def main(args: argparse.Namespace) -> int:
    optimizer = validate.optimizer(args.optimizer)
    location = validate.location(args.location)
    config_path = validate.config_path(args.config, location)

    logging.basicConfig(level=args.log_level)

    # Prepare virtual environment
    venv_path = os.path.join(location, "venv_{}".format(optimizer))
    venv = NestedVenv(venv_path)

    if not os.path.exists(venv_path) and not check_install(optimizer, venv):
        print(
            (
                "No optimizer install found at the given location. Run "
                "'install_optimizer --help' for more details on how to "
                "install an optimizer."
            )
        )
        return -1
    logger.info("Activating virtual environment at: {}".format(venv_path))
    venv.activate()

    config_descriptions = get_config(optimizer, venv)

    config_contents = {}
    for config in config_descriptions:
        value = config["value"]

        if config["type"] == "str":
            if type(config["value"]) is list:
                value = value[0]

        config_contents[config["name"]] = value

    if config_path.exists() and not args.force:
        print(
            (
                "Config file already exists at {}. "
                "Use the '-f' flag to overwrite this file with a new, "
                "default config file."
            ).format(config_path)
        )
        return -1

    with open(config_path, "w") as fout:
        print("Writing config to file:", config_path)
        json.dump(config_contents, fout, indent=4)

    print(
        (
            "Reminder: You must edit the config file for your experiment! "
            "Then, run 'cyrxnopt config' for your optimizer."
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

    parser.add_argument(
        "-f",
        "--force",
        dest="force",
        action="store_true",
        help=("Forces a fresh configuration file to be created."),
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
