"""
counter_checker module
======================

This module provides the `CounterChecker` abstract base class, which defines a method
to determine if a graph is a Ramsey counterexample.

Classes
-------
CounterChecker : ABC
    Abstract base class for checking if a candidate graph is a Ramsey counterexample.
"""

from abc import ABC
import networkx as nx

class CounterChecker(ABC):
    """
    Abstract base class for checking if a candidate is a Ramsey counterexample.

    Methods
    -------
    check(G: nx.Graph, kwargs) -> bool
        Checks if the given graph `G` is a Ramsey counterexample.
    """

    @classmethod
    def check(cls, G: nx.Graph, **kwargs) -> bool:
        """
        Check if the given graph `G` is a Ramsey counterexample.

        Parameters
        ----------
        G : nx.Graph
            The graph to check.
        kwargs : dict
            Additional parameters for specific checking conditions.

        Returns
        -------
        bool
            True if the graph is a counterexample, False otherwise.
        """
        pass
