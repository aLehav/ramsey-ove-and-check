"""
dict_constructor module
=======================

This module provides the `DictConstructor` abstract base class, which defines a method
for generating a dictionary with keys in a decremented Ramsey graph.

Classes
-------
DictConstructor : ABC
    Abstract base class for constructing a dictionary from a given Ramsey graph.
"""

from abc import ABC

class DictConstructor(ABC):
    """
    Abstract base class for constructing a dictionary with keys in a decremented Ramsey graph.

    Methods
    -------
    construct_dict(r_s_t_n: set, early_stopping: tuple[None, int]) -> dict
        Generates a dictionary with keys in R(s, t, n-1) based on the input graph.
    """

    @classmethod
    def construct_dict(cls, r_s_t_n: set, early_stopping: tuple[None, int]) -> dict:
        """
        Given R(s, t, n), generate a dictionary with keys in R(s, t, n-1).

        Parameters
        ----------
        r_s_t_n : set
            The current set representing R(s, t, n).
        early_stopping : tuple[None, int]
            A parameter for optional early stopping, with an integer or None.

        Returns
        -------
        dict
            A dictionary with keys in the decremented Ramsey graph R(s, t, n-1).

        TODO
        ----
        Add corresponding graph counters to decrement.
        """
        pass
