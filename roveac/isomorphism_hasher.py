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
from roveac.key_generator import TriangleGenerator, Sub3Generator

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

class TriangleHasher(IsomorphismHasher):
    """
    Hashes a graph based on triangle counts at each node to facilitate isomorphism checks.

    This class extends `IsomorphismHasher` to use triangle-based hashing for efficient 
    isomorphism checks within a dictionary of pre-hashed graphs. Primarily used when 
    triangle counts are sufficient to distinguish graphs in `D`.

    Methods
    -------
    hash(G: nx.Graph, D: dict) -> tuple[list, dict]
        Hashes the graph based on triangle counts and finds an isomorphic graph in `D`.
    """
    @classmethod
    def hash(cls, G: nx.Graph, D: dict) -> tuple[list, dict]:
        """
        Hash the graph `G` by its triangle count and locate an isomorphic graph in `D`.

        Parameters
        ----------
        G : nx.Graph
            The graph to hash and check for isomorphism.
        D : dict
            Dictionary where keys are triangle-based hashes, each storing graphs with similar structure.

        Returns
        -------
        tuple[list, dict]
            A list containing the hash key and matched graph, and the isomorphism mapping.

        Raises
        ------
        RuntimeError
            If no isomorphic graph is found in `D`.
        """
        key = TriangleGenerator.generate_key(G)
        for G_star in D[key].keys():
            isomorphim = nx.isomorphism.vf2pp_isomorphism(G, G_star)
            if isomorphim is not None:
                return [key, G_star], isomorphim

        raise RuntimeError("No isomorphism found.")
    
class Sub3Hasher(IsomorphismHasher):
    """
    Hashes a graph by subgraph counts of size 3 for efficient isomorphism checks.

    Extends `IsomorphismHasher` to use subgraph size 3 counts for hashing, suitable 
    for cases where subgraph patterns help distinguish graph structures in `D`.

    Methods
    -------
    hash(G: nx.Graph, D: dict) -> tuple[list, dict]
        Hashes the graph based on subgraph size 3 counts and finds an isomorphic graph in `D`.
    """
    @classmethod
    def hash(cls, G: nx.Graph, D: dict) -> tuple[list, dict]:
        """
        Hash the graph `G` by its subgraph size 3 counts and locate an isomorphic graph in `D`.

        Parameters
        ----------
        G : nx.Graph
            The graph to hash and check for isomorphism.
        D : dict
            Dictionary where keys are subgraph size 3-based hashes, each storing graphs with similar structure.

        Returns
        -------
        tuple[list, dict]
            A list containing the hash key and matched graph, and the isomorphism mapping.

        Raises
        ------
        RuntimeError
            If no isomorphic graph is found in `D`.
        """
        key = Sub3Generator.generate_key(G)
        for G_star in D[key].keys():
            isomorphim = nx.isomorphism.vf2pp_isomorphism(G, G_star)
            if isomorphim is not None:
                return [key, G_star], isomorphim

        raise RuntimeError("No isomorphism found.")
    
class VF2PPIterHasher(IsomorphismHasher):
    """
    Performs naive hashing by iterating over `D` and applying VF2++ isomorphism checks.

    This class extends `IsomorphismHasher` to identify an isomorphic graph from a set of 
    candidates by directly iterating over all entries in `D`. Designed for cases where 
    an exact match is known to exist but requires explicit verification.

    Methods
    -------
    hash(G: nx.Graph, D: dict) -> tuple[list, dict]
        Iterates through `D` to find the graph isomorphic to `G`.
    """
    @classmethod
    def hash(cls, G: nx.Graph, D: dict) -> tuple[list, dict]:
        """
        Locate the graph in `D` that is isomorphic to `G`.

        Parameters
        ----------
        G : nx.Graph
            The graph to match with an entry in `D`.
        D : dict
            Dictionary containing graphs to check for isomorphism with `G`.

        Returns
        -------
        tuple[list, dict]
            A list containing the matched graph and the isomorphism mapping.

        Raises
        ------
        RuntimeError
            If no isomorphic graph is found in `D`.
        """
        for G_star in D.keys():
            isomorphim = nx.isomorphism.vf2pp_isomorphism(G, G_star)
            if isomorphim is not None:
                return [G_star], isomorphim

        raise RuntimeError("No isomorphism found.")
