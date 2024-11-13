"""
Searches
=============

This module provides the `Search` abstract base class, which defines a method
for searching within a given Ramsey graph based on specific parameters.

Classes
-------
Search : ABC
    Abstract base class for performing searches on Ramsey graphs.
"""

from abc import ABC

class Search(ABC):
    """
    Abstract base class for performing searches within a Ramsey graph.

    Methods
    -------
    search(R_s_t_n: set, s: int, t: int) -> list
        Searches within R(s, t, n) based on given parameters and returns a list of results.
    """

    @classmethod
    def search(cls, R_s_t_n: set, s: int, t: int) -> list:
        """
        Perform a search within the graph R(s, t, n) based on the provided parameters.

        Parameters
        ----------
        R_s_t_n : set
            The set representing the current Ramsey graph R(s, t, n).
        s : int
            An integer parameter for the search criterion.
        t : int
            An integer parameter for the search criterion.

        Returns
        -------
        list
            A list of results from the search within the Ramsey graph.
        """
        pass
