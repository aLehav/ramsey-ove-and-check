"""
Isomorphism Hashers
=========================

This module provides the `IsomorphismHasher` class, which defines a method
for hashing a graph to check for isomorphisms among known keys in a dictionary.

Classes
-------
IsomorphismHasher
    Class for hashing graphs and checking for isomorphisms.
"""

import networkx as nx
from roveac.key_generator import KeyGenerator

class IsomorphismHasher:
    """
    Class for hashing graphs and retrieving matching isomorphic keys.

    Methods
    -------
    hash(G: nx.Graph, D: dict, method: str) -> tuple[list, dict]
        Hashes the given graph and returns a list of matching isomorphic keys from the dictionary.
    """

    @classmethod
    def hash(cls, G: nx.Graph, D: dict, method: str = "triangle") -> tuple[list, dict]:
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
        method : str
            Denotes which method to use to hash.

        Returns
        -------
        tuple[list, dict]
            A tuple containing:
            
            - A list of keys in `D` that are isomorphic to `G`.
            - A dictionary representing the isomorphism data for the matches.
        """
        if method == "triangle":
            return cls._triangle_hash(G, D)
        if method == "sub_3":
            return cls._sub_3_hash(G, D)
        if method == "flat":
            return cls._flat_hash(G, D)
        raise ValueError("Unknown method provided for hashing.")
    
    @classmethod
    def _triangle_hash(cls, G: nx.Graph, D: dict) -> tuple[list, dict]:
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
        key = KeyGenerator.generate_key(G, method="triangle")
        for G_star in D[key].keys():
            isomorphim = nx.isomorphism.vf2pp_isomorphism(G, G_star)
            if isomorphim is not None:
                return [key, G_star], isomorphim

        raise RuntimeError("No isomorphism found.")
    
    @classmethod
    def _sub_3_hash(cls, G: nx.Graph, D: dict) -> tuple[list, dict]:
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
        key = KeyGenerator.generate_key(G, method="sub_3")
        for G_star in D[key].keys():
            isomorphim = nx.isomorphism.vf2pp_isomorphism(G, G_star)
            if isomorphim is not None:
                return [key, G_star], isomorphim

        raise RuntimeError("No isomorphism found.")
    
    @classmethod
    def _flat_hash(cls, G: nx.Graph, D: dict) -> tuple[list, dict]:
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
