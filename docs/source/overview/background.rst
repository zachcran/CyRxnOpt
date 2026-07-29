.. _background:

############
 Background
############

Optimization algorithms experience widespread application in economics,
molecular modeling, and industrial processes. In chemistry, optimization of
reactions for objectives like desired product yield, selectivity, cost
efficiency, and conversion is a necessity as well. This is typically performed
using a chemist's intuition combined with one variable at a time (OVAT) or
Design of Experiments (DoE) techniques. Mathematical optimization algorithms
designed in other fields have found success when applied to chemical reaction
optimization, but the various interfaces, programming skills, and technical
debugging, and installation methods required to use an optimization algorithm is
usually not considered worth the effort by most chemists. When targeting
reaction optimization, the algorithms are expected to be used in the laboratory,
likely by someone without much programming experience. Compounded on these
issues, there is no one-size-fits-all algorithm so chemists need to switch
algorithms based on which will perform the best on their reaction of interest,
with each new algorithm bringing its unique twist on the challenges enumerated
above. With these challenges in mind, aside from a few exemplary laboratories,
reaction optimization algorithms have still not achieved widespread use in the
field of basic chemistry.

To lower the barrier of entry between chemists and reaction optimization
algorithms, user-friendly interfaces need to be designed between the chemist and
the algorithm on multiple levels. EDBO+ provides a great example of this by
providing a web interface as well as a relatively straightforward API. Our team
has also designed Rxn Rover, a reaction automation platform that strives to
create a user-friendly program to allow chemists to connect optimization
algorithms directly to their reactors in a flexible way.

However, both approaches currently have issues. The EDBO+ web interface only
works for the EDBO+ algorithm, which may not be the best choice for all
reactions. Rxn Rover provides plugins for different optimization algorithms that
are easily loaded in the program, but each of these plugins is difficult and
time consuming to produce. On a level between these user interfaces and the
optimization algorithms, there is a need for an abstracted interface that allows
access to multiple optimization algorithms through common commands and
formatting. It must also be relatively straightforward to add new optimization
algorithm support to this interface.

Due to the myriad possible applications, implementations, data formats, and
programming languages, it is likely impossible to define one abstract interface
that will unilaterraly apply to all optimization algorithms in all fields.
However, narrowing the scope to chemical reaction optimization, algorithms are
commonly implemented in Python with one application in mind, optimize a reaction
for *x*, *y*, *z* results. This significantly reduces the number of challenges
in creating an abstract optimization algorithm interface.

CyRxnOpt aims to provide a single software interface that can provide access to
many different optimization algorithms, mainly designed for use in chemical
reaction optimization. It breaks chemical reaction optimization in to four main
steps: Installation, Configuration, Training, Prediction. This allows users to
program to a single software interface, simplifying the development of
user-friendly tools and interfaces to lower the barrier of entry into reaction
optimization.
