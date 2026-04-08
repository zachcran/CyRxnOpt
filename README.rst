.. image:: https://github.com/RxnRover/CyRxnOpt/actions/workflows/unit_testing.yml/badge.svg
    :alt: Build Status
    :target: https://github.com/RxnRover/CyRxnOpt/actions/workflows/unit_testing.yml

.. image:: https://img.shields.io/badge/Documentation-grey
    :alt: Documentation link
    :target: https://rxnrover.github.io/CyRxnOpt/

.. image:: https://img.shields.io/badge/-PyScaffold-005CA0?logo=pyscaffold
    :alt: Project generated with PyScaffold
    :target: https://pyscaffold.org/

.. image:: https://img.shields.io/badge/Python-3.9-blue
    :alt: Documentation link
    :target: https://rxnrover.github.io/CyRxnOpt/

.. image:: https://img.shields.io/badge/ChemRxiv-Preprint-lightgray
    :alt: ChemRxiv Preprint DOI
    :target: https://doi.org/10.26434/chemrxiv.15001645/v1

..
    These are examples of badges you might want to add to your README:
    please update the URLs accordingly

     .. image:: https://img.shields.io/coveralls/github/<USER>/cyrxnopt/main.svg
         :alt: Coveralls
         :target: https://coveralls.io/r/<USER>/cyrxnopt
     .. image:: https://img.shields.io/pypi/v/cyrxnopt.svg
         :alt: PyPI-Server
         :target: https://pypi.org/project/cyrxnopt/
     .. image:: https://img.shields.io/conda/vn/conda-forge/cyrxnopt.svg
         :alt: Conda-Forge
         :target: https://anaconda.org/conda-forge/cyrxnopt
     .. image:: https://pepy.tech/badge/cyrxnopt/month
         :alt: Monthly Downloads
         :target: https://pepy.tech/project/cyrxnopt

##########
 CyRxnOpt
##########

    CyRxnOpt provides a single interface to use many reaction optimization
    algorithms.

Numerous cutting-edge machine learning algorithms have been developed in recent
years for efficiently optimizing chemical processes. While many are open-source,
evaluating and applying them to chemical processes remains challenging due to
varying, non-standard implementations and interfaces. CyRxnOpt has been
developed as a general, Python-based interface to install, use, and switch
between reaction optimization algorithms under a single software interface. By
integrating optimizers with the CyRxnOpt interface, many state-of-the-art
reaction optimization algorithms can be more easily used in other software and
workflows.

.. _cyrxnopt_overview_install:

************************
 Installation and Usage
************************

CyRxnOpt is a Python-based library available for installation from *PyPI* using
``pip``:

.. code-block:: bash

    pip install cyrxnopt

Further instructions can be found in `the documentation
<https://rxnrover.github.io/CyRxnOpt/overview/installation.html>`__.

.. _cyrxnopt_overview_cli_install:

Installing an Optimizer
=======================

The first thing to do when using CyRxnOpt is to create an experiment directory.
The experiment directory will contain the optimizer installation, optimizer
configuration files, reaction data, and other auxiliary files needed over the
course of an optimization. By default, an instance of the optimization algorithm
will be installed in each experiment directory to provide a snap shot of the
software used at the time of the experiment. Sometimes these duplicate
installations can become too large, so it is also possible to provide an
alternative installation location for an algorithm, provided it was put there
using the following ``install_optimizer`` command so it has the correct
structure.

An optimizer can be installed using the ``install_optimizer`` command. Using a
`supported optimizer name
<https://rxnrover.github.io/CyRxnOpt/supported_algorithms.html>`__, the
``install_optimizer`` command will install the given optimization algorithm into
a subdirectory to be used by future commands. The following command installs the
Nelder-Mead Simplex algorithm (NMSimplex), a classic, local optimization
technique applied in early reaction optimization studies.

.. code-block:: bash

    # Installs the Nelder-Mead Simplex algorithm inside of the directory
    # `./examples/nmsimplex_example`
    install_optimizer nmsimplex -l ./examples/nmsimplex_example

.. _cyrxnopt_overview_cli_config:

