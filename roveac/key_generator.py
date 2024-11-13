"""
key_generator module
====================

This module provides the `KeyGenerator` abstract base class, which defines a method
for generating a key from a graph for use in dictionary generation and hashing.

Classes
-------
KeyGenerator : ABC
    Abstract base class for generating keys from graphs.
"""

from abc import ABC

class KeyGenerator(ABC):
    """
    Abstract base class for generating a unique key from a graph, intended for use
    in dictionary generation and hashing.

    Methods
    -------
    generate_key(G)
        Produces a key based on the given graph.
    """

    def generate_key(self, G):
        """
        Generate a unique key for the provided graph `G`.

        Parameters
        ----------
        G : Graph
            The graph from which to generate the key.

        Returns
        -------
        key
            A unique identifier generated from the graph.
        """
        pass
