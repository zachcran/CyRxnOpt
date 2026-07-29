import unittest
from pydoc import locate
from typing import Any


def validate_config_description(
    test_case: unittest.TestCase, config_desc: list[dict[str, Any]]
) -> None:
    """Validates the general formatting of a config description returned from
    an ``Optimizer.get_config()`` call.

    :param test_case: Unittest test case that has the assertion checks.
    :type test_case: unittest.TestCase
    :param config_desc: Collection of config descriptors
    :type config_desc: list[dict[str, Any]]
    """

    # A config description should be a list of descriptions for each config
    # option of the optimizer
    test_case.assertEqual(type(config_desc), list)

    for description in config_desc:
        # Each config description is a dictionary with relevant information
        test_case.assertEqual(type(description), dict)

        # A description is complete by providing fields for the config option
        # "name", "type", and "value".
        test_case.assertIn("name", description)
        test_case.assertIn("type", description)
        test_case.assertIn("value", description)


def validate_config_description_pytest(
    config_desc: list[dict[str, Any]],
) -> None:
    """Validates the general formatting of a config description returned from
    an ``Optimizer.get_config()`` call.

    :param config_desc: Collection of config descriptors
    :type config_desc: list[dict[str, Any]]
    """

    # A config description should be a list of descriptions for each config
    # option of the optimizer
    assert type(config_desc) is list

    for description in config_desc:
        # Each config description is a dictionary with relevant information
        assert type(description) is dict

        # A description is complete by providing fields for the config option
        # "name", "type", and "value".
        assert "name" in description
        assert "type" in description
        assert "value" in description

    validate_required_configs(config_desc)


def validate_config_description_value(type_str: str, value: Any) -> None:
    """Checks that a default config value is valid based on the type string.

    .. note::

        The type string must be a valid Python type (matching the result of
        ``type(value).__name__``).

    :param type_str: The string describing the type of the config
    :type type_str: str
    :param value: Config default value
    :type value: Any
    """

    value_type = type(value)
    value_type_name = value_type.__name__

    # Certain config types are allowed to have a value given as a list as well
    can_be_list = ["str"]

    if type_str in can_be_list:
        assert (
            value_type_name == type_str or value_type_name.lower() == "list"
        ), f'Value is not of type "{type_str}" or "list": {value_type_name}'

        if value_type is list and len(value) > 0:
            assert type(value[0]).__name__ == type_str
    else:
        assert value_type is locate(type_str)


def validate_required_configs(config_desc: list[dict[str, Any]]) -> None:
    # Check for required keys that have no variations
    required: list[dict[str, Any]] = [
        {"name": "budget", "type": "int"},
    ]

    for req_desc in required:
        found = False
        for description in config_desc:
            # Skip entry if it doesn't match
            if description["name"] != req_desc["name"]:
                continue

            assert description["type"] == req_desc["type"], (
                f"Type for required \"{req_desc['name']}\" config descriptor "
                f"must be \"{req_desc['type']}\", but was \"{description['type']}\"."
            )

            # Multiple value types are accepted for some "type" values
            validate_config_description_value(
                req_desc["type"], description["value"]
            )

            # If this was reached, the required description was found and valid
            found = found or True

        assert (
            found
        ), f"Required config description not found: {req_desc['name']}"

    # Each variation is a set of entries that must all be found
    required_variations: list[list[dict[str, Any]]] = [
        # Continuous feature options
        [
            {
                "name": "continuous_feature_names",
                "type": "list[str]",
                "value": [],
            },
            {
                "name": "continuous_feature_bounds",
                "type": "list[list[float]]",
                "value": [[]],
            },
            {
                "name": "continuous_feature_resolutions",
                "type": "list[float]",
                "value": [],
            },
        ],  # or,
        # Categorial feature options
        [
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
        ],
        # Directions per objective
        [
            {
                "name": "direction",
                "type": "str",
                "value": ["min", "max"],
            },
            {
                "name": "direction",
                "type": "list[str]",
                "value": ["min"],
            },
        ],
    ]

    found_variation = False
    for variation in required_variations:
        found_all_entries = True

        # Ensure we find all required entries in the variation
        for entry in variation:
            found_entry = False

            # Perform a linear search for the entry in the config descriptors
            for description in config_desc:
                # Skip entry if it doesn't match
                if description["name"] != req_desc["name"]:
                    continue

                assert description["type"] == req_desc["type"], (
                    f"Type for required \"{req_desc['name']}\" config descriptor "
                    f"must be \"{req_desc['type']}\""
                )

                # Multiple value types are accepted for some "type" values
                validate_config_description_value(
                    req_desc["type"], description["value"]
                )

                # If this was reached, the required description was found and valid
                found_entry = found_entry or True

            # If a single entry is not found, the search fails
            found_all_entries = found_all_entries and found_entry
            # Exit early if an entry was not found
            assert (
                found_all_entries
            ), f"Missing config description variation entry: {req_desc['name']}"

        found_variation = found_variation or found_all_entries

        # Check that at least one variation was found
        assert found_variation, (
            "No valid required variations of config descriptions found: "
            f"{req_desc['name']}"
        )
