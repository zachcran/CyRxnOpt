.. _writing_documentation:

#######################
 Writing Documentation
#######################

.. note::

    Make sure you know how to `view the documentation <viewing_documentation>`_
    before trying to write any!

We welcome contributions to the CyRxnOpt documentation, whether it be a small
typo fix or an entirely new tutorial or section. This page covers the things you
may need to know to make a contribution to the documentation.

Our documentation is written in `reStructuredText
<https://docutils.sourceforge.io/rst.html>`_ (reST; file extension: ``rst``) and
generated using `Sphinx <https://www.sphinx-doc.org/en/master/>`_. If you are
not familiar with reST, Sphinx has a good primer `here
<https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html>`__.

**********************
 Style and Formatting
**********************

Our documentation style and formatting is mainly delegated to our formatting
tool, `docstrfmt <https://github.com/LilSpazJoekp/docstrfmt>`_. reST files will
be formatted automatically when you run ``git commit`` by pre-commit, but if you
want to format the before files committing them, reST files in the project can
be formatted at any time with:

.. code-block:: bash

    tox -e docformat

Although the formatting will be fixed automatically, it is useful to keep your
files somewhat close to their final formatting to have an idea what it will look
like. The main formatting rules to keep in mind are:

- Keep your lines of text under 80 characters
- Use the following section header characters with no overlines (`why not Python
  headers? <https://github.com/LilSpazJoekp/docstrfmt/issues/91>`_):

  - ``=`` for parts
  - ``-`` for chapters
  - ``~`` for sections
  - ``+`` for subsections
  - ``.`` for subsubsections
  - ``,`` for paragraphs

- Use ``-``, not ``*`` for bulleted lists

*************************
 Documentation Locations
*************************

The majority of our documentation is organized under ``docs/source``, although
there are a variety of other reST files throughout the project to greet users
(``README.rst``), explain usage (``docs/README.rst``), or provide important
information without needing to sift through documentation website
(``AUTHORS.rst``).

***************************
 Testing the Documentation
***************************

The first step in testing the documentation should be to `build and preview it
<viewing_documentation>`_ on your local system to make sure it builds correctly
any links work. If you are seeing a lot of warnings or errors during the build,
you can get a nice summary of warnings and errors by running:

.. code-block:: bash

    tox -e doctests

This can help check for any issues that might be overlooked in manual testing of
the documentation website. You can also check specifically for broken links to
internal pages or external websites with:

.. code-block:: bash

    tox -e linkcheck
