import logging
import re
import shutil
import subprocess
import sys
import venv
from pathlib import Path
from subprocess import CalledProcessError
from typing import Optional, Union

from packaging.specifiers import InvalidSpecifier, SpecifierSet
from packaging.version import Version

# from cyrxnopt.utilities.reset_module import reset_module
logger = logging.getLogger(__name__)


class VenvWorker:
    def __init__(self, venv_dir: Union[str, Path]) -> None:
        self._prefix = Path(venv_dir)

    def create(self) -> Union[str, Path]:
        venv_builder = venv.EnvBuilder(
            system_site_packages=False,
            clear=True,
            symlinks=False,
            upgrade=False,
            with_pip=True,
            prompt=None,
            upgrade_deps=True,
        )
        venv_builder.create(self.prefix)

        return self.prefix

    def delete(self) -> None:
        shutil.rmtree(self.prefix)

    def run_command(
        self,
        command: str,
    ) -> None:
        """Install a package to the active virtual environment using
        ``pip install`` for an editable install.

        :param command: Name of the package
        :type command: str

        :raises CalledProcessError: An error occurred when running pip freeze
        """
        # Create the command list
        cmd: list[str] = [str(self.python), "-c"]
        cmd.append(command)

        logger.debug("Running command: {}".format(command))

        completed_process = subprocess.run(
            cmd,
            capture_output=True,  # Capture stdout and stderr
            encoding="utf-8",  # Dencode the stdout and stderr bytestrings
        )

        logger.debug("stdout: {}".format(completed_process.stdout))
        logger.debug("stderr: {}".format(completed_process.stderr))

        try:
            # Raises CalledProcessError if the return code is non-zero
            completed_process.check_returncode()
        except CalledProcessError as e:
            logger.error("Return code nonzero: {}".format(e))
            logger.error("stdout: {}".format(completed_process.stdout))
            logger.error("stderr: {}".format(completed_process.stderr))

    def pip_freeze(self) -> list[str]:
        """Returns the list of modules in the virtual environment as
        they would be returned by 'pip freeze'.

        :raises CalledProcessError: An error occurred when running pip freeze
        """

        # Run ``pip freeze`` and capture the output
        completed_process = subprocess.run(
            [self.python, "-m", "pip", "freeze"],
            capture_output=True,  # Capture stdout and stderr
            encoding="utf-8",  # Dencode the stdout and stderr bytestrings
        )

        # Raises CalledProcessError if the return code is non-zero
        completed_process.check_returncode()

        # The response is split by newlines since one package is
        # printed on each line
        return completed_process.stdout.split()

    def pip_install(
        self,
        package_name: str,
        package_path: Optional[Path] = None,
        editable: bool = False,
    ) -> None:
        """Install a package to the active virtual environment using
        ``pip install`` for an editable install.

        :param package_name: Name of the package
        :type package_name: str
        :param package_path: Path to the package location. Defaults to None
            (do not use a local path)
        :type package_path: Optional[Path]
        :param editable: Whether to use an editable install. Defaults to False
        :type editable: bool, optional

        :raises CalledProcessError: An error occurred when running pip freeze
        """

        logger.info(f"Installing {package_name}")

        # Decide whether this is a local path or PyPI package
        if package_path is not None:
            package: str = str(package_path)
        else:
            package = package_name

        # Do we need to prepend ``-e`` for an editable install?
        pre_args = []
        if editable:
            pre_args.append("-e")

        # Create the command list
        cmd: list[str] = [str(self.python), "-m", "pip", "install"]
        cmd.extend(pre_args)
        cmd.append(package)

        logger.debug("Running command: {}".format(cmd))

        completed_process = subprocess.run(
            cmd,
            capture_output=True,  # Capture stdout and stderr
            encoding="utf-8",  # Dencode the stdout and stderr bytestrings
        )

        logger.debug("stdout: {}".format(completed_process.stdout))
        logger.debug("stderr: {}".format(completed_process.stderr))

        try:
            # Raises CalledProcessError if the return code is non-zero
            completed_process.check_returncode()
        except CalledProcessError as e:
            logger.error("Return code nonzero: {}".format(e))
            logger.error("stdout: {}".format(completed_process.stdout))
            logger.error("stderr: {}".format(completed_process.stderr))

    def pip_install_e(self, package_path: Path, package_name: str = "") -> None:
        """Install a package to the active virtual environment using
        ``pip install`` for an editable install.

        :param package_path: Path to the package location
        :type package_path: Path
        :param package_name: Name of the package, defaults to "". If not provided,
            the package name is assumed to the the last part of ``package_path``.
        :type package_name: str, optional

        :raises CalledProcessError: An error occurred when running ``pip install``
        """

        # Derive the package name from the package path if a name is not
        # explicitly provided
        if package_name == "":
            package_name = package_path.stem
            logger.info(
                (
                    f"Defaulting to package name of {package_name}",
                    f"from the package path: {package_path}",
                )
            )

        # Attempt to install the package
        self.pip_install(package_name, package_path, editable=True)

    def pip_install_r(self, req_file: Path) -> None:
        """Installs package requirements from a "requirements.txt"-style file.

        :param req_file: Requirements file to use
        :type req_file: str

        :raises CalledProcessError: An error occurred when running
            ``pip install`` for a package
        """

        # Read each line of the requirements file and install the packages
        with open(req_file, "r") as fin:
            lines = fin.readlines()

            for line in lines:
                if line.startswith("-e"):
                    package_path = Path(line.replace("-e", "").strip())
                    package_name = package_path.stem

                    self.pip_install(
                        package_name,
                        package_path.resolve(strict=True),
                        editable=True,
                    )

                else:
                    package = line
                    self.pip_install(package)

    def check_package(self, package: str, version: Union[str,] = "") -> bool:
        try:
            expected_version: Union[Version, SpecifierSet] = SpecifierSet(
                version
            )
        except InvalidSpecifier:
            expected_version = Version(version)

        logger.debug(f"Checking for '{package}' in venv: {self.prefix}")

        pip_show: list[str] = [str(self.python), "-m", "pip", "show"]
        pip_show.append(package)

        logger.debug("Running command: {}".format(pip_show))

        completed_process = subprocess.run(
            pip_show,
            capture_output=True,  # Capture stdout and stderr
            encoding="utf-8",  # Dencode the stdout and stderr bytestrings
        )

        logger.debug("stdout: {}".format(completed_process.stdout))
        logger.debug("stderr: {}".format(completed_process.stderr))
        logger.debug("returncode: {}".format(completed_process.returncode))

        # pip show returns 0 if found and 1 if not
        if completed_process.returncode != 0:
            return False

        # No version to check; we're done
        if version == "":
            logger.debug(f'Found a package matching "{package}"')
            return True

        # Now check the version of the found package
        pkg_version_match = re.search(
            r"Version: ([^\s]+)", completed_process.stdout
        )
        assert pkg_version_match is not None, (
            "Pattern matching error for check package version search. "
            "Please submit an issue!"
        )

        pkg_version = Version(pkg_version_match.group(1))
        logger.debug(f"Found {package} version: {pkg_version}")

        if isinstance(expected_version, SpecifierSet):
            return expected_version.contains(pkg_version)
        # Assume it is a Version at this point, otherwise an exception would
        # have occurred above
        else:
            return expected_version == pkg_version

    def _get_python_version(self) -> str:
        # This grabs the full semver, for example, "3.11.3"
        python_version = sys.version.split(" ")[0]

        # Remove the patch version
        python_version = ".".join(python_version.split(".")[:2])

        return python_version

    @property
    def binary_directory(self) -> Path:
        """The venv subdirectory containing binaries based on operating system.

        :return: Full path to the venv binary directory
        :rtype: Path
        """

        return self.prefix / self._binary_directory_name

    @property
    def prefix(self) -> Path:
        """The prefix directory for this venv.

        :return: Full path to the prefix directory for this venv
        :rtype: Path
        """

        return self._prefix

    @prefix.setter
    def prefix(self, value: Path) -> None:
        full_prefix = value.resolve()

        logger.debug("Setting venv prefix to {}".format(full_prefix))
        self._prefix = full_prefix

    @property
    def python(self) -> Path:
        """The python binary of the venv based on operatingsystem.

        :return: Full path to the Python binary of the venv
        :rtype: Path
        """

        return self.binary_directory / self._python_binary_file_name

    @property
    def _python_binary_file_name(self) -> str:
        """The python binary file name based on operating system.

        :return: Python binary file name
        :rtype: str
        """

        return "python.exe" if sys.platform == "win32" else "python"

    @property
    def _binary_directory_name(self) -> str:
        """The name of the venv subdirectory containing binaries based on
        operating system.

        :return: Virtual environment binary directory
        :rtype: str
        """

        return "Scripts" if sys.platform == "win32" else "bin"
