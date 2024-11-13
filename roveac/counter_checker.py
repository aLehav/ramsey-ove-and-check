"""
Counter Checkers
======================

This module provides a consolidated `CounterChecker` class, which defines methods
to determine if a graph is a Ramsey counterexample using various checking approaches.

Classes
-------
CounterChecker
    Class for checking if a candidate graph is a Ramsey counterexample using different strategies.
"""

from itertools import combinations
from functools import reduce
import networkx as nx

class CounterChecker:
    """
    Class for checking if a candidate is a Ramsey counterexample.

    Methods
    -------
    check(kwargs) -> bool
        Checks if a given graph is a Ramsey counterexample.
    has_clique_of_size_k(G: nx.Graph, k: int) -> bool
        Checks if the graph `G` has a clique of size `k`.
    has_independent_set_of_size_k(G: nx.Graph, k: int) -> bool
        Checks if the graph `G` has an independent set of size `k`.
    """

    @classmethod
    def check(cls, **kwargs) -> bool:
        """
        Check if the given graph `G` is a Ramsey counterexample using the specified method.

        Parameters
        ----------
        kwargs : dict
            Keyword arguments containing required parameters based on the chosen method.

        Returns
        -------
        bool
            True if the graph is a counterexample, False otherwise.
        """
        method = kwargs.get("method")
        if method == "ramsey":
            return cls._ramsey_check(**kwargs)
        if method == "subgraph_st":
            return cls._subgraph_st_check(**kwargs)
        raise ValueError("Unknown method provided for checking.")

    @staticmethod
    def has_clique_of_size_k(G: nx.Graph, k: int) -> bool:
        """
        Check if the graph `G` has a clique of size `k`.

        Parameters
        ----------
        G : nx.Graph
            The graph to check for the presence of a clique.
        k : int
            The size of the clique to search for.

        Returns
        -------
        bool
            True if the graph has a clique of the specified size, False otherwise.
        """
        for nodes in combinations(G.nodes, k):
            if G.subgraph(nodes).number_of_edges() == k * (k - 1) // 2:
                return True
        return False

    @staticmethod
    def has_independent_set_of_size_k(G: nx.Graph, k: int) -> bool:
        """
        Check if the graph `G` has an independent set of size `k`.

        Parameters
        ----------
        G : nx.Graph
            The graph to check for an independent set.
        k : int
            The size of the independent set to search for.

        Returns
        -------
        bool
            True if the graph has an independent set of the specified size, False otherwise.
        """
        for nodes in combinations(G.nodes, k):
            if G.subgraph(nodes).number_of_edges() == 0:
                return True
        return False

    @classmethod
    def _ramsey_check(cls, **kwargs) -> bool:
        """
        Check if the given graph `G_prime` lacks both a clique of size `s` and 
        an independent set of size `t`.

        Parameters
        ----------
        kwargs : dict
            Keyword arguments containing:

            - G_prime : nx.Graph
                The graph to check.
            - s : int
                The size of the clique to check for.
            - t : int
                The size of the independent set to check for.

        Returns
        -------
        bool
            True if `G_prime` lacks both a clique of size `s` and an independent set of size `t`,
            indicating it is a Ramsey counterexample, False otherwise.
        """
        G_prime = kwargs["G_prime"]
        s = kwargs["s"]
        t = kwargs["t"]
        if cls.has_clique_of_size_k(G_prime, s):
            return False
        if cls.has_independent_set_of_size_k(G_prime, t):
            return False
        return True

    @classmethod
    def _subgraph_st_check(cls, **kwargs) -> bool:
        """
        Check that each subgraph of `G_n` that excludes indices not in `passed_indices` 
        passes hash-based tests.

        Parameters
        ----------
        kwargs : dict
            Keyword arguments containing:

            - G_n : nx.Graph
                The primary graph to check subgraphs within.
            - G_prime : nx.Graph
                A reference graph for neighbor checks.
            - D : dict
                Dictionary for hashed subgraph lookups.
            - hash : callable
                Hashing function for subgraphs.
            - passed_indices : set
                Set of node indices that have already been checked.
            - n : int
                The total number of nodes in `G_n`.
            - s : int
                Size parameter for clique checks.
            - t : int
                Size parameter for independent set checks.

        Returns
        -------
        bool
            True if all necessary subgraphs pass the hash-based checks, False otherwise.
        """
        G_n = kwargs["G_n"]
        G_prime = kwargs["G_prime"]
        D = kwargs["D"]
        hash_func = kwargs["hash"]
        passed_indices = kwargs["passed_indices"]
        n = kwargs["n"]
        s = kwargs["s"]
        t = kwargs["t"]
        checks_needed = min(n, max(s, t) + 1)
        checks_performed = len(passed_indices)

        for i in range(n):
            if i not in passed_indices:
                G_n_min_i = G_n.copy()
                G_n_min_i.remove_node(i)
                keys, isomorphism = hash_func(G=G_n_min_i, D=D)

                v_n_neighbors = set(G_prime.neighbors(n))
                v_n_neighbors.discard(i)
                iso_neighbors = tuple(sorted([isomorphism[neighbor] for 
                                              neighbor in v_n_neighbors], reverse=True))

                if iso_neighbors not in reduce(lambda d, key: d[key], keys, D):
                    return False

                checks_performed += 1
                if checks_performed == checks_needed:
                    return True

        return True
