"""
Isomorphism Hashers
=========================

This module provides the `IsomorphismHasher` abstract base class, which defines a method
for hashing a graph to check for isomorphisms among known keys in a dictionary.

Classes
-------
IsomorphismHasher : ABC
    Abstract base class for hashing graphs and checking for isomorphisms.
"""

from abc import ABC
import networkx as nx

class IsomorphismHasher(ABC):
    """
    Abstract base class for hashing graphs and retrieving matching isomorphic keys.

    Methods
    -------
    hash(G: nx.Graph, D: dict) -> tuple[list, dict]
        Hashes the given graph and returns a list of matching isomorphic keys from the dictionary.
    """

    @classmethod
    def hash(cls, G: nx.Graph, D: dict) -> tuple[list, dict]:
        """
        Takes in a graph known to be among the keys of `D` and hashes it, returning
        a matching list of isomorphic keys and the corresponding isomorphism data.

        The last key in the returned list should represent a graph for the time being.

        Parameters
        ----------
        G : nx.Graph
            The graph to be hashed and checked for isomorphisms.
        D : dict
            A dictionary where keys are graph representations to check for isomorphism with `G`.

        Returns
        -------
        tuple[list, dict]
            A tuple containing:
            - A list of keys in `D` that are isomorphic to `G`.
            - A dictionary representing the isomorphism data for the matches.
        """
        pass
