Usage
=====

.. _installation:

Installation
------------

To use ROVEaC, first install it using pip:

.. code-block:: console

   (.venv) $ pip install roveac

Usage Examples
--------------

### Checking for Ramsey Counterexamples

To check if a graph is a Ramsey counterexample, use the `CounterChecker` module:

.. code-block:: python

   from roveac.counter_checkers import CounterChecker
   import networkx as nx

   G = nx.complete_graph(5)  # Example graph
   result = CounterChecker.check(G)
   print("Is counterexample:", result)

More details on each module are available in the :doc:`api` section.