import pandas as pd
import pytest

from cyrxnopt.NestedVenv import NestedVenv
from cyrxnopt.OptimizerRandom import OptimizerRandom
from tests.cyrxnopt.utilities_for_testing.validate_config_description import (
    validate_config_description_pytest,
)


@pytest.fixture(scope="session")
def venv_random(tmp_path_factory):
    venv_path = tmp_path_factory.mktemp("venv_random")

    test_venv = NestedVenv(venv_path)

    # No dependencies to install for random sampling, but the install/check
    # flow is still exercised for interface compatibility.
    opt = OptimizerRandom(test_venv)
    opt.venv_worker.create()
    opt.install()
    assert opt.check_install()

    yield test_venv

    opt.venv_worker.delete()


def _base_config(seed=None):
    config = {
        "continuous_feature_names": ["f1", "f2"],
        "continuous_feature_bounds": [[-1, 1], [0, 10]],
        "continuous_feature_resolutions": [0.1, 0.1],
        "categorical_feature_names": ["f3"],
        "categorical_feature_values": [["a", "b", "c"]],
        "direction": ["min"],
        "budget": 10,
        "objective": ["yield"],
    }

    if seed is not None:
        config["seed"] = seed

    return config


def test_get_config_returns_valid_description_list(venv_random) -> None:
    opt = OptimizerRandom(venv_random)

    result = opt.get_config()

    validate_config_description_pytest(result)


def test_set_config_creates_correct_files(venv_random, tmp_path) -> None:
    opt = OptimizerRandom(venv_random)

    config = _base_config()

    opt.set_config(str(tmp_path), config)

    assert (tmp_path / "config.json").exists()
    assert (tmp_path / opt._results_filename).exists()

    with open(tmp_path / opt._results_filename) as fin:
        header = fin.readline().strip()
        assert header == "f1,f2,f3,yield"


def test_train_does_nothing(venv_random, tmp_path) -> None:
    opt = OptimizerRandom(venv_random)
    expected_suggestion = []

    suggestion = opt.train([], 0, tmp_path, {})

    assert expected_suggestion == suggestion


def test_predict_returns_values_within_bounds(venv_random, tmp_path) -> None:
    opt = OptimizerRandom(venv_random)
    config = _base_config()

    opt.set_config(str(tmp_path), config)

    next_params: list = []
    result = 0.0

    for _ in range(5):
        next_params = opt.predict(next_params, result, str(tmp_path), config)
        result = 1.0

        assert len(next_params) == 3
        assert -1 <= next_params[0] <= 1
        assert 0 <= next_params[1] <= 10
        assert next_params[2] in ["a", "b", "c"]


def test_predict_records_results_in_order(venv_random, tmp_path) -> None:
    opt = OptimizerRandom(venv_random)
    config = _base_config()

    opt.set_config(str(tmp_path), config)

    next_params: list = []
    result = 0
    suggestions = []

    for _ in range(4):
        next_params = opt.predict(next_params, result, str(tmp_path), config)
        suggestions.append(list(next_params))
        result += 1

    results = pd.read_csv(tmp_path / "results.csv")

    # Four predict() calls means three completed reactions were recorded (the
    # 4th suggestion has not been performed yet, so it isn't recorded).
    assert len(results) == 3

    expected_result = 1
    for i in range(3):
        row = results.iloc[i]
        assert row["f1"] == pytest.approx(suggestions[i][0])
        assert row["f2"] == pytest.approx(suggestions[i][1])
        assert row["f3"] == suggestions[i][2]
        assert row["yield"] == pytest.approx(expected_result)
        expected_result += 1


def test_predict_is_reproducible_with_seed(
    venv_random, tmp_path_factory
) -> None:
    opt_1 = OptimizerRandom(venv_random)
    opt_2 = OptimizerRandom(venv_random)

    def run(opt, location) -> list:
        config = _base_config(seed=42)
        opt.set_config(str(location), config)

        next_params: list = []
        result = 0.0
        history = []

        for _ in range(3):
            next_params = opt.predict(
                next_params, result, str(location), config
            )
            history.append(list(next_params))
            result = 1.0

        return history

    results_1 = run(opt_1, tmp_path_factory.mktemp("random_seed_a"))
    results_2 = run(opt_2, tmp_path_factory.mktemp("random_seed_b"))

    assert results_1 == results_2


def test_predict_categorical_only(venv_random, tmp_path) -> None:
    opt = OptimizerRandom(venv_random)
    config = _base_config()
    # Clear continuous settings
    config["continuous_feature_names"] = []
    config["continuous_feature_bounds"] = []
    config["continuous_feature_resolutions"] = []
    # Add categorial settings
    config["categorical_feature_names"] = ["catalyst"]
    config["categorical_feature_values"] = [["A", "B", "C"]]

    opt.set_config(str(tmp_path), config)

    result = opt.predict([], 0, str(tmp_path), config)

    assert len(result) == 1
    assert result[0] in ["A", "B", "C"]
