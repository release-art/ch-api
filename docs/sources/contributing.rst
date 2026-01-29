.. meta::

   :google-site-verification: 3F2Jbz15v4TUv5j0vDJAA-mSyHmYIJq0okBoro3-WMY

============
Contributing
============

Contributors and contributions are welcome. Please read these guidelines first.

.. _contributing.git:

Git :fab:`github`
=================

The project homepage is on `GitHub <https://github.com/release-art/ch-api>`_.

Contributors can open pull requests from a fork targeting the parent `main branch <https://github.com/release-art/ch-api/tree/main>`_. But it may be a good first step to create an `issue <https://github.com/release-art/ch-api/issues>`_ or open
a `discussion topic <https://github.com/release-art/ch-api/discussions>`_.

.. _contributing.repo:

Repo :fas:`folder`
==================

Setting up the project should be straightforward once you have cloned the repository. A minimum of Python 3.11 is required (see ``requires-python`` in ``pyproject.toml``).

To run examples or tests you will need an API key from the `Companies House developer portal <https://developer.company-information.service.gov.uk/get-started>`_.

.. _contributing.dependencies-and-pdm:

Dependencies :fas:`cubes`
=========================

Runtime dependencies are defined in the ``[project]`` section of ``pyproject.toml``. At the time of writing these are:

* `httpx <https://www.python-httpx.org/>`_ for asynchronous HTTP communication.
* `pydantic <https://docs.pydantic.dev/>`_ for data validation and typed models.

Development and tooling dependencies are specified under ``[tool.pdm.dev-dependencies]`` in the `project TOML <https://github.com/release-art/ch-api/blob/main/pyproject.toml>`_.

.. _contributing.tests:

Tests :fas:`microscope`
=======================

Tests are located in the ``tests`` folder and can be run directly with ``pytest`` or via helper scripts in the ``bin/`` directory:

* ``bin/test.sh`` - run the full test suite with coverage reporting (automatically injects API key from 1Password).
* ``bin/autoformat.sh`` - apply Ruff formatting and autofix lint issues where possible.
* ``bin/run.sh <command>`` - run any command with API key automatically injected from 1Password.


.. _contributing.documentation:

Documentation :fas:`book`
=========================

The documentation is written in `reStructuredText <https://docutils.sourceforge.io/rst.html>`_ and built with `Sphinx <https://www.sphinx-doc.org/en/master/>`_.

HTML documentation is built locally with::

   pdm run sphinx-build -b html docs dist/docs/html

which builds the documentation and outputs HTML into ``dist/docs/html``.

The Sphinx theme in use is `pydata-sphinx-theme <https://pydata-sphinx-theme.readthedocs.io/>`_.

.. _contributing.ci:

CI :fas:`circle-play`
=====================

The CI workflows are defined `here <https://github.com/release-art/ch-api/blob/main/.github/workflows/ci.yml>`_ and there is also a separate `CodeQL workflow <https://github.com/release-art/ch-api/blob/main/.github/workflows/codeql-analysis.yml>`_.

.. _contributing.versioning-and-releases:

