from collections.abc import Generator

import pytest

from cyrxnopt.NestedVenv import NestedVenv
from cyrxnopt.OptimizerAmlro import OptimizerAmlro
from tests.cyrxnopt.utilities_for_testing.validate_config_description import (
    validate_config_description_pytest,
)


@pytest.fixture(scope="session")
def venv_amlro(tmp_path_factory) -> Generator[NestedVenv]:
    venv_path = tmp_path_factory.mktemp("venv_amlro")

    test_venv = NestedVenv(venv_path)

    test_venv.create()
    test_venv.activate()

    # Preinstall dependencies
    opt = OptimizerAmlro(test_venv)
    opt.install()
    assert opt.check_install()

    yield test_venv

    test_venv.deactivate()
    assert not test_venv.is_active()
    test_venv.delete()


def test_get_config_returns_valid_description_list(venv_amlro):
    opt = OptimizerAmlro(venv_amlro)

    result = opt.get_config()

    validate_config_description_pytest(result)


def test_set_config_creates_correct_config(venv_amlro, tmp_path):
    opt = OptimizerAmlro(venv_amlro)

    config = {
        "continuous_feature_names": ["f1", "f2"],
        "continuous_feature_bounds": [[-1, 1], [-5, 5]],
        "continuous_feature_resolutions": [1, 5, 1],
        "categorical_feature_names": ["f3"],
        "categorical_feature_values": [["a", "b", "c"]],
        "budget": 10,
        "objectives": ["yield"],
        "direction": "min",
    }

    opt.set_config(str(tmp_path), config)

    # Check if files were created during config
    assert (tmp_path / "full_combo_file.txt").exists()
    assert (tmp_path / "training_combo_file.txt").exists()
    assert (tmp_path / "training_set_decoded_file.txt").exists()
    assert (tmp_path / "training_set_file.txt").exists()


def test_train_call(venv_amlro, tmp_path):
    opt = OptimizerAmlro(venv_amlro)
    config = {
        "continuous_feature_names": ["f1", "f2"],
        "continuous_feature_bounds": [[-1, 1], [-1, 1]],
        "continuous_feature_resolutions": [0.1, 0.1],
        "categorical_feature_names": ["f3"],
        "categorical_feature_values": [[0, 1, 2]],
        "direction": "min",
        "budget": 10,
        "objectives": ["yield"],
    }

    opt.set_config(str(tmp_path), config)
    suggestion = opt.train([], 0, tmp_path, config)

    # Can't check exact values since random sampling is used
    assert len(suggestion) == 3


def test_predict_basic_run(venv_amlro, tmp_path, obj_func_3d):
    import pandas as pd

    opt = OptimizerAmlro(venv_amlro)
    config = {
        "continuous_feature_names": ["f1", "f2"],
        "continuous_feature_bounds": [[-1, 1], [-1, 1]],
        "continuous_feature_resolutions": [0.1, 0.1],
        "categorical_feature_names": ["f3"],
        "categorical_feature_values": [[0, 1, 2]],
        "direction": "min",
        "budget": 10,
        "objectives": ["yield"],
    }

    # Set up the necessary files
    opt.set_config(tmp_path, config)

    # Perform training
    next_params: list[float] = []
    result = 0
    for i in range(20):
        next_params = opt.train(next_params, result, tmp_path, config)
        result = obj_func_3d(next_params)

    # Run two predict steps; one to get parameters, the next to write the result
    next_params = opt.predict(next_params, result, tmp_path, config)
    result = obj_func_3d(next_params)
    next_params = opt.predict(next_params, result, tmp_path, config)

    # Read the generated dataset so far
    result_training_set = pd.read_csv(tmp_path / "training_set_file.txt")

    # Ensure it is the correct length (20 training + 1 predict)
    assert len(result_training_set) == 21


def test__validate_config_complete_config(venv_amlro):
    opt = OptimizerAmlro(venv_amlro)

    config = {
        "continuous_feature_names": ["f1", "f2"],
        "continuous_feature_bounds": [[-1, 1], [-5, 5]],
        "continuous_feature_resolutions": [1, 5, 1],
        "categorical_feature_names": ["f3"],
        "categorical_feature_values": [["a", "b", "c"]],
        "budget": 10,
        "objectives": ["yield"],
        "direction": "min",
    }

    opt._validate_config(config)


def test__validate_config_continuous_config(venv_amlro):
    opt = OptimizerAmlro(venv_amlro)

    config = {
        "continuous_feature_names": ["f1", "f2"],
        "continuous_feature_bounds": [[-1, 1], [-5, 5]],
        "continuous_feature_resolutions": [1, 5, 1],
        "direction": "min",
        "budget": 10,
    }

    opt._validate_config(config)


def test__validate_config_categorical_config(venv_amlro):
    opt = OptimizerAmlro(venv_amlro)

    config = {
        "categorical_feature_names": ["f3"],
        "categorical_feature_values": [["a", "b", "c"]],
        "budget": 10,
        "direction": "min",
    }

    opt._validate_config(config)


def test__validate_config_missing_parts(venv_amlro):
    opt = OptimizerAmlro(venv_amlro)

    config_no_names = {
        "continuous_feature_bounds": [[-1, 1], [-5, 5]],
        "continuous_feature_resolutions": [1, 5, 1],
        "categorical_feature_values": [["a", "b", "c"]],
        "direction": "min",
        "budget": 10,
    }

    with pytest.raises(RuntimeError):
        opt._validate_config(config_no_names)

    config_no_continuous_feature_bounds_or_res = {
        "continuous_feature_names": ["f1", "f2"],
        "direction": "min",
        "budget": 10,
    }

    with pytest.raises(RuntimeError):
        opt._validate_config(config_no_continuous_feature_bounds_or_res)

    config_no_categorical_feature_values = {
        "categorical_feature_names": ["f3"],
        "direction": "min",
        "budget": 10,
    }

    with pytest.raises(RuntimeError):
        opt._validate_config(config_no_categorical_feature_values)

    config_no_budget = {
        "continuous_feature_names": ["f1", "f2"],
        "continuous_feature_bounds": [[-1, 1], [-5, 5]],
        "continuous_feature_resolutions": [1, 5, 1],
        "categorical_feature_names": ["f3"],
        "categorical_feature_values": [["a", "b", "c"]],
        "direction": "min",
    }

    with pytest.raises(RuntimeError):
        opt._validate_config(config_no_budget)

    config_no_direction = {
        "continuous_feature_names": ["f1", "f2"],
        "continuous_feature_bounds": [[-1, 1], [-5, 5]],
        "continuous_feature_resolutions": [1, 5, 1],
        "categorical_feature_names": ["f3"],
        "categorical_feature_values": [["a", "b", "c"]],
        "budget": 10,
    }

    with pytest.raises(RuntimeError):
        opt._validate_config(config_no_direction)
