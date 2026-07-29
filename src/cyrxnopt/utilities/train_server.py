from typing import TYPE_CHECKING, Any, Callable, Tuple

from cyrxnopt.OptimizerController import train

if TYPE_CHECKING:
    from cyrxnopt.NestedVenv import NestedVenv

problematic_optimizers = [
    "amlro",
    "edbop",
]


def train_server(
    optimizer_name: str,
    training_steps: int,
    output_dir: str,
    config: dict[str, Any],
    venv: "NestedVenv",
    obj_func: Callable[[list[float]], float],
) -> Tuple[list[Any], float]:
    """Unified behavioral interface for training all supported optimizers.

    This interface unifies the behavior of all supported optimizers to be
    internal training loops accepting an objective function, wrapping
    algorithms with one-call-at-a-time training behavior with
    :func:`train_faux_server` to emulate an internal training loop.

    :param optimizer_name: Name of the supported optimizer to use
    :type optimizer_name: str
    :param training_steps: Number of training steps to perform
    :type training_steps: int
    :param output_dir: Output directory for saving data files
    :type output_dir: str
    :param config: CyRxnOpt-level config for the optimizer
    :type config: dict[str, Any]
    :param venv: Virtual environment to use
    :type venv: NestedVenv
    :param obj_func: Objective function to optimize
    :type obj_func: Callable[[list[float]], float]

    :raises RuntimeError: Internal training loop algorithms are not yet supported.

    :return: Final training parameters and resulting objective value
    :rtype: Tuple[list[Any], float]
    """
    if optimizer_name.lower() in problematic_optimizers:
        prev_param, yield_value = train_faux_server(
            optimizer_name,
            training_steps,
            output_dir,
            config,
            venv,
            obj_func,
        )
    else:
        prev_param = train(
            optimizer_name,
            venv,
            [],
            0,
            output_dir,
            config,
            obj_func=obj_func,
        )

        # Algorithm doesn't support training
        if len(prev_param) == 0:
            yield_value = 0
        else:
            # TODO: Support grabbing the last yield value when an algorithm
            # behaves like this
            raise RuntimeError(
                (
                    "Algorithms with internal training loops are not yet "
                    f"supported by {__name__}. Please submit an issue "
                    "requesting this feature if you have an optimizer that"
                    " requires this."
                )
            )

    return prev_param, yield_value


def train_faux_server(
    optimizer_name: str,
    training_steps: int,
    output_dir: str,
    config: dict[str, Any],
    venv: "NestedVenv",
    obj_func: Callable[[list[float]], float],
) -> Tuple[list[Any], float]:
    """Wrapper for one-call-at-a-time training behavior to unify the
    training behavior interface for all supported algorithms as internal
    training loops

    :param optimizer_name: Name of the supported optimizer to use
    :type optimizer_name: str
    :param training_steps: Number of training steps to perform
    :type training_steps: int
    :param output_dir: Output directory for saving data files
    :type output_dir: str
    :param config: CyRxnOpt-level config for the optimizer
    :type config: dict[str, Any]
    :param venv: Virtual environment to use
    :type venv: NestedVenv
    :param obj_func: Objective function to optimize
    :type obj_func: Callable[[list[float]], float]

    :return: Final training parameters and resulting objective value
    :rtype: Tuple[list[Any], float]
    """
    prev_param: list[float] = []
    yield_value = 0.0

    for i in range(training_steps):
        prev_param = train(
            optimizer_name,
            venv,
            prev_param,
            yield_value,
            output_dir,
            config,
        )

        yield_value = obj_func(prev_param)

    return prev_param, yield_value
