.. _developer_development_environment:

#########################
 Development Environment
#########################

******************
 Getting the Code
******************

1. Create an user account on GitHub if you do not already have one.
2. Fork the `CyRxnOpt repository <https://github.com/RxnRover/CyRxnOpt>`_ on
   GitHub: click on the *Fork* button near the top of the page. This creates a
   copy of the code under your account on GitHub.
3. Clone this fork copy to your local disk:

   ::

       git clone git@github.com:YourLogin/cyrxnopt.git
       cd cyrxnopt

***************
 Initial Setup
***************

1. Create a virtual environment for the project installs:

   .. code-block:: bash

       python -m venv venv

   And activate it:

   .. code-block:: bash

       source venv/bin/activate # For Linux (and probably Mac)

   .. code-block:: powershell

       .\venv\Scripts\activate  # For Windows

2. Import the package as an editable install to capture your changes in
   realtime:

   .. code-block:: bash

       pip install -e .

3. Install `pre-commit <https://pre-commit.com/>`_:

   .. code-block:: bash

       pip install pre-commit
       pre-commit install

   ``cyrxnopt`` comes with a lot of hooks configured to automatically help the
   developer to check the code being written. Any time you run ``git commit``,
   pre-commit is going to help check and format your code before the commit is
   allowed to succeed.

4. Install `tox <https://tox.wiki/en/stable/>`_:

   .. code-block:: bash

       pip install tox

   ``tox`` is the tool we use to automate every process we can. Instead of each
   developer creating helper scripts for things like building and viewing the
   documentation, running unit tests, and formatting code, these common actions
   are captured through tox commands. To get a full list of commands, run ``tox
   -av`` in the repository.
