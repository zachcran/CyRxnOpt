import shutil
import sys
import venv
from pathlib import Path

import pytest

from cyrxnopt.VenvWorker import VenvWorker


@pytest.fixture
def test_venv_path(tmp_path):
    return tmp_path / "venv"


@pytest.fixture
def test_venv(test_venv_path):
    create_venv(test_venv_path)

    yield test_venv_path

    # Clean up
    shutil.rmtree(test_venv_path)


def create_venv(venv_path):
    venv_builder = venv.EnvBuilder(
        system_site_packages=False,
        clear=True,
        symlinks=False,
        upgrade=False,
        with_pip=True,
        prompt=None,
        upgrade_deps=True,
    )
    venv_builder.create(venv_path)

    return venv_path


def test_pip_install_numpy(test_venv) -> None:
    """This test attempts to install the 'numpy' package from online
    using 'pip'.
    """

    worker = VenvWorker(test_venv)

    # CyRxnOpt depends on numpy, but it should be reinstalled in the nested venv
    worker.pip_install("numpy")

    assert worker.check_package("numpy")


def test_pip_install_test_package_with_path(
    test_venv, test_assets_path
) -> None:

    worker = VenvWorker(test_venv)

    worker.pip_install(
        "test_project", package_path=test_assets_path / "test_project"
    )

    assert worker.check_package("test_project")


def test_pip_install_e(test_venv, test_assets_path) -> None:
    """This test attempts to self-install this package into a new
    virtual environment using an editable install.
    """

    venv = VenvWorker(test_venv)

    venv.pip_install_e(test_assets_path / "test_project")

    assert venv.check_package("test_project")


def test_pip_install_r(test_venv, test_assets_path) -> None:
    """This test attempts to self-install this package's requirements.txt
    file into a new virtual environment using
    'pip install -r requirements.txt'.
    """

    venv = VenvWorker(test_venv)

    venv.pip_install_r(test_assets_path / "requirements.txt")

    assert venv.check_package("test_project")
    assert venv.check_package("numpy")
    assert venv.check_package("requests")


def test_pip_install_numpy_first_of_two_venvs(test_venv_path) -> None:
    venv1 = Path(str(test_venv_path) + "_1")
    venv2 = Path(str(test_venv_path) + "_2")
    create_venv(venv1)
    create_venv(venv2)

    venv1_worker = VenvWorker(venv1)
    venv2_worker = VenvWorker(venv2)

    # Install numpy only into the first, non-primary venv
    venv1_worker.pip_install("numpy")

    # The first venv should have numpy
    assert venv1_worker.check_package("numpy")

    # The second, primary venv should not
    assert not venv2_worker.check_package("numpy")

    shutil.rmtree(venv1)
    shutil.rmtree(venv2)


def test_pip_install_numpy_two_versions(test_venv_path) -> None:
    venv1 = Path(str(test_venv_path) + "_1")
    venv2 = Path(str(test_venv_path) + "_2")
    create_venv(venv1)
    create_venv(venv2)

    venv1_worker = VenvWorker(venv1)
    venv2_worker = VenvWorker(venv2)

    if sys.version_info[:2] >= (3, 12):
        numpy_version_1 = "2.0"
        numpy_version_2 = "1.26"
    elif sys.version_info[:2] >= (3, 9):
        numpy_version_1 = "1.25"
        numpy_version_2 = "1.24"
    else:
        raise RuntimeError("Python versions under 3.9 not supported")

    venv1_worker.pip_install(f"numpy=={numpy_version_1}")
    venv2_worker.pip_install(f"numpy=={numpy_version_2}")

    assert venv1_worker.check_package("numpy", f"{numpy_version_1}.0")
    assert not venv1_worker.check_package("numpy", ">=2.0")
    assert venv2_worker.check_package("numpy", f"{numpy_version_2}.0")

    shutil.rmtree(venv1)
    shutil.rmtree(venv2)
