import json
import logging
import os
import random
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any, Optional

import numpy as np
import pandas as pd

from cyrxnopt.NestedVenv import NestedVenv
from cyrxnopt.OptimizerABC import OptimizerABC
from cyrxnopt.utilities.config.transforms import use_subkeys
from cyrxnopt.utilities.NpEncoder import NpEncoder

logger = logging.getLogger(__name__)


class OptimizerEDBOp(OptimizerABC):
    # Private static data member to list dependency packages required
    # by this class
    _packages = [
        "setuptools<82.0",
        "git+https://github.com/zachcran/edboplus@performance_improvements",
    ]

    def __init__(self, venv: NestedVenv) -> None:
        """Optimizer class for the EDBO+ algorithm.

        :param venv: Virtual environment to install the optimizer
        :type venv: NestedVenv
        """
        super().__init__(venv)

        self._edbop_filename = "my_optimization.csv"
        self._reaction_order_filename = "reaction_order.csv"

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
                "value": [],
            },
            {
                "name": "continuous_feature_resolutions",
                "type": "list[float]",
                "value": [],
            },
            {
                "name": "categorical_feature_names",
                "type": "list[str]",
                "value": [],
            },
            {
                "name": "categorical_feature_values",
                "type": "list[list[str]]",
                "value": [],
            },
            {
                "name": "budget",
                "type": "int",
                "value": 100,
                "range": [1, sys.maxsize],
            },
            {
                "name": "objectives",
                "type": "list[str]",
                "value": ["yield"],
            },
            {
                "name": "direction",
                "type": "list[str]",
                "value": ["min"],
                "range": ["min", "max"],
            },
        ]

        return config

    def set_config(self, experiment_dir: str, config: dict[str, Any]) -> None:
        """Generate all the necessary data files based on the given configuration.

        See :py:meth:`OptimizerABC.set_config` for more information about how
        to form the config dictionary and for general usage information.

        :param experiment_dir: Output directory for the configuration file
        :type experiment_dir: str
        :param config: CyRxnOpt-level config for the optimizer
        :type config: dict[str, Any]
        """

        self._validate_config(config)

        if not os.path.exists(experiment_dir):
            os.makedirs(experiment_dir)

        # Get reaction scope configurations from general config
        config = self._config_translate(config)

        # generate reaction scope for EDBO+
        self.venv_worker.run_command(f"""
from edbo.plus.optimizer_botorch import EDBOplus; EDBOplus().generate_reaction_scope(
    components={config["reaction_components"]},
    directory="{experiment_dir}",
    filename="{self._edbop_filename}",
    check_overwrite=False,
)
""")

        # Initialize the EDBO+ file to be used for prediction
        self.venv_worker.run_command(f"""
from edbo.plus.optimizer_botorch import EDBOplus; EDBOplus().run(
    directory="{experiment_dir}",
    # Previously generated scope
    filename="{self._edbop_filename}",
    # Objectives to be optimized
    # For example, maximize yield and ee but minimize side_product:
    # objectives=['yield', 'ee', 'side_product'],
    # objective_mode=['max', 'max', 'min'],
    objectives={config["objectives"]},
    objective_mode={config["direction"]},
    # Number of experiments in parallel to perform in this round
    batch=1,
    # Features to be included in the model
    columns_features="all",
    # Initialization method
    init_sampling_method="seed",
    seed={random.randint(0, 2**32 - 1)},
)
""")

        config_path = os.path.join(experiment_dir, self._config_filename)

        with open(config_path, "w") as fout:
            json.dump(config, fout, indent=4, cls=NpEncoder)

        # Create file for preserving reaction order
        # TODO: Rework this when we switch to multi-objective!
        with open(
            Path(experiment_dir) / self._reaction_order_filename, "w"
        ) as fout:
            feature_names = config["continuous"]["feature_names"]
            # If categorical feature names is an empty list, list.extend leaves
            # the list unchanged
            feature_names.extend(config["categorical"]["feature_names"])

            # Collect the feature names and objective names as headers
            headers = feature_names
            headers.extend(config["objectives"])

            fout.write(",".join(headers) + "\n")

    def train(
        self,
        prev_param: list[Any],
        yield_value: float,
        experiment_dir: str,
        config: dict[str, Any],
        obj_func: Optional[Callable[..., float]] = None,
    ) -> list[Any]:
        """No training step for this algorithm.

        :returns: List will always be empty.
        :rtype: list[Any]
        """

        # If an objective function is provided, assume that the user is trying
        # to train this algorithm and send a signal that there is no training
        # to be done.
        if obj_func is not None:
            obj_func([])

        return []

    def predict(
        self,
        prev_param: list[Any],
        yield_value: float,
        experiment_dir: str,
        config: dict[str, Any],
        obj_func: Optional[Callable[..., float]] = None,
    ) -> Any:
        """Searches for the best parameters and records results from prior steps.

        .. note::

            **Behavior Note:** This method operates with a one-call-at-a-time
            approach, not with an internal optimization loop. For a unified
            behavioral interface, please use
            :func:`cyrxnopt.utilities.predict_server`.

        :py:meth:`OptimizerEDBOp.set_config` must be called prior to this method
        to generate the necessary files.

        :param prev_param: Parameters provided from the previous prediction,
                           provide an empty list for the first call
        :type prev_param: list[Any]
        :param yield_value: Experimental yield
        :type yield_value: float
        :param experiment_dir: Output directory for any generated files
        :type experiment_dir: str
        :param config: CyRxnOpt-level config for the optimizer
        :type config: dict[str, Any]
        :param obj_func: Ignored for this optimizer, defaults to None
        :type obj_func: Optional[Callable[..., float]], optional

        :returns: The next suggested reaction to perform
        :rtype: list[Any]
        """

        # Get reaction scope configurations from general config file
        config = self._config_translate(config)

        # Read optimization file with reaction conditions
        df_edbo = pd.read_csv(
            os.path.join(experiment_dir, self._edbop_filename)
        )

        if len(prev_param) != 0:
            df_edbo.loc[0, config["objectives"][0]] = yield_value
            df_edbo.to_csv(
                os.path.join(experiment_dir, self._edbop_filename), index=False
            )

            # Write the reaction parameters and results to the file preserving
            # reaction order
            # TODO: Rework this when we switch to multi-objective!
            with open(
                Path(experiment_dir) / self._reaction_order_filename, "a"
            ) as fout:
                line = prev_param
                line.extend([yield_value])
                line = [str(element) for element in line]
                fout.write(",".join(line))
                fout.write("\n")

        self.venv_worker.run_command(f"""
from edbo.plus.optimizer_botorch import EDBOplus; EDBOplus().run(
    directory="{experiment_dir}",
    filename="{self._edbop_filename}",
    objectives={config["objectives"]},
    objective_mode={config["direction"]},
    batch=1,
    columns_features="all",
    init_sampling_method="seed",
    seed={random.randint(0, 2**32 - 1)},
    write_extra_data=False,
)
""")

        # After one cycle of prediction, read the reaction condition file to
        # get the next reaction condition
        df_edbo = pd.read_csv(
            os.path.join(experiment_dir, self._edbop_filename)
        )

        next_combo = df_edbo.iloc[:1].values.tolist()
        next_combo = next_combo[0][:-2]

        return next_combo

    def _config_translate(self, config: dict[str, Any]) -> dict[str, Any]:
        """Convers general config into EDBO+ reaction scope config format.

        :param config: General configuration dictionary
        :type config: dict[str, Any]

        :return: Translated configuration dictionary
        :rtype: dict[str, Any]
        """

        self._import_deps()
        reaction_components = {}

        config = use_subkeys(config)

        for i in range(len(config["continuous"]["feature_names"])):
            low_bound = config["continuous"]["bounds"][i][0]
            upper_bound = config["continuous"]["bounds"][i][1]
            increment = config["continuous"]["resolutions"][i]

            values = np.arange(low_bound, upper_bound + increment, increment)

            values = [float(x) for x in values]

            reaction_components[config["continuous"]["feature_names"][i]] = (
                values
            )

        if bool(config["categorical"]["feature_names"]):
            for i in range(len(config["categorical"]["feature_names"])):
                reaction_components[
                    config["categorical"]["feature_names"][i]
                ] = config["categorical"]["values"][i]

        config["reaction_components"] = reaction_components

        # EDBO+ supports multi-objective optimization, of which single-
        # objective optimization is a subset. When providing arguments
        # for single-objective optimization, only one objective and one
        # corresponding direction must be given. This catches when the user
        # does not provide single-element lists for the objectives and
        # their directions, which could be an easy mistake.
        if type(config["objectives"]) is str:
            config["objectives"] = [config["objectives"]]
        if type(config["direction"]) is str:
            config["direction"] = [config["direction"]]

        edbo_config = {
            "reaction_components": reaction_components,
            "objectives": config["objectives"],
            "direction": config["direction"],
        }

        edbo_config = config | edbo_config

        return edbo_config

    def _import_deps(self) -> None:
        """Import packages needed to run the optimizer."""

        if not self.venv_worker.check_package("edbo"):
            raise ModuleNotFoundError
