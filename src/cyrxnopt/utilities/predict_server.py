from typing import TYPE_CHECKING, Any, Callable, Union

from cyrxnopt.OptimizerController import predict

if TYPE_CHECKING:
    from cyrxnopt.NestedVenv import NestedVenv

problematic_optimizers = ["amlro", "edbop", "random"]


def predict_server(
    optimizer_name: str,
    prev_param: list[Any],
    yield_value: float,
    output_dir: str,
    config: dict[str, Any],
    venv: "NestedVenv",
    obj_func: Callable[[list[float]], float],
) -> Union[list[Any], dict[str, Any]]:
    """Unified behavioral interface for prediction on all supported optimizers.

    This interface unifies the behavior of all supported optimizers to be
    internal optimization loops accepting an objective function, wrapping
    algorithms with one-call-at-a-time optimization behavior with
    :func:`predict_faux_server` to emulate an internal optimization loop.

    :param optimizer_name: Name of the supported optimizer to use
    :type optimizer_name: str
    :param prev_param: Parameters provided from the previous prediction
        or from the final call to training.
    :type prev_param: list[Any]
    :param yield_value: Result from the previous suggested conditions
    :type yield_value: float
    :param output_dir: Output directory for saving data files
    :type output_dir: str
    :param config: CyRxnOpt-level config for the optimizer
    :type config: dict[str, Any]
    :param venv: Virtual environment to use
    :type venv: NestedVenv
    :param obj_func: Objective function to optimize
    :type obj_func: Callable[[list[float]], float]

    :return: Final optimization loop results
    :rtype: Union[list[Any], dict[str, Any]]
    """
    if optimizer_name.lower() in problematic_optimizers:
        results = predict_faux_server(
            optimizer_name,
            prev_param,
            yield_value,
            output_dir,
            config,
            venv,
            obj_func,
        )
    else:
        results = predict(
            optimizer_name,
            venv,
            prev_param,
            yield_value,
            output_dir,
            config,
            obj_func,
        )

    return results


def predict_faux_server(
    optimizer_name: str,
    prev_param: list[Any],
    yield_value: float,
    output_dir: str,
    config: dict[str, Any],
    venv: "NestedVenv",
    obj_func: Callable[[list[float]], float],
) -> Union[list[Any], dict[str, Any]]:
    """Wrapper for one-call-at-a-time prediction behavior to unify the
    optimization behavior interface for all supported algorithms as internal
    optimization loops

    :param optimizer_name: Name of the supported optimizer to use
    :type optimizer_name: str
    :param prev_param: Parameters provided from the previous prediction
        or from the final call to training.
    :type prev_param: list[Any]
    :param yield_value: Result from the previous suggested conditions
    :type yield_value: float
    :param output_dir: Output directory for saving data files
    :type output_dir: str
    :param config: CyRxnOpt-level config for the optimizer
    :type config: dict[str, Any]
    :param venv: Virtual environment to use
    :type venv: NestedVenv
    :param obj_func: Objective function to optimize
    :type obj_func: Callable[[list[float]], float]

    :return: Final optimization loop results
    :rtype: Union[list[Any], dict[str, Any]]
    """
    results = {
        "total_iter": config["budget"],
        "best_coords": None,
        "best_value": None,
        "best_iter": None,
        "raw_results": [],
    }

    # TODO: This is a temporary fix until multi-objective is supported
    if type(config["direction"]) is list:
        direction = config["direction"][0]
    else:
        direction = config["direction"]

    if direction == "min":
        results["best_value"] = float("inf")
    else:
        results["best_value"] = float("-inf")

    # Loop over cycle iterations
    for i in range(config["budget"]):
        prev_param = predict(
            optimizer_name,
            venv,
            prev_param,
            yield_value,
            output_dir,
            config,
        )

        yield_value = obj_func(prev_param)

        if (direction == "min" and yield_value < results["best_value"]) or (
            direction == "max" and yield_value > results["best_value"]
        ):
            results["best_value"] = yield_value
            results["best_coords"] = prev_param
            results["best_iter"] = i

        # Add another line to the raw results
        result_line = [x for x in prev_param]
        result_line.append(yield_value)
        results["raw_results"].append(result_line)

    return results
