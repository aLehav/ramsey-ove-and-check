"""
Decrementors
==================

This module provides the `Decrementor` abstract base class, which defines a method
to generate a new Ramsey graph by decrementing a parameter and checking for subgraph isomorphisms.

Classes
-------
Decrementor : ABC
    Abstract base class for generating a decremented Ramsey graph.
TriangleDecrementor : Decrementor
    Decrements with triangle keys.
FlatDecrementor : Decrementor
    Decrements without keys and hashing.
"""

from abc import ABC
from tqdm import tqdm
import networkx as nx
from roveac.key_generator import TriangleGenerator

class Decrementor(ABC):
    """
    Abstract base class for generating a decremented Ramsey graph by analyzing subgraphs
    and performing isomorphism checking.

    Methods
    -------
    decrement(R_s_t_n: set, early_stopping=None) -> set
        Generates R(s, t, n-1) by analyzing subgraphs and checking for isomorphisms.
    """
    @classmethod
    def decrement(cls, R_s_t_n: set, early_stopping=None) -> set:
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

class TriangleDecrementor(Decrementor):
    """
    Performs decrementing operations on sets of graphs for Ramsey theory computations,
    specifically aimed at reducing graphs by removing nodes to check for specific properties.

    This class extends `Decrementor` to implement a specialized decrementing method that 
    operates on sets of graphs, utilizing a unique key-based storage mechanism for subgraphs.

    Methods
    -------
    decrement(R_s_t_n: set, early_stopping=None) -> dict
        Decrements each graph in `R_s_t_n` by removing individual nodes, generating subgraphs,
        and indexing them based on unique keys.
    """

    @classmethod
    def decrement(cls, R_s_t_n: set, early_stopping=None) -> dict:
        """
        Decrement each graph in `R_s_t_n` by removing nodes and indexing resulting subgraphs.

        For each graph in `R_s_t_n`, iteratively removes nodes to create subgraphs, which 
        are stored in a dictionary `D` keyed by a unique identifier. If a subgraph is already 
        present in `D`, isomorphism checks are performed to ensure unique storage of isomorphic 
        subgraphs. The function halts early if the `early_stopping` limit is reached.

        Parameters
        ----------
        R_s_t_n : set of nx.Graph
            Set of graphs on which decrementing operations are performed.
        early_stopping : int, optional
            Limits the total number of decrementing iterations, halting early if reached.

        Returns
        -------
        set of nx.Graph
            Set of all unique subgraphs created through the decrementing process, with node
            labels converted to integers.
        """
        D = {}

        # Get n
        for G_n in R_s_t_n:
            n = G_n.order()
            break

        total_graphs = len(R_s_t_n)
        total_combinations = n * total_graphs

        with tqdm(total=total_combinations, desc="Decrementing combinations") as pbar:
            pbar.set_postfix(graph=f"0/{total_graphs}")
            iterations = 0
            for idx, G_n in enumerate(R_s_t_n, start=1):
                for i in range(n):
                    G_n_minus_one = G_n.copy()
                    G_n_minus_one.remove_node(i)
                    key = TriangleGenerator.generate_key(G_n_minus_one)
                    if key in D:
                        found_iso = False
                        for G_star in D[key]:
                            if nx.isomorphism.vf2pp_is_isomorphic(G_n_minus_one, G_star):
                                found_iso = True
                                break
                        if not found_iso: 
                            D[key].add(G_n_minus_one)
                    else:
                        D[key] = set((G_n_minus_one,))
                    pbar.update(1)
                    iterations += 1
                    if (early_stopping is not None) and (iterations >= early_stopping):
                        break

                if (early_stopping is not None) and (iterations >= early_stopping):
                    break
                pbar.set_postfix(graph=f"{idx}/{total_graphs}")

        S = set()

        total_graphs = sum((len(D[key]) for key in D))
        with tqdm(total=total_graphs, desc="Reindexing subgraphs") as pbar:
            for key, graphs in D.items():
                for graph in graphs:
                    graph = nx.convert_node_labels_to_integers(graph)
                    S.add(graph)
                    pbar.update(1)
                
        return S

class FlatDecrementor(Decrementor):
    """
    Generates decremented versions of graphs in a flat structure without indexing, 
    resulting in a set of unique subgraphs of `R(s, t, n-1)`.

    This class extends `Decrementor` to provide a flat decrementing method that 
    performs isomorphism checks for each subgraph and stores only unique results.

    Methods
    -------
    decrement(R_s_t_n: set, early_stopping=None) -> dict
        Decrements each graph in `R_s_t_n` by removing individual nodes to create unique
        subgraphs, returning them as a set.
    """

    @classmethod
    def decrement(cls, R_s_t_n: set, early_stopping=None) -> dict:
        """
        Decrement each graph in `R_s_t_n` by removing nodes and storing unique subgraphs.

        For each graph in `R_s_t_n`, iteratively removes nodes to generate subgraphs, 
        adding each non-isomorphic subgraph to the set `D`. The function halts early if 
        the `early_stopping` limit is reached.

        Parameters
        ----------
        R_s_t_n : set of nx.Graph
            Set of graphs to decrement by node removal operations.
        early_stopping : int, optional
            Limits the total number of decrementing iterations, halting early if reached.

        Returns
        -------
        set of nx.Graph
            Set of all unique subgraphs created through the decrementing process, with 
            node labels converted to integers.
        """
        D = set()

        # Get n
        for G_n in R_s_t_n:
            n = G_n.order()
            break

        total_graphs = len(R_s_t_n)
        total_combinations = n * total_graphs

        with tqdm(total=total_combinations, desc="Decrementing combinations") as pbar:
            pbar.set_postfix(graph=f"0/{total_graphs}")
            iterations = 0
            for idx, G_n in enumerate(R_s_t_n, start=1):
                for i in range(n):
                    G_n_minus_one = G_n.copy()
                    G_n_minus_one.remove_node(i)
                    if len(D) > 0:
                        found_iso = False
                        for G_star in D:
                            if nx.isomorphism.vf2pp_is_isomorphic(G_n_minus_one, G_star):
                                found_iso = True
                                break
                        if not found_iso: 
                            D.add(G_n_minus_one)
                    else:
                        D.add(G_n_minus_one)
                    pbar.update(1)
                    iterations += 1
                    if (early_stopping is not None) and (iterations >= early_stopping):
                        break

                if (early_stopping is not None) and (iterations >= early_stopping):
                    break
                pbar.set_postfix(graph=f"{idx}/{total_graphs}")

        S = set()

        total_graphs = len(D)
        with tqdm(total=total_graphs, desc="Reindexing subgraphs") as pbar:
            for graph in D:
                graph = nx.convert_node_labels_to_integers(graph)
                S.add(graph)
                pbar.update(1)
                
        return S