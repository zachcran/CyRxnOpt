import subprocess
import sys

import pytest
from git import Repo

from cyrxnopt.NestedVenv import NestedVenv
from cyrxnopt.OptimizerEDBOp import OptimizerEDBOp
from tests.cyrxnopt.utilities_for_testing.validate_config_description import (
    validate_config_description_pytest,
)

skip_libtorch_error = pytest.mark.skipif(
    not sys.platform.startswith("win"),
    reason=(
        "Issue with libtorch_cpu.so on Linux prevents successful import "
        "of EDBO+ during testing."
    ),
)

skip_error_on_install_import = pytest.mark.skip(
    "Currently fails because import will fail in same session as installation."
)


@pytest.fixture(scope="session")
def edboplus_local_path(tmp_path_factory):
    repo_location = tmp_path_factory.mktemp("edboplus")

    # EDBO+ starts to run into installation issues noticed 2025-10-07.
    # This, along with never merging in PR #6 with 40x performance improvements,
    # requires manually downloading an older version/branch of EDBO+.
    Repo.clone_from(
        "https://github.com/zachcran/edboplus",
        repo_location,
        branch="performance_improvements",
    )

    return repo_location


@pytest.fixture(scope="session")
def venv_edbop(tmp_path_factory, edboplus_local_path):
    venv_path = tmp_path_factory.mktemp("venv_edbop")

    test_venv = NestedVenv(venv_path)

    # Preinstall dependencies
    opt = OptimizerEDBOp(test_venv)
    # opt.install(local_paths={"edboplus": edboplus_local_path})
    opt.venv_worker.create()
    opt.venv_worker.pip_install("setuptools<82.0.0")
    opt.venv_worker.pip_install_e(edboplus_local_path)
    assert opt.venv_worker.check_package("setuptools")
    assert opt.venv_worker.check_package("edbo")

    # Patch out execstack issue with libtorch_cpu.so
    subprocess.call(
        [
            "patchelf",
            "--clear-execstack",
            venv_path / "lib/python3.9/site-packages/torch/lib/libtorch_cpu.so",
        ]
    )

    yield test_venv

    opt.venv_worker.delete()


def test_get_config_returns_valid_description_list(venv_edbop) -> None:
    opt = OptimizerEDBOp(venv_edbop)

    result = opt.get_config()

    validate_config_description_pytest(result)


def test_set_config_creates_correct_config(venv_edbop, tmp_path) -> None:
    opt = OptimizerEDBOp(venv_edbop)

    config = {
        "continuous_feature_names": ["f1", "f2"],
        "continuous_feature_bounds": [[-1, 1], [-1, 1]],
        "continuous_feature_resolutions": [0.1, 0.1],
        "categorical_feature_names": ["f3"],
        "categorical_feature_values": [["a", "b", "c"]],
        "direction": ["min"],
        "budget": 10,
        "objectives": ["yield"],
    }

    opt.set_config(str(tmp_path), config)

    # Check if config file was created
    assert (tmp_path / "my_optimization.csv").exists()
    assert (tmp_path / "reaction_order.csv").exists()


def test_train_does_nothing(venv_edbop, tmp_path) -> None:
    opt = OptimizerEDBOp(venv_edbop)
    expected_suggestion = []

    suggestion = opt.train([], 0, tmp_path, {})

    assert expected_suggestion == suggestion


def test_predict_basic_run(venv_edbop, tmp_path, obj_func_3d) -> None:
    import pandas as pd

    opt = OptimizerEDBOp(venv_edbop)
    config = {
        "continuous_feature_names": ["f1", "f2"],
        "continuous_feature_bounds": [[-1, 1], [-1, 1]],
        "continuous_feature_resolutions": [0.1, 0.1],
        "categorical_feature_names": ["f3"],
        "categorical_feature_values": [[0, 1, 2]],
        "direction": ["min"],
        "budget": 10,
        "objectives": ["yield"],
    }
    opt.set_config(str(tmp_path), config)

    next_params: list[float] = []
    result = 0

    next_params = opt.predict(next_params, result, tmp_path, config)
    result = obj_func_3d(next_params)
    next_params = opt.predict(next_params, result, tmp_path, config)

    # Read the generated dataset so far
    result_training_set = pd.read_csv(tmp_path / "reaction_order.csv")

    # Ensure it is the correct length (20 training + 1 predict)
    assert len(result_training_set) == 1
