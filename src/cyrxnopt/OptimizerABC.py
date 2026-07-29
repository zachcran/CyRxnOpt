import logging
from abc import ABC, abstractmethod
from collections.abc import Callable
from pathlib import Path
from typing import Any, Optional

from cyrxnopt.NestedVenv import NestedVenv
from cyrxnopt.VenvWorker import VenvWorker

logger = logging.getLogger(__name__)


class OptimizerABC(ABC):
    """This is the abstract class for general optimizer algorithms
    which include all the abstract functions need.
    """

    # Private static data member to list dependency packages required
    # by this class. This should be overwritten in children.
    _packages: list[str] = []

    def __init__(self, venv: NestedVenv) -> None:
        """Instantiates general Optimizer properties.

        :param venv: Virtual environment manager to use
        :type venv: cyrxnopt.NestedVenv
        """

        self._imports: dict[str, Any] = {}  # Populated in self._import_deps()
        self.__venv = venv
        self.venv_worker = VenvWorker(venv.prefix)

        self._config_filename = "config.json"

    def check_install(self) -> bool:
        """Check if an installation for this optimizer exists or not.

        :return: Whether the optimizer is installed (True) or not (False).
        :rtype: bool
        """

        # Attempt to import all of the packages this optimizer depends
        # on. If this import fails, we consider the optimizer to not
        # be installed or to have a broken install.
        try:
            self._import_deps()
        except ModuleNotFoundError as e:
            # Printing the exception so the user knows what went wrong
            logger.error(e)
            return False

        return True

    def install(self, local_paths: dict[str, str] = {}) -> None:
        """Install the optimizer and its dependencies.

        The list of packages to be installed can be checked with the
        :py:meth:`OptimizerABC.dependencies` property.

        :param local_paths: Mapping of package names to local paths to the
            packages to be installed. The package names in the mapping must
            match a name returned by :py:meth:`OptimizerABC.dependencies`.
            Defaults to {}
        :type local_paths: dict[str, str], optional
        """

        logger.info("Installing {}...".format(self.__class__.__name__))

        if not self.__venv.is_active():
            self.__venv.activate()

        # Install each package
        for package in self._packages:
            # Install from local path if one is given
            if package in local_paths.keys():
                self.venv_worker.pip_install_e(Path(local_paths[package]))
            else:
                self.venv_worker.pip_install(package)

        # Import the packages after they were installed
        self._import_deps()

    @abstractmethod
    def get_config(self) -> list[dict[str, Any]]:
        """Provides descriptions for valid configuration settings for an optimizer.

        This method provides information about the possible configuration options
        and their default values for a given optimizer. The intent is for this
        method to provide the necessary information for a user-facing program to
        present the configuration options to the user. Once the user has chosen
        their desired configurations, they can be set for the optimizer using
        :py:meth:`~OptimizerABC.set_config`.

        The configuration descriptions returned by this function are
        dictionaries with three keys, "name", "type", and "value":

        - "name" will contain the name for the config option in snake_case,
          with "continuous" or "categorical" prepended to the name if two
          versions of the option are needed for continuous and categorical
          variables.
        - "type" will contain the Python type annotation describing the type
          to use for this option (for translating to strictly typed languages)
        - "value" will provide the default value of the option.
        - "range" is optional and used to specify the allowed range for
          numbers or to constrain what options a string input can accept.
          For example, a description of an option for the optimization
          direction could be::

             {
                 "name": "optimization_direction",
                 "type": str,
                 "value": "min",
                 "range": ["min", "max"]
             }
        - "description" is an optional description of the purpose of a config
          option, along with any caveats that may come with it.

        .. note::

           For number bounds that are only in one direction, such as >0 or <=0,
           define a "range" using typical max/min values of the data type as
           appropriate, a very large/small number, or define a reasonable bound
           for the specific application. For example, >0 on an integer could be
           [1, sys.maxsize], or <=0 could be [-sys.maxsize + 1, 0]
        """

        pass

    @abstractmethod
    def set_config(self, experiment_dir: str, config: dict[str, Any]) -> None:
        """Generates initial configurations and files for an optimizer.

        Valid configuration options should be retrieved using
        :py:meth:`~OptimizerABC.get_config` before calling this function.
        The key for each option must match the corresponding "name" field
        and the value type must match the one assigned in the "type" field
        from the optimizer's :py:meth:`~OptimizerABC.get_config` method.

        :param experiment_dir: Experimental directory for saving data files.
        :type experiment_dir: str
        :param config: Configuration settings defined from `get_config()`.
        :type config: dict[str, Any]
        """

        pass

    @abstractmethod
    def train(
        self,
        prev_param: list[Any],
        yield_value: float,
        experiment_dir: str,
        config: dict[str, Any],
        obj_func: Optional[Callable[..., float]] = None,
    ) -> list[Any]:
        """Abstract optimizer training function.

        If an optimizer does not support/need training, the default behavior
        returning an empty list can be used.

        :param prev_param: Parameters provided from the previous prediction or
                           training step.
        :type prev_param: list[Any]
        :param yield_value: Result from the previous prediction or training
                            step.
        :type yield_value: float
        :param experiment_dir: Output directory for the optimizer algorithm.
        :type experiment_dir: str
        :param config: Optimizer config
        :type config: dict[str, Any]
        :param obj_func: Objective function to optimize, defaults to None
        :type obj_func: Optional[Callable[..., float]], optional

        :returns: The next suggested reaction to perform
        :rtype: list[Any]
        """
        # If an objective function is provided, assume that the user is trying
        # to train this algorithm and send a signal that there is no training
        # to be done.
        if obj_func is not None:
            obj_func([])

        return []

    @abstractmethod
    def predict(
        self,
        prev_param: list[Any],
        yield_value: float,
        experiment_dir: str,
        config: dict[str, Any],
        obj_func: Optional[Callable] = None,
    ) -> Any:
        """Abstract optimizer prediction function.

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

        :returns: The results of the prediction. Check function documentation
            for potential behavioral notes and specific return values of each
            optimization class.
        :rtype: Any
        """

        pass

    @abstractmethod
    def _import_deps(self) -> None:
        """Imports required dependencies for the optimizer"""

        pass

    def _validate_config(self, config: dict[str, Any]) -> None:
        """Verifies that an optimizer configuration is valid.

        :param config: Optimizer configuration to check
        :type config: dict[str, Any]
        :raises RuntimeError: Invalid optimizer configuration
        """

        # Make sure that feature names are provided
        if (
            "continuous_feature_names" not in config
            and "categorical_feature_names" not in config
        ):
            raise RuntimeError(
                (
                    "Either 'continuous_feature_names' or "
                    "'categorical_feature_names' must be provided in the "
                    "configuration."
                )
            )

        # Make sure all continuous feature descriptors were provided
        if "continuous_feature_names" in config:
            no_bounds = False
            no_resolutions = False
            msg = "'continuous_feature_names' was provided, but "

            if "continuous_feature_bounds" not in config:
                no_bounds = True
                msg += "'continuous_feature_bounds' "
            if "continuous_feature_resolutions" not in config:
                no_resolutions = True
                if no_bounds:
                    msg += "and "
                msg += "'continuous_feature_resolutions' "

            if no_bounds and no_resolutions:
                msg += "were "
            else:
                msg += "was "

            msg += "not."

            if no_bounds or no_resolutions:
                raise RuntimeError(msg)

        # Make sure all categorical feature descriptors were provided
        if "categorical_feature_names" in config:
            msg = "'categorical_feature_names' was provided, but "

            if "categorical_feature_values" not in config:
                msg += "'categorical_feature_values' was not."
                raise RuntimeError(msg)

        if "budget" not in config:
            raise RuntimeError("'budget' must be provided in the config.")

        if "direction" not in config:
            raise RuntimeError("'direction' must be provided in the config.")

    @property
    def dependencies(self) -> list[str]:
        """Dependencies required by this optimizer.

        :return: Dependency package names
        :rtype: list[str]
        """

        return self._packages
