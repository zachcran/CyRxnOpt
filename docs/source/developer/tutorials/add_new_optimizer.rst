.. _add_new_optimizer:

################################
 Creating a New Optimizer Class
################################

1. Make a copy of ``OptimizerTemplate.py`` and rename it as
   ``OptimizerName.py``, replacing ``Name`` with the name or an abbreviation of
   your optimizer. For example, if this template was being used to add support
   for the optimizer, Nelder-Mead Simplex, we may rename
   ``OptimizerTemplate.py`` to ``OptimizerNMSimplex.py``. You can download the
   file here: :download:`OptimizerTemplate.py <OptimizerTemplate.py>`. It can
   also be found in the CyRxnOpt repository at
   ``docs/source/developer/tutorials/OptimizerTemplate.py``.
2. Change the class name to your optimizer class name, for example,
   ``OptimizerName``.

   .. literalinclude:: add_new_optimizers.py.snippets
       :lines: 1
       :language: python

3. Add all the necessary libraries required for your optimizer to the
   ``__packages`` list in the template file.

   .. literalinclude:: add_new_optimizers.py.snippets
       :lines: 5
       :language: python

4. Check that the ``install()`` and ``check_install()`` functions do not need to
   be modified:

   ``install()`` - This function will install an optimizer and its dependencies
   optimizer class. When we run an optimizer for the first time, the install
   function will create a new virtual environment to contain the installation,
   then install all the packages using pip. When we use an optimizer, it will
   activate the relevant virtual environment.

   ``check_install()`` - This function checks whether necessary packages are
   installed or not.

5. In the ``get_config()`` function, you need to update the configuration
   dictionary. This dictionary serves as a description of the configuration
   options for an optimization algorithm so user-facing programs can dynamically
   adjust the offered configuration options for different optimization
   algorithms. Here you can add more variables that are only used by your
   algorithm and it should dynamically change the front-end user interface.

   Add all the necessary configurations and variables required as user input to
   run your optimizer. Follow the same dictionary keys as other optimizer
   classes. The following is an example ``get_config`` dictionary with extra
   options added:

   .. literalinclude:: add_new_optimizers.py.snippets
       :lines: 8-50
       :language: python

6. In the ``set_config()`` function, you need to add the necessary code to
   handle and initialize the optimizer. This function handles configuring an
   optimizer before training or prediction begins. Code to generate your
   reaction space, handle the format of configuration data into your algorithm
   format, and generate initial files will go inside ``set_config()`` function.
7. If your optimizer requires training steps, add the necessary code for
   training inside the ``train()`` function. For example, AMLRO requires
   training the initial ML model before starting the active learning prediction.
   Therefore, the AMLRO optimizer class ``train()`` function includes code to
   generate training dataset and perform each training step.
8. In the ``predict()`` function, your algorithm should be called to find the
   optimal reaction conditions. This function will return the suggested reaction
   conditions that should be run in next cycle. Actual optimization
   loop/prediction step code should be implemented here.
9. In the ``_import_deps()`` function, write the necessary package import lines.
   Each package should be added to the ``_imports`` dictionary, and for the
   dictionary key, use the package name. As a example, ``numpy`` and ``pandas``
   are imported here:

   .. literalinclude:: add_new_optimizers.py.snippets
       :lines: 54-59
       :language: python

   Then, when you want to use the imported library, you can access it through
   the ``self._imports`` dictionary:

   .. literalinclude:: add_new_optimizers.py.snippets
       :lines: 62-63
       :language: python

10. Depending on your optimizer workflow, add more class methods as necessary.
    Refer to how existing optimizer classes are defined for guidance.

**********************************
 Adding New Optimizer to CyRxnOpt
**********************************

After implementing your optimizer class, update the ``OptimizerController.py``
file to use your optimizer.

1. At the top of this file, add the optimizer import line, replacing
   ``OptimizerName`` with the name of your optimizer class:

   .. literalinclude:: add_new_optimizers.py.snippets
       :lines: 65
       :language: python

2. Update the ``get_optimizer()`` function to include your optimizer:

   .. literalinclude:: add_new_optimizers.py.snippets
       :lines: 69-70
       :language: python

3. All function parameters should match with the corresponding abstract function
   defined in ``OptimizerABC``. If you want to add a new parameter for any
   function, first add that to ``OptimizerController`` and ``OptimizerABC``,
   then give the default value as ``None``. For example, if your algorithm
   predict function requires a new parameter, learning rate:

   .. literalinclude:: add_new_optimizers.py.snippets
       :lines: 73-82
       :language: python
