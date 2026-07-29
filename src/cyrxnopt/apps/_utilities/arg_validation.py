from pathlib import Path
from typing import Optional

# Basic list of supported optimizers. In the future, hopefully we can
# dynamically populate this.
SUPPORTED_OPTIMIZERS: list[str] = [
    "amlro",
    "edbop",
    "nmsimplex",
    "random",
    "sqsnobfit",
]


def optimizer(arg_value: str) -> str:
    """Validates the optimizer argument provided, checking against supported
    optimizer identifiers.

    :param arg_value: Optimizer argument value
    :type arg_value: str
    :raises ValueError: Invalid optimizer
    :return: Optimizer argument value that was provided (unedited)
    :rtype: str
    """

    if arg_value not in SUPPORTED_OPTIMIZERS:
        raise ValueError(f"Invalid optimizer identifier: {arg_value}")

    return arg_value


def location(arg_value: str) -> Path:
    """Validates and normalizes the location argument provided.

    This function does NOT create the location directory.

    :param arg_value: Location directory provided
    :type arg_value: str

    :raises ValueError: Location or its parent directory did not exist.

    :return: Normalized location directory path
    :rtype: Path
    """
    # Ensure location is a Path, absolute, and normalized for the OS
    location = Path(arg_value).resolve()

    # Ensure the location (or at least its parent) exists
    if not location.parent.exists():
        raise ValueError("Location directory (or its parent) does not exist.")

    return location


def config_path(
    arg_value: Optional[str],
    location: Path,
    default_filename: str = "config.json",
) -> Path:
    """Validates and defaults the config file path.

    Does not create the config file or location.

    :param arg_value: Config file path, defaults to "``location``/``default_filename``"
    :type arg_value: Optional[str]
    :param location: Location directory for CyRxnOpt to operate. It is highly
        recommended that this is first validated with :func:``validate_location``.
    :type location: Path
    :param default_filename: Default filename to use if arg_value is None,
        defaults to "config.json"
    :type default_filename: str, optional

    :return: Normalized config file path
    :rtype: Path
    """
    config_path = Path(arg_value) if arg_value is not None else Path()

    # Default the config path to config.json in the provided location
    if arg_value is None:
        config_path = location / "config.json"

    return config_path
