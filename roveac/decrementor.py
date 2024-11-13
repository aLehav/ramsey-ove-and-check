"""
decrementor module
==================

This module provides the `Decrementor` abstract base class, which defines a method
to generate a new Ramsey graph by decrementing a parameter and checking for subgraph isomorphisms.

Classes
-------
Decrementor : ABC
    Abstract base class for generating a decremented Ramsey graph.
"""

from abc import ABC

class Decrementor(ABC):
    """
    Abstract base class for generating a decremented Ramsey graph by analyzing subgraphs
    and performing isomorphism checking.

    Methods
    -------
    decrement(R_s_t_n: set, early_stopping=None) -> set
        Generates R(s, t, n-1) by analyzing subgraphs and checking for isomorphisms.
    """

    def decrement(self, R_s_t_n: set, early_stopping=None) -> set:
        """
        Generate R(s, t, n-1) by intelligently analyzing subgraphs and performing
        isomorphism checks.

        Parameters
        ----------
        R_s_t_n : set
            The current set representing R(s, t, n).
        early_stopping : optional
            A parameter to allow early termination of the process, if applicable.

        Returns
        -------
        set
            A set representing the decremented graph R(s, t, n-1).
        """
        pass
