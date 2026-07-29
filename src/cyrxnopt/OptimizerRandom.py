import copy
import json
import logging
import os
import random
import sys
from collections.abc import Callable
from typing import Any, Optional

from cyrxnopt.NestedVenv import NestedVenv
from cyrxnopt.OptimizerABC import OptimizerABC

logger = logging.getLogger(__name__)


class OptimizerRandom(OptimizerABC):
    """Optimizer class that searches the reaction space using uniform
    random sampling.

    Continuous features are sampled independently from a continuous
    uniform distribution within their configured bounds. Categorical
    features are sampled independently and uniformly from their list of
    allowed values. Every suggestion is drawn independently of all prior
    suggestions, so no adaptation or learning takes place between calls;
    this optimizer is primarily useful as a baseline for benchmarking other
    algorithms.
    """

    # Private static data member to list dependency packages required
    # by this class. Random sampling only relies on Python's standard
    # library, so no additional packages need to be installed.
    _packages: list[str] = []

    def __init__(self, venv: NestedVenv) -> None:
        """Optimizer class for random sampling of the reaction space.

        :param venv: Virtual environment to install the optimizer
        :type venv: NestedVenv
        """

        super().__init__(venv)

        self._results_filename = "results.csv"

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
                # Not used for sampling since continuous features are drawn
                # from a continuous uniform distribution instead of a
                # discretized grid, but kept for compatibility with the
                # standard config schema.
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
                "name": "objective",
                "type": "list[str]",
                "value": ["yield"],
            },
            {
                "name": "direction",
                "type": "list[str]",
                "value": ["min"],
                "range": ["min", "max"],
            },
            {
                "name": "seed",
                "type": "int",
                "value": None,
                "description": (
                    "Optional seed for reproducible sampling. If omitted, "
                    "or set to null/None, each suggested reaction is drawn "
                    "from a fresh, non-reproducible source of randomness."
                ),
            },
        ]

        return config

    def set_config(self, experiment_dir: str, config: dict[str, Any]) -> None:
        """Generate the necessary data files based on the given configuration.

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

        if not os.path.exists(experiment_dir):
            os.makedirs(experiment_dir)

        translated_config = self._config_translate(config)

        config_path = os.path.join(experiment_dir, self._config_filename)

        with open(config_path, "w") as fout:
            json.dump(translated_config, fout, indent=4)

        # Create the file used to preserve suggested reaction conditions
        # and their recorded results, in the order they were performed.
        with open(
            os.path.join(experiment_dir, self._results_filename), "w"
        ) as fout:
            feature_names = list(translated_config["continuous_feature_names"])
            feature_names.extend(translated_config["categorical_feature_names"])

            # Collect the feature names and objective name as headers
            # TODO: Extend this when we support multi-objective
            headers = feature_names
            headers.append(translated_config["objective"][0])

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
    ) -> list[Any]:
        """Draws a new set of reaction conditions and records results from
        the previous step.

        .. note::

            **Behavior Note:** This method operates with a one-call-at-a-time
            approach, not with an internal optimization loop. For a unified
            behavioral interface, please use
            :func:`cyrxnopt.utilities.predict_server`.

        :py:meth:`OptimizerRandom.set_config` must be called prior to this
        method to generate the necessary files.

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

        self._import_deps()

        translated_config = self._config_translate(config)

        results_path = os.path.join(experiment_dir, self._results_filename)

        # Record the reaction parameters and result from the previous step
        # to the results file, preserving the order they were performed in.
        # TODO: Rework this when we switch to multi-objective!
        if len(prev_param) != 0:
            with open(results_path, "a") as fout:
                line = [str(element) for element in prev_param]
                line.append(str(yield_value))
                fout.write(",".join(line))
                fout.write("\n")

        # Since suggestions are drawn independently (with replacement), no
        # state needs to persist between calls other than an optional seed.
        # A fresh instance of this class is created for every call, so the
        # number of previously recorded results is used, along with the
        # configured seed, to keep suggestions reproducible across separate
        # calls when a seed is provided.
        call_index = self._count_recorded_results(results_path)
        rng = self._make_rng(config.get("seed"), call_index)

        next_combo: list[Any] = []

        continuous_bounds = translated_config["continuous_feature_bounds"]
        for bounds in continuous_bounds:
            low_bound = float(bounds[0])
            upper_bound = float(bounds[1])

            next_combo.append(rng.uniform(low_bound, upper_bound))

        categorical_values = translated_config["categorical_feature_values"]
        for values in categorical_values:
            next_combo.append(rng.choice(values))

        return next_combo

    def _config_translate(self, config: dict[str, Any]) -> dict[str, Any]:
        """Converts general config into the format used by this optimizer.

        :param config: General configuration dictionary
        :type config: dict[str, Any]

        :return: Translated configuration dictionary
        :rtype: dict[str, Any]
        """

        translated_config = copy.deepcopy(config)

        # Random sampling supports multi-objective configuration in the
        # sense that it does not use the objective(s) to decide what to
        # sample, but only a single objective's results are recorded to
        # the results file (see the TODO notes in set_config/predict).
        # This catches when the user does not provide single-element
        # lists for the objectives and their directions, which could be
        # an easy mistake.
        if type(translated_config.get("objective")) is str:
            translated_config["objective"] = [translated_config["objective"]]
        if type(translated_config.get("direction")) is str:
            translated_config["direction"] = [translated_config["direction"]]

        return translated_config

    def _count_recorded_results(self, results_path: str) -> int:
        """Counts the number of reaction results recorded so far.

        :param results_path: Path to the results file created by
            :py:meth:`OptimizerRandom.set_config`
        :type results_path: str

        :return: Number of recorded results, not counting the header row.
                 Returns 0 if the results file does not exist yet.
        :rtype: int
        """

        if not os.path.exists(results_path):
            return 0

        with open(results_path) as fin:
            line_count = sum(1 for _ in fin)

        # Subtract 1 to account for the header row. This is guarded against
        # going negative in case the results file is empty for some reason.
        return max(line_count - 1, 0)

    def _make_rng(self, seed: Optional[int], call_index: int) -> random.Random:
        """Creates a random number generator for the current prediction call.

        :param seed: Base seed from the optimizer config, or None to use a
            fresh, non-reproducible source of randomness.
        :type seed: Optional[int]
        :param call_index: Number of results already recorded, used to
            derive a distinct, reproducible seed for each call.
        :type call_index: int

        :return: Random number generator to use for this prediction call.
        :rtype: random.Random
        """

        if seed is None:
            return random.Random()

        return random.Random(int(seed) + call_index)

    def _import_deps(self) -> None:
        """No external dependencies are required for random sampling.

        This optimizer only relies on Python's standard library, so this
        method is a no-op provided for interface compatibility with
        :py:class:`OptimizerABC`.
        """

        self._imports = {}
