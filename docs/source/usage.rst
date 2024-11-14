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

To perform one-vertex extension from a counterexample set, use the `Extender` module:

.. code-block:: python

   from roveac import Extender
   import networkx as nx

   R_4_6_35 = set(nx.read_graph6('r46_35some.g6'))
   R_4_6_36 = Extender.extend(r_s_t_n=R_4_6_35, 
                                    s=4,
                                    t=6,
                                    extension_method="base",
                                    dict_constructor_method="triangle",
                                    hash_method="triangle",
                                    check_method="subgraph_st",
                                    generate_key_method="triangle")
   print(f"{len(R_4_6_36)} counterexamples exist in the set R(4,6,36)")

To perform counterexample checking, use the `CounterChecker` module:

.. code-block:: python

   from roveac import CounterChecker

   counter_13 = nx.read_graph6("r35_13.g6")
   is_counter = CounterChecker.check(G_prime=counter_13, s=3, t=5, method="ramsey")
   assert is_counter

More details on each module are available in the :doc:`api` section.