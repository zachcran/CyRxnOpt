import logging
from collections.abc import Callable
from typing import Any, Optional

from cyrxnopt.NestedVenv import NestedVenv
from cyrxnopt.OptimizerABC import OptimizerABC
from cyrxnopt.OptimizerAmlro import OptimizerAmlro
from cyrxnopt.OptimizerEDBOp import OptimizerEDBOp
from cyrxnopt.OptimizerNMSimplex import OptimizerNMSimplex
from cyrxnopt.OptimizerRandom import OptimizerRandom
from cyrxnopt.OptimizerSQSnobFit import OptimizerSQSnobFit

logger = logging.getLogger(__name__)


def check_install(optimizer_name: str, venv: NestedVenv) -> bool:
    """Checks if an optimizer is installed in the given environment.

    :param optimizer_name: Name of the optimizer algorithm
    :type optimizer_name: str
    :param venv: Environment containing the optimizer installation
    :type venv: NestedVenv

    :return: Whether the optimizer is installed (True) or not (False)
    :rtype: bool
    """

    opt = get_optimizer(optimizer_name, venv)

    return opt.check_install()


def install(
    optimizer_name: str, venv: NestedVenv, local_paths: dict[str, str] = {}
) -> None:
    """Installs an optimizer into the given environment.

    :param optimizer_name: Name of the optimizer algorithm
    :type optimizer_name: str
    :param venv: Environment containing the optimizer installation
    :type venv: NestedVenv
    :param local_paths: Mapping of package names to local paths to the packages
        to be installed, defaults to {}
    :type local_paths: dict[str, str], optional
    """

    opt = get_optimizer(optimizer_name, venv)

    opt.install(local_paths=local_paths)


def get_config(optimizer_name: str, venv: NestedVenv) -> list[dict[str, Any]]:
    """Gets the description of the options available for an optimizer.

    :param optimizer_name: Name of the optimizer algorithm
    :type optimizer_name: str
    :param venv: Environment containing the optimizer installation
    :type venv: NestedVenv

    :return: Descriptions for valid configuration values of the optimizer.
    :rtype: list[dict[str, Any]]
    """

    opt = get_optimizer(optimizer_name, venv)

    return opt.get_config()


def set_config(
    optimizer_name: str,
    venv: NestedVenv,
    config: dict[str, Any],
    experiment_dir: str,
) -> None:
    """Sets the provided options for the given optimizer.

    :param optimizer_name: Name of the optimizer algorithm
    :type optimizer_name: str
    :param venv: Environment containing the optimizer installation
    :type venv: NestedVenv
    :param config: Desired optimizer configuration
    :type config: dict[str, Any]
    :param experiment_dir: Directory to be used for the current experiment.
        This is where the config files will be output.
    :type experiment_dir: str
    """

    opt = get_optimizer(optimizer_name, venv)

    opt.set_config(experiment_dir, config)


def train(
    optimizer_name: str,
    venv: NestedVenv,
    prev_param: list[Any],
    yield_value: float,
    experiment_dir: str,
    config: dict[str, Any],
    obj_func: Optional[Callable] = None,
) -> list[Any]:
    """Predicts new reaction conditions using the given optimizer.

    :param optimizer_name: Name of the optimizer algorithm
    :type optimizer_name: str
    :param venv: Environment containing the optimizer installation
    :type venv: NestedVenv
    :param prev_param: Previous suggested reaction conditions
    :type prev_param: list[Any]
    :param yield_value: Yield value from previous reaction conditions
    :type yield_value: float
    :param experiment_dir: Output directory for the current experiment
    :type experiment_dir: str
    :param config: Optimizer configuration
    :type config: dict[str, Any]
    :param obj_func: Objective function to optimize, defaults to None
    :type obj_func: Optional[Callable], optional

    :returns: The next suggested conditions to perform
    :rtype: list[Any]
    """

    opt = get_optimizer(optimizer_name, venv)

    opt.check_install()

    return opt.train(prev_param, yield_value, experiment_dir, config, obj_func)


def predict(
    optimizer_name: str,
    venv: NestedVenv,
    prev_param: list[Any],
    yield_value: float,
    experiment_dir: str,
    config: dict[str, Any],
    obj_func: Optional[Callable] = None,
) -> list[Any]:
    """Predicts new reaction conditions using the given optimizer.

    :param optimizer_name: Name of the optimizer algorithm
    :type optimizer_name: str
    :param venv: Environment containing the optimizer installation
    :type venv: NestedVenv
    :param prev_param: experimental parameter combination for previous experiment
    :type prev_param: list[Any]
    :param yield_value: experimental yield
    :type yield_value: float
    :param experiment_dir: experimental directory for saving data files
    :type experiment_dir: str
    :param config: Initial reaction feature configurations
    :type config: dict[str, Any]
    :param obj_func: Objective function needed to optimize, defaults to None
    :type obj_func: Optional[Callable], optional

    :return: Next suggested reaction conditions
    :rtype: list[Any]
    """

    opt = get_optimizer(optimizer_name, venv)

    try:
        next_suggestion = opt.predict(
            prev_param, yield_value, experiment_dir, config, obj_func=obj_func
        )
    except TypeError:
        next_suggestion = opt.predict(
            prev_param, yield_value, experiment_dir, config
        )

    return next_suggestion


def get_optimizer(optimizer_name: str, venv: NestedVenv) -> OptimizerABC:
    """Gets an instance of the requested optimizer algorithm

    :param optimizer_name: Name of the optimizer algorithm
    :type optimizer_name: str
    :param venv: Environment containing the optimizer installation
    :type venv: NestedVenv

    :raises RuntimeError: Invalid optimizer name given

    :return: Requested optimizer
    :rtype: OptimizerABC
    """

    optimizer_name = optimizer_name.lower()

    # Define the initial base type of the optimizer
    optimizer: OptimizerABC

    # Determine which optimizer to use
    if optimizer_name == "amlro":
        optimizer = OptimizerAmlro(venv)
    elif optimizer_name == "edbop":
        optimizer = OptimizerEDBOp(venv)
    elif optimizer_name == "nmsimplex":
        optimizer = OptimizerNMSimplex(venv)
    elif optimizer_name == "random":
        optimizer = OptimizerRandom(venv)
    elif optimizer_name == "sqsnobfit":
        optimizer = OptimizerSQSnobFit(venv)
    else:
        raise RuntimeError(
            "Invalid optimizer name given: {}".format(optimizer_name)
        )

    return optimizer
