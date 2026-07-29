import sys
from pathlib import Path

import pytest

from cyrxnopt.NestedVenv import NestedVenv


@pytest.fixture
def test_venv(tmp_path):
    venv_path = tmp_path / "venv"

    return venv_path


def test_activate_with_no_venv_created(test_venv) -> None:
    venv = NestedVenv(test_venv)

    with pytest.raises(RuntimeError):
        venv.activate()


def test_activate_with_venv_created(test_venv) -> None:
    venv = NestedVenv(test_venv)
    venv.create()

    # Shouldn't throw an exception
    venv.activate()


def test_activate_when_active(test_venv) -> None:
    venv = NestedVenv(test_venv)
    venv.create()

    # Shouldn't throw an exception
    venv.activate()

    # Also shouldn't throw an exception
    venv.activate()


def test_activate_two_venvs(test_venv) -> None:
    venv1 = NestedVenv(Path(str(test_venv) + "_1"))
    venv2 = NestedVenv(Path(str(test_venv) + "_2"))

    # Created first, will not be primary
    venv1.create()
    venv1.activate()

    # Created second, will be primary
    venv2.create()
    venv2.activate()

    assert not venv1.is_primary()
    assert venv2.is_primary()

    # Both venvs should be active
    assert venv1.is_active()
    assert venv2.is_active()


def test_activate_two_venvs_then_deactivate_first(test_venv) -> None:
    venv1 = NestedVenv(Path(str(test_venv) + "_1"))
    venv2 = NestedVenv(Path(str(test_venv) + "_2"))

    # Created first, will not be primary
    venv1.create()
    venv1.activate()

    # Created second, will be primary
    venv2.create()
    venv2.activate()

    venv1.deactivate()

    # Only venv2 should be primary
    assert not venv1.is_primary()
    assert venv2.is_primary()

    # Only venv2 should be active
    assert not venv1.is_active()
    assert venv2.is_active()


def test_create_with_no_prior_creation(test_venv) -> None:
    venv = NestedVenv(test_venv)

    venv.create()

    # Check that the created venv exists and has the right components
    assert test_venv.exists()
    assert venv.python.exists()


def test_create_when_dir_exists(test_venv) -> None:
    venv = NestedVenv(test_venv)

    # Create the directory beforehand
    test_venv.mkdir(parents=True, exist_ok=False)

    # Creating venv but path already exists
    venv.create()

    # Check that the venv was created and has the right components
    assert test_venv.exists()
    assert venv.python.exists()


def test_create_twice(test_venv) -> None:
    venv = NestedVenv(test_venv)

    venv.create()
    venv.create()

    # Check that the venv was created and has the right components
    assert test_venv.exists()
    assert venv.python.exists()


def test_delete_venv_when_not_created(test_venv) -> None:
    venv = NestedVenv(test_venv)

    # Confirm that the venv does not yet exist
    assert not test_venv.exists()

    # Nothing should happen here
    venv.delete()

    # Venv should still not exist
    assert not test_venv.exists()


def test_delete_venv_after_creation(test_venv) -> None:
    venv = NestedVenv(test_venv)

    venv.create()

    # Confirm that the venv exists
    assert test_venv.exists()

    venv.delete()

    # Venv should not exist anymore
    assert not test_venv.exists()


def test_delete_venv_after_activation(test_venv) -> None:
    venv = NestedVenv(test_venv)

    venv.create()
    venv.activate()

    # Confirm that the venv exists
    assert test_venv.exists()
    assert venv.is_active()
    assert venv.is_primary()

    venv.delete()

    # Venv should not exist anymore
    assert not test_venv.exists()
    assert not venv.is_active()
    assert not venv.is_primary()


def test_deactivate_not_active(test_venv) -> None:
    venv = NestedVenv(test_venv)

    # Venv is not active
    assert not venv.is_active()

    # Nothing should happen here
    venv.deactivate()

    # Venv should still not be active
    assert not venv.is_active()


def test_is_active_not_active(test_venv) -> None:
    venv = NestedVenv(test_venv)

    # No venv has been created or activated

    assert not venv.is_active()


def test_is_active(test_venv) -> None:
    venv = NestedVenv(test_venv)

    venv.create()
    venv.activate()

    # Venv was activated and should be active
    assert venv.is_active()


def test_inactive_venv_should_not_be_primary(test_venv) -> None:
    venv = NestedVenv(test_venv)

    # No venv has been created or activated

    assert not venv.is_primary()


def test_single_active_venv_is_primary(test_venv) -> None:
    venv = NestedVenv(test_venv)

    venv.create()
    venv.activate()

    assert venv.is_primary()

    venv.deactivate()

    assert not venv.is_primary()


