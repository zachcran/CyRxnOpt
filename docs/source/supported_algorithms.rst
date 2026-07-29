.. _supported-algorithms:

######################
 Supported Algorithms
######################

CyRxnOpt supports a variety of state-of-the-art optimization algorithms, ranging
from traditional methods to modern machine learning-driven approaches. These
algorithms enable efficient exploration of reaction condition landscapes, local
and global search strategies, and single- or multi-objective decision-making.

Below are sections briefly describing each supported algorithm, along with the
:term:`CyRxnOpt ID` associated with each method in CyRxnOpt.

*******
 AMLRO
*******

:term:`CyRxnOpt ID`: ``amlro``

AMLRO (Active Machine Learning Reaction Optimizer) is our **in-house active
learning framework** designed for **reaction space optimization**. [amlro]_ It
integrates regression models with iterative candidate selection. AMLRO is
capable of handling **continuous and categorical features**, dynamic objectives
with directions (minimization or maximization), and user feedback loops.

- **Status:** Source code is currently under development. Public release is
  planned, and the project will be hosted on GitHub (expected link: *TBA*).

References
==========

.. [amlro] Manuscript in preparation.

*******
 EDBO+
*******

:term:`CyRxnOpt ID`: ``edbop``

EDBO+ [garridotorres2022]_ is a **Bayesian optimization** framework specifically
designed for chemical reaction optimization based on the original EDBO
(Experimental Design via Bayesian Optimization) algorithm [shields2021]_ from
the Doyle group. It leverages Gaussian process models with acquisition functions
(e.g., Expected Improvement, qEI, and EHVI for multi-objective settings) to
identify new experiments that are most informative. EDBO+ has been successfully
applied to **global, multi-objective optimization** of reaction yields,
selectivity, and sustainability metrics.

Compatibility
=============

If on Linux, it is likely that you will run into an error with the execstack
when running run_client with the edbop optimizer if you have glibc >=2.40.
[pytorchcpuissue]_

We were able to resolve this by running the following commands manually after
`cyrxnopt install edbop` completed:

.. code-block:: bash

    # Find the problematic libtorch_cpu.so path in your venv_edbop created from
    # running 'cyrxnopt install edbop' the first time
    find <path_to_venv_edbop> -name \*.so -print | grep "libtorch_cpu.so"

    # Reset the execstack to fix the issue
    # Solution from: https://github.com/conda-forge/pytorch-cpu-feedstock/issues/350#issuecomment-4712140412
    # Note: You may need to install or enable patchelf first
    patchelf --clear-execstack
    <path>/<to>/libtorch_cpu.so

References
==========

.. [shields2021] Shields, B. J.; Stevens, J.; Li, J.; Parasram, M.; Damani, F.;
    Alvarado, J. I. M.; Janey, J. M.; Adams, R. P.; Doyle, A. G. Bayesian
    Reaction Optimization as a Tool for Chemical Synthesis. *Nature* **2021**,
    *590* (7844), 89--96. DOI: `10.1038/s41586-021-03213-y
    <https://doi.org/10.1038/s41586-021-03213-y>`__.

.. [garridotorres2022] Garrido Torres, J. A.; Lau, S. H.; Anchuri, P.; Stevens,
    J. M.; Tabora, J. E.; Li, J.; Borovika, A.; Adams, R. P.; Doyle, A. G. A
    Multi-Objective Active Learning Platform and Web App for Reaction
    Optimization. *J. Am. Chem. Soc.* **2022**, *144* (43), 19999--20007. DOI:
    `10.1021/jacs.2c08592 <https://doi.org/10.1021/jacs.2c08592>`__.

.. [pytorchcpuissue]
    https://github.com/conda-forge/pytorch-cpu-feedstock/issues/350

*********************
 Nelder-Mead Simplex
*********************

:term:`CyRxnOpt ID`: ``nmsimplex``

CyRxnOpt uses `Scipy's Python implementation
<https://docs.scipy.org/doc/scipy/reference/optimize.minimize-neldermead.html>`__
of the Nelder-Mead Simpex method (NMSIM). [nelder1965]_ NMSIM is a
**derivative-free, local optimization algorithm** widely used for smooth,
low-dimensional problems. It iteratively refines a simplex (a polytope with n+1
vertices in n-dimensional space) through reflection, expansion, contraction, and
shrink steps to approach a local minimum. While efficient for surfaces or
regions with a single optimum, noisy surfaces or those with many local optima
may converge to a local optimum rather than the desired global solution.

References
==========

.. [nelder1965] Nelder, J. A.; Mead, R. A Simplex Method for Function
    Minimization. *The Computer Journal* **1965**, *7* (4), 308--313. DOI:
    `10.1093/comjnl/7.4.308 <https://doi.org/10.1093/comjnl/7.4.308>`__.

********
 Random
********

:term:`CyRxnOpt ID`: ``random``

A random sampling optimizer has been provided to use as a baseline comparison
for other optimization algorithms in situations like performance benchmarking.
This algorithm samples from a uniform distribution of the search space and
supports categorical variables. This optimizer is implemented using only
standard library functions and has no third-party dependencies.

***********
 SQSnobFit
***********

:term:`CyRxnOpt ID`: ``sqsnobfit``

`SQSnobFit <https://pypi.org/project/SQSnobFit/>`__ is scikit-quant's Python
implementation of Huyer and Neumaier's original SNOBFIT (Stable Noisy
Optimization by Branch and Fit) algorithm. [huyer2008]_ SNOBFIT is a **global
optimization algorithm** particularly well-suited for expensive, noisy black-box
functions. It combines local quadratic model fitting with global
space-partitioning to balance **exploration and exploitation**.

References
==========

.. [huyer2008] Huyer, W.; Neumaier, A. SNOBFIT -- Stable Noisy Optimization by
    Branch and Fit. *ACM Transactions on Mathematical Software* **2008**, *35*
    (2), 1--25. DOI: `10.1145/1377612.1377613
    <https://doi.org/10.1145/1377612.1377613>`__.
