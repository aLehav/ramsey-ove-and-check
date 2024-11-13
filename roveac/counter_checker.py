"""
counter_checker module
======================

This module provides the `CounterChecker` abstract base class, which defines a method
to determine if a graph is a Ramsey counterexample.

Classes
-------
CounterChecker : ABC
    Abstract base class for checking if a candidate graph is a Ramsey counterexample.
RamseyChecker : CounterChecker
    Counterexample checker using standard ramsey theory definition.
SubgraphSTChecker : CounterChecker
    Counterexample checker using max(s,t) - 1 subgraphs of size n.
"""

from abc import ABC
from itertools import combinations
from functools import reduce
import networkx as nx

class CounterChecker(ABC):
    """
    Abstract base class for checking if a candidate is a Ramsey counterexample.

    Methods
    -------
    check(kwargs) -> bool
        Checks if a given graph `G_prime` is a Ramsey counterexample.
    """

    @classmethod
    def check(cls, **kwargs) -> bool:
        """
        Check if the given graph `G` is a Ramsey counterexample.

        Parameters
        ----------
        kwargs : dict
            Keyword arguments containing at least:

            - G_prime : nx.Graph
                The graph to check.
                
        Returns
        -------
        bool
            True if the graph is a counterexample, False otherwise.
        """
        pass

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

class RamseyChecker(CounterChecker):
    """
    Checker for Ramsey theory counterexamples using clique and independent set tests.

    This class provides a method for checking if a given graph lacks both a clique
    of size `s` and an independent set of size `t`, which is a condition for it being
    a Ramsey counterexample.

    Runtime
    -------
    *O(n^max(s,t))*

    Methods
    -------
    check(G_prime: nx.Graph, s: int, t: int) -> bool
        Checks if the graph `G_prime` lacks both a clique of size `s` and an independent
        set of size `t`.
    """

    @classmethod
    def check(cls, **kwargs) -> bool:
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
        if has_clique_of_size_k(G_prime, s):
            return False
        if has_independent_set_of_size_k(G_prime, t):
            return False
        return True

class SubgraphSTChecker(CounterChecker):
    """
    Checker for subgraph conditions in Ramsey counterexamples using hashing and s-t optimization.

    This class verifies that for every subgraph missing an index (excluding the `passed_indices`
    in `G`), no bad subgraphs exist by using a hash map lookup to reduce computation 
    time. The checks ensure that the largest unchecked group is of size `max(s, t) + 1`.

    Runtime
    -------
    *O((max{s, t} - 1)HASH)*

    Methods
    -------
    check(G_n: nx.Graph, G_prime: nx.Graph, D: dict, hash: callable, passed_indices: set, n: int, s: int, t: int) -> bool
        Checks each relevant subgraph in `G_n` to ensure no bad subgraph is present.
    """

    @classmethod
    def check(cls, **kwargs) -> bool:
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
        hash = kwargs["hash"]
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
                keys, isomorphism = hash(G=G_n_min_i, D=D)

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
