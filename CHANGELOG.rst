###########
 Changelog
###########

All notable changes to this project will be documented in this file.

The format is based on `Keep a Changelog
<https://keepachangelog.com/en/2.0.0/>`_, and this project adheres to `Semantic
Versioning <https://semver.org/spec/v2.0.0.html>`_.

*************
 Unreleased_
*************

- None yet

*********************
 1.0.0_ - 2026-07-28
*********************

Added
=====

- CLI commands as ``cyrxnopt <subcommand>``
- Unified behavioral interface functions: ``train_server`` and
  ``predict_server``
- Initial benchmarking paper optimizers: - AMLRO, EDBO+, Nelder-Mead Simplex,
  and SQSnobFit - Random sampling optimizer for baseline comparison
- Major code cleanup (formatting, linting, bug fixes, etc.)
- Significant docstring and documentation additions

Changed
=======

- Updated testing for all optimizers

.. Reference links

.. _1.0.0: https://github.com/RxnRover/cyrxnopt/releases/tag/v1.0.0

.. _dulithaprasanna: https://github.com/dulithaprasanna

.. _semver: https://semver.org

.. _unreleased: https://github.com/RxnRover/cyrxnopt/compare/v1.0.0...HEAD

.. _zachcran: https://github.com/zachcran