Configuring an Optimizer
========================

Once we have the NMSimplex algorithm installed, we can set up the directory to
store data related to a reaction optimization campaign. This data starts with
the specific configuration of the optimizer. At a minimum, this includes the
reaction parameters that the optimizer should change, parameter boundaries, the
maximum number of reactions to attempt (budget), and the optimization direction
(maximize or minimize).

To create a default configuration file, use the ``create_config`` command. This
will create a ``default_config.json`` file at the given experiment directory, in
this example, ``./examples/nmsimplex_example``. Note that this is different than
where we installed the algorithm! One algorithm installation can typically be
used for many different experiments.

.. code-block:: bash

    create_config nmsimplex -l ./examples/nmsimplex_example

Let's say we make a copy of ``default_config.json`` at
``./examples/nmsimplex_example/my_config.json`` and change some options in the
file. We then use the ``configure_optimizer`` command to configure NMSimplex for
our experiment based on the options in the modified ``my_config.json`` file.

.. code-block:: bash

    cd ./examples/nmsimplex_example
    configure_optimizer nmsimplex -c my_config.json

The behavior of ``configure_optimizer`` will vary per optimizer being used. Some
optimizers require additional files that are created here, but for NMSimplex the
formatting is simply checked to make sure the settings can be properly read
during usage.

.. _cyrxnopt_overview_cli_training:

Training an Optimizer
=====================

Once the optimizer is configured, if training is needed, the ``train_optimizer``
command can be run. A default of 20 training steps are used, which can be
changed with the ``-t`` flag. This is not needed for the NMSimplex algorithm,
resulting in a no-op if ``train_optimizer`` is called.

.. code-block:: bash

    # If not already there
    cd ./examples/nmsimplex_example

    # Begin training loop
    train_optimizer nmsimplex -c my_config.json -t 20

.. _cyrxnopt_overview_cli_prediction:

Optimizing a Function
=====================

Once trained, if necessary, the optimization loop can be run with
``start_optimization``.

.. code-block:: bash

    # If not already there
    cd ./examples/nmsimplex_example

    # Begin optimization loop
    start_optimization nmsimplex -c my_config.json

***********
 API Usage
***********

For API usage, see `API Reference
<https://rxnrover.github.io/CyRxnOpt/api/modules.html>`__.

.. _contributing:

*******************************
 Making Changes & Contributing
*******************************

This project enforces formatting and style using pre-commit_ and uses tox_ for
project automation. Please make sure to install these before making any changes.

.. code-block:: bash

    # Clone the repo
    git clone https://github.com/RxnRover/CyRxnOpt cyrxnopt

    # Install dev prerequisites
    cd cyrxnopt
    pip install pre-commit tox

    # Install pre-commit hooks
    pre-commit install

A list of useful commands are provided via tox (run with ``tox r -e
<command>``), and can be listed at any time using ``tox l`` in a terminal.

*******
 Paper
*******

Comprehensive comparisons of optimization algorithms are crucial for researchers
to make informed decisions about which algorithm will perform best for their
process, but there is little information comparing how each algorithm performs
on differing chemical processes. To demonstrate the use and flexibility of
CyRxnOpt, it was used to access four optimization algorithms and benchmark their
performance on standard optimization functions and reaction models built from
experimental datasets, providing a benchmarking framework which we plan to
expand to more optimization algorithms.

ChemRxiv Preprint: https://doi.org/10.26434/chemrxiv.15001645/v1

Please cite preprint as: Zachery Crandall, Dulitha P. Kulathunga, Lun An, et al.
CyRxnOpt: Generalized Interface for Benchmarking Reaction Optimization
Algorithms. *ChemRxiv*. 06 April 2026. DOI:
https://doi.org/10.26434/chemrxiv.15001645/v1

.. _pyscaffold-note:

******
 Note
******

This project has been set up using PyScaffold 4.3.1. For details and usage
information on PyScaffold see pyscaffold_.

.. _pre-commit: https://pre-commit.com/

.. _pyscaffold: https://pyscaffold.org/

.. _tox: https://tox.wiki/en/latest/
