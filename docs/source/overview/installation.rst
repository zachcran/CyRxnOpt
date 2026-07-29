.. _installation:

##############
 Installation
##############

To utilize the CyRxnOpt Library, follow the steps below for either pip or manual
installation:

*********
 via Pip
*********

1. If you have not already, it is recommended to use a virtual environment for
   your project:

   .. code-block:: bash

       python -m venv venv

2. If you created a virtual environment, activate it:

   .. code-block:: bash

       source venv/bin/activate  # On Unix or MacOS
       .\venv\Scripts\activate   # On Windows

3. Install the CyRxnOpt library from PyPI using ``pip``:

   .. code-block:: bash

       pip install cyrxnopt

   .. note::

       You can also add ``cyrxnopt`` to your project's dependency list in
       ``requirements.txt``, ``pyproject.toml``, or ``setup.cfg`` for automatic
       installation with your project.

**************************
 via Source Code (Manual)
**************************

1. Clone the repository:

   .. code-block:: bash

       git clone https://github.com/RxnRover/CyRxnOpt.git

2. Navigate to the library directory:

   .. code-block:: bash

       cd CyRxnOpt

3. Create a virtual environment:

   .. code-block:: bash

       python -m venv venv

4. Activate the virtual environment:

   .. code-block:: bash

       source venv/bin/activate  # On Unix or MacOS
       .\venv\Scripts\activate   # On Windows

5. Install the library:

   .. code-block:: bash

       pip install .
