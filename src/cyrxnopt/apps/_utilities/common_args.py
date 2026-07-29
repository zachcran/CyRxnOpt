import argparse


def optimizer() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("optimizer", help="Optimizer to use.")

    return parser


def location() -> argparse.ArgumentParser:
    """Provides an argument parser for a root experiment/operating location.

    :return: Parser providing arguments for root experiment/operating location.
    :rtype: argparse.ArgumentParser
    """
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument(
        "-l",
        "--location",
        dest="location",
        default=".",
        type=str,
        help=(
            "Root location for experiment data. This location must exist! "
            "Defaults to the current working directory."
        ),
    )

    return parser


def config() -> argparse.ArgumentParser:
    """Provides an argument parser for getting a config file.

    :return: Parser providing arguments for getting a config file.
    :rtype: argparse.ArgumentParser
    """
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument(
        "-c",
        "--config",
        dest="config",
        default=None,
        type=str,
        help=(
            "Configuration file to use for the given optimizer. "
            "Defaults to <location>/config.json"
        ),
    )

    return parser


def logging() -> argparse.ArgumentParser:
    """Provides an argument parser for common logging capabilities.

    :return: Parser providing arguments for logging capabilities.
    :rtype: argparse.ArgumentParser
    """
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument(
        "--log-level",
        dest="log_level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="WARNING",
        # Make choices case insensitive
        type=str.upper,
        help=("Set the log level. Defaults to WARNING"),
    )

    return parser
