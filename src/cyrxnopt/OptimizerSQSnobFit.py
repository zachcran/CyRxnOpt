import json
import os
import sys
from collections.abc import Callable
from typing import Any, Optional

from cyrxnopt.NestedVenv import NestedVenv
from cyrxnopt.OptimizerABC import OptimizerABC


class OptimizerSQSnobFit(OptimizerABC):
    # Private static data member to list dependency packages required
    # by this class
    _packages = ["SQSnobFit"]

    def __init__(self, venv: NestedVenv) -> None:
        """Optimizer class for the SQSnobFit algorithm from the ``SQSnobFit`` package.

        :param venv: Virtual environment manager to use
        :type venv: NestedVenv
        """

        super().__init__(venv)

    def get_config(self) -> list[dict[str, Any]]:
        """Get the configuration options available for this optimizer.

        See :py:meth:`OptimizerABC.get_config` for more information about the
        config descriptions returned by this method and for general usage
        information.

        :return: List of configuration options with option name, data type,
                 and information about which values are allowed/defaulted.
        :rtype: list[dict[str, Any]]
        """

        config: list[dict[str, Any]] = [
            {
                "name": "continuous_feature_names",
                "type": "list[str]",
                "value": [],
            },
            {
                "name": "continuous_feature_bounds",
                "type": "list[list[float]]",
                "value": [[]],
            },
            {
                # Not used for this algorithm, but kept for compatibility with
                # the standard config schema
                "name": "continuous_feature_resolutions",
                "type": "list[float]",
                "value": [],
            },
            {
                "name": "budget",
                "type": "int",
                "value": 100,
                "range": [1, sys.maxsize],
            },
            {
                "name": "direction",
                "type": "str",
                "value": ["min", "max"],
            },
            {
                "name": "param_init",
                "type": "list",
                "value": [],
            },
            {
                "name": "maxfail",
                "type": "int",
                "value": 5,
            },
            {
                "name": "verbose",
                "type": "bool",
                "value": False,
            },
        ]

        return config

    def set_config(self, experiment_dir: str, config: dict[str, Any]) -> None:
        """Set the configuration for this instance of the optimizer.

        See :py:meth:`OptimizerABC.set_config` for more information about how
        to form the config dictionary and for general usage information.

        :param experiment_dir: Output directory for the configuration file
        :type experiment_dir: str
        :param config: CyRxnOpt-level config for the optimizer
        :type config: dict[str, Any]
        """

        self._import_deps()

        # continuous_feature_resolution not needed for this algorithm, so ignore
        # it and fill in with placeholder for validation
        if "continuous_feature_resolutions" not in config:
            config["continuous_feature_resolutions"] = 0

        self._validate_config(config)

        output_file = os.path.join(experiment_dir, self._config_filename)

        # Write the configuration to a file for later use
        with open(output_file, "w") as fout:
            json.dump(config, fout, indent=4)

    def train(
        self,
        prev_param: list[Any],
        yield_value: float,
        experiment_dir: str,
        config: dict[str, Any],
        obj_func: Optional[Callable] = None,
    ) -> list[Any]:
        """No training step for this algorithm.

        .. note::

            **Behavior Note:** If an objective function is provided, it will be
            called once with an empty list to indicate that training is not
            needed.

        :returns: List will always be empty.
        :rtype: list[Any]
        """
        return super().train(
            prev_param,
            yield_value,
            experiment_dir,
            config,
            obj_func,
        )

    def predict(
        self,
        prev_param: list[Any],
        yield_value: float,
        experiment_dir: str,
        config: dict[str, Any],
        obj_func: Optional[Callable[..., float]] = None,
    ) -> Any:
        """Find the desired optimum of the provided objective function.

        .. note::

            **Behavior Note:** This method operates with an internal optimization
            loop, not a one-call-at-a-time approach. For a unified behavioral
            interface, please use :func:`cyrxnopt.utilities.predict_server`.

        :param prev_param: Parameters provided from the previous prediction,
                           provide an empty list for the first call
        :type prev_param: list[Any]
        :param yield_value: Result from the previous prediction
        :type yield_value: float
        :param experiment_dir: Output directory for the optimizer algorithm
        :type experiment_dir: str
        :param config: CyRxnOpt-level config for the optimizer
        :type config: dict[str, Any]
        :param obj_func: Objective function to optimize, defaults to None. Due
            to the alternative behavior of this method, this is *required*.
        :type obj_func: Optional[Callable[..., float]]

        :returns: The next suggested reaction to perform
        :rtype: `SQCommon.Result
            <https://github.com/scikit-quant/scikit-quant/blob/master/opt/common/python/SQCommon/_result.py#L6>`__
        """

        if obj_func is None:
            raise RuntimeError(
                (
                    "Objective function is required for this implementation of "
                    "SQSnobFit (SNOBFIT), as it does not support "
                    "one-call-at-a-time approach."
                )
            )

        self._import_deps()

        # Load the config file
        # with open(os.path.join(experiment_dir, "recent_config.json")) as fout:
        #     config = json.load(fout)

        # Convert initial parameters to tuple
        # param_init = tuple(config["param_init"])
        param_init = config["param_init"]

        # Convert bounds list to sequence of tuples
        # bounds = tuple([tuple(bound_list) for bound_list in config["bounds"]])
        bounds = config["continuous_feature_bounds"]

        options = {
            "minfcall": None,
            "maxmp": None,
            "maxfail": config["maxfail"],
            "verbose": config["verbose"],
        }
        options = self._imports["SQSnobFit"].optset(options)

        # Call the minimization function
        result, history = self._imports["SQSnobFit"].minimize(
            obj_func,
            param_init,
            bounds,
            config["budget"],
            options,
        )

        result.history = history

        return result

    def _import_deps(self) -> None:
        """Import package needed to run the optimizer."""

        import SQSnobFit  # type: ignore

        self._imports = {
            "SQSnobFit": SQSnobFit,
        }