def test_is_primary_two_venvs(test_venv) -> None:
    venv1 = NestedVenv(Path(str(test_venv) + "_1"))
    venv2 = NestedVenv(Path(str(test_venv) + "_2"))

    venv1.create()
    venv2.create()

    # neither venv is active
    assert not venv1.is_primary()
    assert not venv2.is_primary()

    # venv1 is the only active
    venv1.activate()
    assert venv1.is_primary()
    assert not venv2.is_primary()

    # venv1 and venv2 are active, venv2 should be primary
    venv2.activate()
    assert not venv1.is_primary()
    assert venv2.is_primary()

    # only venv2 is active
    venv1.deactivate()
    assert not venv1.is_primary()
    assert venv2.is_primary()

    # venv1 and venv2 active again, but venv1 should be primary
    venv1.activate()
    assert venv1.is_primary()
    assert not venv2.is_primary()

    # neither venv is active
    venv1.deactivate()
    venv2.deactivate()
    assert not venv1.is_primary()
    assert not venv2.is_primary()


def test_pip_install_numpy(test_venv) -> None:
    """This test attempts to install the 'numpy' package from online
    using 'pip'.
    """

    venv = NestedVenv(test_venv)

    venv.create()
    venv.activate()

    venv.pip_install("numpy")

    assert venv.check_package("numpy")


def test_pip_install_e(test_venv, test_assets_path) -> None:
    """This test attempts to self-install this package into a new
    virtual environment using an editable install.
    """

    venv = NestedVenv(test_venv)

    venv.create()
    venv.activate()

    venv.pip_install_e(test_assets_path / "test_project")

    # assert venv.check_package("test_project")
    assert venv.check_package("numpy")


def test_pip_install_r(test_venv, test_assets_path) -> None:
    """This test attempts to self-install this package's requirements.txt
    file into a new virtual environment using
    'pip install -r requirements.txt'.
    """

    venv = NestedVenv(test_venv)

    venv.create()
    venv.activate()

    venv.pip_install_r(test_assets_path / "requirements.txt")

    # assert venv.check_package("test_project")
    assert venv.check_package("numpy")
    assert venv.check_package("requests")


@pytest.mark.individual
@pytest.mark.skip(
    reason=(
        "This nestedvenv method seems to no longer "
        "work with numpy in Python 3.9 after EOL"
    )
)
def test_pip_install_numpy_first_of_two_venvs(test_venv) -> None:
    venv1 = NestedVenv(Path(str(test_venv) + "_1"))
    venv2 = NestedVenv(Path(str(test_venv) + "_2"))

    # Created first, will not be primary
    venv1.create()
    venv1.activate()

    # Created second, will be primary
    venv2.create()
    venv2.activate()

    # Install numpy only into the first, non-primary venv
    venv1.pip_install("numpy")

    # The first venv should have numpy
    assert venv1.check_package("numpy")

    # The second, primary venv should not
    assert not venv2.check_package("numpy")


@pytest.mark.individual
@pytest.mark.skip(
    reason=(
        "This nestedvenv method seems to no longer "
        "work with numpy in Python 3.9 after EOL"
    )
)
def test_pip_install_numpy_two_versions(test_venv) -> None:
    venv1 = NestedVenv(Path(str(test_venv) + "_1"))
    venv2 = NestedVenv(Path(str(test_venv) + "_2"))

    # Created first, will not be primary
    venv1.create()
    venv1.activate()

    # Created second, will be primary
    venv2.create()
    venv2.activate()

    if sys.version_info[:2] >= (3, 12):
        numpy_version_1 = "2.0"
        numpy_version_2 = "1.26"
    elif sys.version_info[:2] >= (3, 9):
        numpy_version_1 = "1.25"
        numpy_version_2 = "1.24"
    else:
        raise RuntimeError("Python versions under 3.9 not supported")

    venv1.pip_install("numpy=={}".format(numpy_version_1))
    venv2.pip_install("numpy=={}".format(numpy_version_2))

    assert venv1.check_package("numpy", "{}.0".format(numpy_version_1))
    assert venv2.check_package("numpy", "{}.0".format(numpy_version_2))

    import numpy  # type: ignore

    assert numpy.__version__ == "{}.0".format(numpy_version_2)

    venv1.deactivate()

    import numpy

    assert numpy.__version__ == "{}.0".format(numpy_version_2)

    venv2.deactivate()
    venv1.activate()

    import numpy

    assert numpy.__version__ == "{}.0".format(numpy_version_1)
