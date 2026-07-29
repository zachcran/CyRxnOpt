.. _glossary:

##########
 Glossary
##########

.. glossary::

    budget
       A user-provided number of :term:`optimization steps <optimization step>`
       to be attempted before abandoning the :term:`optimization cycle`.

    CyRxnOpt ID
        The *exact* identifier of an optimizer to use when an optimizer name is required when calling a CyRxnOpt function.

    experiment
        In the context of reaction optimization, we consider an experiment to be
        one :term:`optimization cycle`.

    experiment directory
       Directory containing all files generated for a specific
       :term:`experiment`.

    objective function
       The function you wish to minize or maximize in your optimization problem.
       In reaction optimization, this is typically your reaction, where reaction
       parameters are function input and reaction analysis is the function output
       (yield, conversion %, or more complex results).

    optimization cycle
       When optimizing a reaction or function, an optimization cycle is
       considered to be all:term:`optimization steps <optimization step>` from
       the start of the optimization until either an optimum satisfying the
       algorithm's stop conditions is found or the :term:`budget` is reached.

    optimization iteration
       See :term:`optimization step`.

    optimization step
       Optimization algorithms work by suggesting a set of parameter values that
       are evaluated on an :term:`objective function`. The result is provided
       back to the optimizer and the algorithm determines the next set of
       paramter values to provide.
