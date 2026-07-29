import json
import logging
import os
import sys
from collections.abc import Callable
from typing import Any, Optional

from cyrxnopt.NestedVenv import NestedVenv
from cyrxnopt.OptimizerABC import OptimizerABC
from cyrxnopt.utilities.config.transforms import use_subkeys

logger = logging.getLogger(__name__)


class OptimizerAmlro(OptimizerABC):
    # Private static data member to list dependency packages required
    # by this class
    _packages = [
        "git+https://github.com/RxnRover/amlo",
        "numpy",
        "pandas",
        "joblib",
    ]

    def __init__(self, venv: NestedVenv) -> None:
        """Optimizer class for the AMLRO package.

        :param venv: Virtual environment to install the optimizer
        :type venv: NestedVenv
        """

        super().__init__(venv)

        self._full_combo_filename = "full_combo_file.txt"
        self._training_combo_filename = "training_combo_file.txt"
        self._training_set_filename = "training_set_file.txt"
        self._training_set_decoded_filename = "training_set_decoded_file.txt"

    def get_config(self) -> list[dict[str, Any]]:
        """Gets the configuration options available for this optimizer.

        See :py:meth:`OptimizerABC.get_config` for more information about the
        config descriptions returned by this method and for general usage
        information.

        :return: Configuration option descriptions
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
                "type": "str",
                "value": "min",
                "range": ["min", "max"],
            },
        ]

        return config

    def set_config(self, experiment_dir: str, config: dict[str, Any]) -> None:
        """Generates necessary data files based on the given config.

        See :py:meth:`OptimizerABC.set_config` for more information about how
        to form the config dictionary and for general usage information.

        :param experiment_dir: Output directory for generated files
        :type experiment_dir: str
        :param config: Configuration options for this optimizer instance
        :type config: dict[str, Any]
        """

        self._import_deps()

        self._validate_config(config)

        if not os.path.exists(experiment_dir):
            os.makedirs(experiment_dir)

        full_combo_list = self._imports[
            "generate_combos"
        ].generate_uniform_grid(use_subkeys(config))

        full_combo_list = self._imports["np"].around(
            full_combo_list, decimals=4
        )
        full_combo_df = self._imports["pd"].DataFrame(full_combo_list)
        training_combo_df = full_combo_df.sample(20)

        if bool(config["categorical_feature_names"]):
            feature_names_list = self._imports["np"].concatenate(
                (
                    config["continuous_feature_names"],
                    config["categorical_feature_names"],
                )
            )
        else:
            feature_names_list = config["continuous_feature_names"]

        full_combo_df.columns = feature_names_list

        full_combo_path = os.path.join(
            experiment_dir, self._full_combo_filename
        )
        training_combo_path = os.path.join(
            experiment_dir, self._training_combo_filename
        )

        full_combo_df.to_csv(full_combo_path, index=False)
        training_combo_df.to_csv(training_combo_path, index=False)

        training_set_path = os.path.join(
            experiment_dir, self._training_set_filename
        )
        training_set_decoded_path = os.path.join(
            experiment_dir, self._training_set_decoded_filename
        )

        # Write the reaction conditions for training dataset into files
        # (encoded and decoded versions)
        with open(training_set_path, "w") as file_object:
            feature_names = ",".join([str(elem) for elem in feature_names_list])
            file_object.write(feature_names + ",Yield" + "\n")

        with open(training_set_decoded_path, "w") as file_object:
            feature_names = ",".join([str(elem) for elem in feature_names_list])
            file_object.write(feature_names + ",Yield" + "\n")

        config_path = os.path.join(experiment_dir, self._config_filename)

        with open(config_path, "w") as fout:
            json.dump(config, fout, indent=4)

    def train(
        self,
        prev_param: list[Any],
        yield_value: float,
        experiment_dir: str,
        config: dict[str, Any],
        obj_func: Optional[Callable[..., float]] = None,
    ) -> list[Any]:
        """Suggests and records training data points needed for AMLRO.

        :py:meth:`OptimizerAmlro.set_config` must be called prior to this method
        to generate the necessary files.

        The previous parameter+result is recorded during the *next*
        call to either :py:meth:`~OptimizerAmlro.train` or
        :py:meth:`~OptimizerAmlro.predict`. This means that on the first call
        here, the ``prev_param`` and ``yield_value`` values provided are
        ignored. Importantly, this also means that the last suggested
        parameter+result pair from training will not be recorded unless either
        another :py:meth:`~OptimizerAmlro.train` or a subsequent
        :py:meth:`~OptimizerAmlro.predict` call are made afterward!

        :param prev_param: Experimental parameter combination from the previous
            experiment, provide an empty list for the first call
        :type prev_param: list[Any]
        :param yield_value: Experimental yield
        :type yield_value: float
        :param experiment_dir: Output directory for saving data files
        :type experiment_dir: str
        :param config: CyRxnOpt-level config for the optimizer
        :type config: dict[str, Any]
        :param obj_func: Ignored for this optimizer, defaults to None
        :type obj_func: Optional[Callable[..., float]], optional

        :return: Next parameter combination to perform, or an empty list (``[]``)
                 if all training points have been performed
        :rtype: list[Any]
        """

        self._import_deps()

        training_set_path = os.path.join(
            experiment_dir, self._training_set_filename
        )
        training_set_decoded_path = os.path.join(
            experiment_dir, self._training_set_decoded_filename
        )
        training_combo_path = os.path.join(
            experiment_dir, self._training_combo_filename
        )

        if config["direction"].lower() == "min":
            yield_value = -yield_value

        # Determine next training row to perform
        training_combos = self._imports["pd"].read_csv(training_combo_path)
        training_set = self._imports["pd"].read_csv(training_set_path)
        next_index = self._get_next_training_index_by_length(
            training_combos, training_set
        )

        # Exit early if all training points have already been performed
        if next_index == -1:
            return []

        # Workaround to avoid being stuck at the first parameter
        if len(prev_param) > 0:
            next_index += 1

        # training step
        next_parameters = self._imports[
            "training_set_generator"
        ].generate_training_data(
            training_set_path,
            training_set_decoded_path,
            training_combo_path,
            use_subkeys(config),
            prev_param,
            yield_value,
            next_index,
        )

        return next_parameters

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

        :py:meth:`OptimizerAmlro.set_config` and :py:meth:`OptimizerAmlro.train`
        must be called prior to this method to generate the necessary files and
        initial training data for the model.

        The previous parameter+result is recorded during the *next*
        call to :py:meth:`~OptimizerAmlro.predict`. The ``prev_param`` and
        ``yield_value`` values provided here are always recorded. Importantly,
        this also means that the last suggested parameter+result pair from
        prediction will not be recorded unless either another
        :py:meth:`~OptimizerAmlro.predict` call is made afterward!

        :param prev_param: Parameters provided from the previous prediction
                           or from the final call to :py:meth:`OptimizerAmlro.train`
        :type prev_param: list[Any]
        :param yield_value: Result from the previous suggested conditions
        :type yield_value: float
        :param experiment_dir: Output directory for saving data files
        :type experiment_dir: str
        :param config: CyRxnOpt-level config for the optimizer
        :type config: dict[str, Any]
        :param obj_func: Ignored for this optimizer, defaults to None
        :type obj_func: Optional[Callable[..., float]], optional

        :return: The next suggested reaction to perform
        :rtype: list[Any]
        """

        self._import_deps()

        training_set_path = os.path.join(
            experiment_dir, self._training_set_filename
        )
        training_set_decoded_path = os.path.join(
            experiment_dir, self._training_set_decoded_filename
        )
        full_combo_path = os.path.join(
            experiment_dir, self._full_combo_filename
        )

        if config["direction"].lower() == "min":
            yield_value = -yield_value

        # prediction step
        best_combo = self._imports["optimizer_main"].get_optimized_parameters(
            training_set_path,
            training_set_decoded_path,
            full_combo_path,
            use_subkeys(config),
            prev_param,
            yield_value,
        )

        return best_combo

    def _import_deps(self) -> None:
        """importing all the packages and libries needed for running amlro optimizer"""

        import numpy as np  # type: ignore
        import pandas as pd  # type: ignore
        from amlro import (  # type: ignore
            generate_combos,
            optimizer,
            optimizer_main,
            training_set_generator,
        )

        self._imports = {
            "generate_combos": generate_combos,
            "training_set_generator": training_set_generator,
            "optimizer": optimizer,
            "optimizer_main": optimizer_main,
            "np": np,
            "pd": pd,
        }

    def _get_next_training_index_by_length(  # type: ignore
        self, training_combos, training_dataset
    ) -> int:
        """Gets the index for the next training condition to be performed.

        This is implemented by a simple check on the dataset length. It is
        assumed that the only rows present in the dataset are those from the
        training combo list. This means that if the dataset has 6 rows, then
        the index of the next training combo to perform is also 6.

        :param training_combos: Training conditions suggested by AMLRO
        :type training_combos: pd.DataFrame
        :param training_dataset: Current dataset of performed reactions used to
                                 train AMLRO
        :type training_dataset: pd.DataFrame

        :returns: Index in the training combo list of the next conditions
                  missing from the training dataset. An index of -1 is returned
                  if the dataset is longer than the training combo list.
        :rtype: int
        """

        # Get the row counts of the training combos and dataset
        combo_rows = len(training_combos.index)
        dataset_rows = len(training_dataset.index)

        # Simple check assuming the dataset only contains the training combos
        # that have been run
        if dataset_rows >= combo_rows:
            # No more training points to run
            return -1

        # The row count of the dataset will be the next index in the combo
        # list due to zero indexing
        return dataset_rows
