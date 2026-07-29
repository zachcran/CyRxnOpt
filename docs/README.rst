###########################
 Viewing the Documentation
###########################

This guide outlines the steps to build and view the documentation on your local
computer. Python needs to be installed and you must already have the CyRxnOpt
repository cloned to your computer.

In your copy of the CyRxnOpt code, create a virtual environment and install `tox
<https://tox.wiki/en/stable/>`_ into it:

.. code-block:: bash

    python -m venv venv       # Create venv
    source venv/bin/activate  # Activate venv

    pip install tox           # Install tox

With ``tox`` installed, it is a single command to compile the documentation and
host it on your local computer for viewing:

.. code-block:: bash

    tox run -e viewdocs

Navigate to ``localhost:3000`` to view the documentation website.

.. note::

    The port that the documentation website is hosted on can be changed with:

    .. code-block:: bash

        tox run -e viewdocs --override testenv:viewdocs.setenv+=PORT=<desired_port_number>
