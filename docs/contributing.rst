Contributing
======================

Setup Development Environment
-----------------------------

Install poetry

.. code:: console

   $ curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python
   $ source $HOME/.poetry/env

set python versions

.. code:: console

   $ pyenv local 3.8.2 3.7.6

Install nox

.. code:: console

   $ pipx install nox

Install pre-commit hooks

.. code:: console

   $ pipx install pre-commit
   $ pre-commit install

Useful Stuff
------------

-  Install dependencies

.. code:: console

   $ poetry install

-  Run the tests

.. code:: console

   $ nox -rs tests

-  Run the linter

.. code:: console

   $ nox -rs lint

-  Build the docs

.. code:: console

   $ nox -rs docs

-  Add standard dependency

.. code:: console

   $ poetry add <package-name>

-  Add development dependency:

.. code:: console

   $ poetry add --dev <package-name>
