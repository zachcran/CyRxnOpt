|Documentation|
|Build Status|
|Generated with Pyscaffold|

.. |Build Status| image:: https://github.com/RxnRover/CyRxnOpt/actions/workflows/unit_testing.yml/badge.svg
    :alt: Build Status
    :target: https://github.com/RxnRover/CyRxnOpt/actions/workflows/unit_testing.yml

.. |Documentation| image:: https://img.shields.io/badge/Documentation-slategrey
    :alt: Documentation link
    :target: https://rxnrover.github.io/CyRxnOpt/

.. |Generated with Pyscaffold| image:: https://img.shields.io/badge/-PyScaffold-005CA0?logo=pyscaffold
    :alt: Project generated with PyScaffold
    :target: https://pyscaffold.org/

..
    These are examples of badges you might want to add to your README:
    please update the URLs accordingly

     .. image:: https://api.cirrus-ci.com/github/<USER>/cyrxnopt.svg?branch=main
         :alt: Built Status
         :target: https://cirrus-ci.com/github/<USER>/cyrxnopt
     .. image:: https://readthedocs.org/projects/cyrxnopt/badge/?version=latest
         :alt: ReadTheDocs
         :target: https://cyrxnopt.readthedocs.io/en/stable/
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
     .. image:: https://img.shields.io/twitter/url/http/shields.io.svg?style=social&label=Twitter
         :alt: Twitter
         :target: https://twitter.com/cyrxnopt

.. .. image:: https://api.cirrus-ci.com/github/RxnRover/pyoptimizer_backend.svg?branch=main
..     :alt: Built Status
..     :target: https://cirrus-ci.com/github/RxnRover/pyoptimizer_backend

CyRxnOpt
========

    CyRxnOpt provides a single interface to use many reaction optimization
    algorithms.

- optimization algorithms have different user interfaces, from web portals to
  software-only interfaces
- when targeting reaction optimization, the algorithms are expected to be used
  in the lab, likely by someone without much programming experience
- trying different algorithms means potentially learning multiple installation
  methods, user interfaces, and data formats
- CyRxnOpt aims to provide a single software interface that can provide access
  to many different reaction optimization algorithms
- this allows users to program to a single software interface, simplifying the
  development of user-friendly tools and interfaces to lower the barrier of
  entry into reaction optimization

.. _cyrxnopt_overview_install:

Installation and Usage
----------------------

CyRxnOpt is a Python-based library available for installation from PyPI
using ``pip``:

.. code-block:: bash

   pip install cyrxnopt

.. todo::

   Can we easily make this available through conda as well? That would
   be advantageous, but not strictly necessary.


.. _cyrxnopt_overview_cli_install:

Installing an Optimizer
~~~~~~~~~~~~~~~~~~~~~~~

The first thing to do when using CyRxnOpt is to create an :term:`experiment
directory`. The experiment directory will contain the optimizer installation,
optimizer configuration files, reaction data, and other auxiliary files needed
over the course of an optimization. By default, an instance of the optimization
algorithm will be installed in each experiment directory to provide a snap shot
of the software used at the time of the experiment. Sometimes these duplicate
installations can become too large, so it is also possible to provide an
alternative installation location for an algorithm, provided it was put there
using the following ``install`` command so it has the correct structure.

An optimizer can be installed using the ``install`` command.
Using a :ref:`supported optimizer name<supported_optimizer_list>`, the
``install`` command will install the given optimization algorithm into a
subdirectory to be used by future commands. The following command installs
the Nelder-Mead Simplex algorithm (NMSimplex), a classic, local optimization
technique applied in early reaction optimization studies.

.. code-block:: bash

   # Installs the Nelder-Mead Simplex algorithm inside of the directory
   # `./examples/nmsimplex_example`
   install nmsimplex ./examples/nmsimplex_example

.. todo::

   We need to actually make this install command.


.. _cyrxnopt_overview_cli_config:

Configuring an Optimizer
~~~~~~~~~~~~~~~~~~~~~~~~

Once we have the NMSimplex algorithm installed, we can set up the directory
to store data related to a reaction optimization campaign. This
data starts with the specific configuration of the optimizer. At a minimum,
this includes the reaction parameters that the optimizer should change,
parameter boundaries, the maximum number of reactions to attempt (budget),
and the optimization direction (maximize or minimize).

To create a default configuration file, use the ``create_config`` command.
This will create a ``default_config.json`` file at the given experiment
directory, in this example, ``./examples/nmsimplex_example``. Note that this
is different than where we installed the algorithm! One algorithm installation
can typically be used for many different experiments.

.. code-block:: bash

   create_config nmsimplex ./examples/nmsimplex_example

Let's say we make a copy of ``default_config.json`` at
``./examples/nmsimplex_example/my_config.json`` and change some options in the
file. We then use the ``configure_optimizer`` command to configure NMSimplex
for our experiment based on the options in the modified ``my_config.json``
file.

.. code-block:: bash

   cd ./examples/nmsimplex_example
   configure_optimizer nmsimplex ./examples/nmsimplex_example/

The behavior of ``configure_optimizer`` will vary per optimizer being used.
Some optimizers require additional files that are created here, but for
NMSimplex the formatting is simply checked to make sure the settings can
be properly read during usage.


.. _cyrxnopt_overview_cli_training:

Training an Optimizer
~~~~~~~~~~~~~~~~~~~~~

.. todo::

   write me!

TODO

.. _cyrxnopt_overview_cli_prediction:

Optimizing a Function
~~~~~~~~~~~~~~~~~~~~~

.. todo::

   write me!

This is where the optimizer prediction will be described.


API Usage
---------

For API usage, see :ref:`api_usage`.

CyRxnOpt is a Python-based library available for installation from PyPI using
``pip``:

.. code-block:: bash

    pip install cyrxnopt

.. todo::

    Can we easily make this available through conda as well? That would
    be advantageous, but not strictly necessary.

.. _pyscaffold-notes:

Making Changes & Contributing
-----------------------------

This project uses `pre-commit`_, please make sure to install it before making
any changes or you will not be able to make commits!!!

.. code-block:: bash

   pip install pre-commit
   cd cyrxnopt
   pre-commit install

It is a good idea to update the hooks to the latest version:

.. code-block:: bash

   pre-commit autoupdate

Don't forget to tell your contributors to also install and use pre-commit.

.. _pre-commit: https://pre-commit.com/


Note
----

This project has been set up using PyScaffold 4.3.1. For details and usage
information on PyScaffold see https://pyscaffold.org/.
