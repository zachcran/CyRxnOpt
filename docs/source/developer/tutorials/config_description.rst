.. _config_schema:

######################################
 Understanding the Config Description
######################################

Every optimizer class implements
:py:meth:`~cyrxnopt.OptimizerABC.OptimizerABC.get_config`, which describes the
configuration options an optimizer accepts. A user-facing program (CLI, web UI,
desktop app, etc.) can call this method to discover what options exist for a
given optimizer, present them to a user, and then pass the user's choices back
to :py:meth:`~cyrxnopt.OptimizerABC.OptimizerABC.set_config`.

This page explains the shape of the data returned by ``get_config()`` and
suggests how each option shape can be mapped to a traditional UI widget when
building a configuration screen on top of CyRxnOpt.

***************************
 Config Description Schema
***************************

``get_config()`` returns a list of dictionaries, one per configuration option.
Each dictionary can contain the following keys:

- ``name`` (required) - The identifier for the option, in ``snake_case``. If an
  option needs separate continuous and categorical variants, ``continuous`` or
  ``categorical`` is prepended to the name (for example,
  ``continuous_feature_names`` and ``categorical_feature_names``).
- ``type`` (required) - A string naming the expected Python type for the value
  of the
- option. This is intended to be language-agnostic enough that a non-Python
  front end can map it to an equivalent native type. Avoid using more complex,
  third-party, or abstracted types, sticking to commonly known types such as
  ``"int"``, ``"str"``, ``"bool"``, ``"list[str]"``, ``"list[list[float]]"``,
  and ``"dict[str,str]"``.
- ``value`` (required) - The default value for the option, matching ``type``.
- ``range`` (optional) - Constrains the allowed values:

  - For numeric types, a two-element ``[min, max]`` bound.
  - For string types, the list of allowed choices.

  If an option is only bounded in one direction (for example, "must be > 0"),
  the convention is to still provide a two-element range using an appropriate
  sentinel for the open side, such as ``[1, sys.maxsize]``.

- ``description`` (optional) - Human-readable text explaining the purpose of the
  option and any caveats. Intended for use as help text or a tooltip in a UI.

The canonical shape for an option with a constrained set of string values looks
like this:

.. code-block:: python

    {
        "name": "direction",
        "type": "str",
        "value": "min",
        "range": ["min", "max"],
    }

``value`` is a single default, and ``range`` is the full set of allowed choices.
A consuming program should generally prefer ``range`` as the source of truth for
what choices are valid.

.. note::

    A ``str``-typed option ``value`` may also be given directly as a list of the
    allowed choices instead of a single default, omitting ``range`` entirely. In
    that form, the first entry in the list is the default choice. For example,
    :py:class:`~OptimizerNMSimplex.OptimizerNMSimplex` and
    :py:class:`~OptimizerSQSnobFit.OptimizerSQSnobFit` describe ``direction``
    as:

    .. code-block:: python

        {
            "name": "direction",
            "type": "str",
            "value": ["min", "max"],
        }

    Both forms are valid and supported by the config description validation
    utilities and by :py:mod:`~cyrxnopt.apps.create_config`, which picks
    ``value[0]`` as the default when ``value`` is a list. When writing a new
    optimizer, prefer the ``value`` + ``range`` form shown above, since it keeps
    "the default" and "the allowed choices" as clearly separate concepts.

*****************************
 Required Configuration Keys
*****************************

:py:meth:`~OptimizerABC.OptimizerABC._validate_config` enforces that every
optimizer's configuration includes:

- ``budget`` - An ``int`` with a ``range``, giving the number of
  evaluations/predictions the optimizer will run. Default the ``range`` to ``[1,
  sys.maxsize]`` if it can be any positive, non-zero integer.
- ``direction`` - A ``str`` (or, for optimizers that support multiple
  objectives, ``list[str]``) describing the optimization direction(s), using
  either of the two forms described above.
- Either the continuous feature descriptors:

  - ``continuous_feature_names`` (``list[str]``)
  - ``continuous_feature_bounds`` (``list[list[float]]``)
  - ``continuous_feature_resolutions`` (``list[float]``)

  or the categorical feature descriptors:

  - ``categorical_feature_names`` (``list[str]``)
  - ``categorical_feature_values`` (``list[list[str]]``)

  or both, if the optimizer supports mixed feature spaces.

Individual optimizers may add further options beyond these (for example,
``xatol`` for :py:class:`~OptimizerNMSimplex.OptimizerNMSimplex` or ``seed`` for
:py:class:`~OptimizerRandom.OptimizerRandom`).

*******************************
 Mapping Options to UI Widgets
*******************************

The combination of ``type`` and the presence/shape of ``range`` is enough to
choose a sensible default widget for most options. The table below gives
suggested mappings for a traditional desktop/web form:

.. list-table::
    :header-rows: 1

    - - Config shape
      - Suggested widget
      - Notes
    - - ``int`` or ``float`` without ``range``
      - Plain numeric input
      - No bounds to enforce client-side.
    - - ``int`` or ``float`` with ``range``
      - Plain numeric input with bound enforcement or slider with an adjacent
        numeric field
      - A slider alone is often too imprecise for scientific values; pairing it
        with a numeric readout/input is recommended. For ``int``, restrict the
        slider/spinner step to whole numbers.
    - - ``bool``
      - Checkbox or toggle switch
      -
    - - ``str`` without choices
      - Single-line text input
      - No validation constraints are known beyond "is a string".
    - - ``str`` with choices (``range`` or ``value`` as a list)
      - Combo box / dropdown / radio group
      - The default choice is ``value`` (or ``value[0]`` for the list form).
    - - ``list[str]`` with ``range``
      - Multi-select list or checkbox group
      -
    - - ``list[str]`` without ``range``
      - Repeatable text input fields, one row per entry
      - Used for open-ended name lists, such as
        ``continuous_feature_names``/``categorical_feature_names``.
    - - ``list[float]``
      - Repeatable numeric input, one row per associated name
      - Typically parallel to a ``list[str]`` of names (for example,
        ``continuous_feature_resolutions`` lines up with
        ``continuous_feature_names``); consider rendering them together as one
        row per feature rather than as two independent lists.
    - - ``list[list[float]]``
      - Paired min/max numeric inputs, repeated per feature
      - Used for ``continuous_feature_bounds``: one ``[min, max]`` row per entry
        in ``continuous_feature_names``.
    - - ``list[list[str]]``
      - Repeatable tag/multi-value input, one group per feature
      - Used for ``categorical_feature_values``: one group of allowed values per
        entry in ``categorical_feature_names``.

.. note::

    Several options are parallel arrays keyed by position rather than by name
    (for example, ``continuous_feature_bounds[i]`` describes the bounds for
    ``continuous_feature_names[i]``). A UI does not need to reproduce this flat
    structure, it is often clearer to present one row per feature name, with the
    bounds/resolution/values as columns on that row, and translate back to
    parallel arrays when calling ``set_config()``.
