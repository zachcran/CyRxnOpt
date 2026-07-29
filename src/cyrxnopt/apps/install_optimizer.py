import argparse
import logging
import os
import sys
from typing import Callable

from cyrxnopt.apps._utilities import arg_validation as validate
from cyrxnopt.apps._utilities import common_args as parsers
from cyrxnopt.NestedVenv import NestedVenv
from cyrxnopt.OptimizerController import check_install, install

logger = logging.getLogger(__name__)


def main(args: argparse.Namespace) -> int:
    optimizer = validate.optimizer(args.optimizer)
    location = validate.location(args.location)

    logging.basicConfig(level=args.log_level)

    # Prepare virtual environment
    venv_path = os.path.join(location, f"venv_{optimizer}")
    venv = NestedVenv(venv_path)

    if not os.path.exists(venv_path) or args.force:
        print(f"Creating virtual environment at: {venv_path}")
        venv.create()
    logger.info(f"Activating virtual environment at: {venv_path}")
    venv.activate()

    # Install the optimizer if it is not already installed
    if not check_install(optimizer, venv):
        install(
            optimizer,
            venv,
        )
        print(f'Optimizer "{optimizer}" installed in venv at {venv_path}')
    else:
        print(
            (
                "Optimizer already installed. Use the '-f' flag to force "
                "a fresh reinstall if needed."
            )
        )

        return 2

    print(
        (
            "Reminder: Generate a config file for your optimizer now with "
            "'cyrxnopt config-init'."
        )
    )

    return 0


def get_parser(
    create_lambda: Callable[
        ..., argparse.ArgumentParser
    ] = argparse.ArgumentParser,
) -> argparse.ArgumentParser:
    parser = create_lambda(
        parents=[parsers.optimizer(), parsers.location(), parsers.logging()]
    )

    parser.add_argument(
        "-f",
        "--force",
        dest="force",
        action="store_true",
        help=(
            "Forces a fresh installation by recreating the virtual environment."
        ),
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
