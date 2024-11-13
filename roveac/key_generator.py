"""
Key Generators
====================

This module provides the `KeyGenerator` class, which defines a method for generating a key 
from a graph for use in dictionary generation and hashing.

Classes
-------
KeyGenerator : ABC
    Abstract base class for generating keys from graphs.
TriangleGenerator : KeyGenerator
    Generates key for number of triangles through each vertex.
Sub3Generator : KeyGenerator
    Generates key for all subgraphs of size 3 through each vertex.
"""

import networkx as nx
from collections import Counter
from itertools import combinations

class KeyGenerator:
    """
    Class for generating a unique key from a graph, intended for use
    in dictionary generation and hashing.

    Methods
    -------
    generate_key(method: str, G: nx.Graph)
        Produces a key based on the given graph.
    """
    @classmethod
    def generate_key(cls, method: str, G: nx.Graph):
        """
        Generate a unique key for the provided graph `G`.

        Parameters
        ----------
        method : str
            Denotes which method to use to construct the dictionary.
        G : nx.Graph
            The graph from which to generate the key.

        Returns
        -------
        key
            A unique identifier generated from the graph.
        """
        if method == "triangle":
            return cls._triangle_generate_key(G)
        if method == "sub_3":
            return cls._sub_3_generate_key(G)
        raise ValueError("Unknown method for generate key")

    @classmethod
    def _triangle_generate_key(cls, G: nx.Graph) -> tuple:
        """
        Generate a unique key for the graph `G` based on the count of triangles at each node.

        This method computes the triangle counts for all nodes in `G` and returns a sorted
        tuple of these counts in descending order. The resulting key can be used to identify
        or compare graphs with similar triangle structures.

        Parameters
        ----------
        G : nx.Graph
            The graph for which the key is generated, based on triangle counts.

        Returns
        -------
        tuple of int
            A sorted tuple of triangle counts in descending order, representing the triangle
            structure of `G`.
        """
        triangle_count = nx.triangles(G)
        return tuple(sorted((count for count in triangle_count.values()), reverse=True))

    @staticmethod
    def _subgraphs_and_degree_iter(G: nx.Graph, nodes=None):
        """
        Return an iterator of (node, zero_edges, one_edge, two_edges, triangles) for each node.

        This function calculates and yields the count of subgraphs of size 3 with 0, 1, 2, 
        and 3 edges (triangles) for each node in `G`.

        Parameters
        ----------
        G : nx.Graph
            The graph for which subgraphs are analyzed.
        nodes : iterable of nodes, optional
            Nodes to include in the analysis. If None, all nodes in `G` are analyzed.

        Yields
        ------
        tuple
            A tuple of the form (node, zero_edges, one_edge, two_edges, triangles), where each
            count represents the number of subgraphs with the respective edge counts.
        """
        nodes = list(G.nodes()) if nodes is None else list(G.nbunch_iter(nodes))
        neighbors = {v: set(G.neighbors(v)) for v in nodes}

        for v in nodes:
            all_other_nodes = set(G.nodes()) - {v}
            zero_edges = 0
            one_edge = 0
            two_edges = 0
            triangles = 0

            for u, w in combinations(all_other_nodes, 2):
                edges = (u in neighbors[v], w in neighbors[v], w in neighbors[u])
                num_edges = sum(edges)

                if num_edges == 0:
                    zero_edges += 1
                elif num_edges == 1:
                    one_edge += 1
                elif num_edges == 2:
                    two_edges += 1
                elif num_edges == 3:
                    triangles += 1

            yield (v, zero_edges, one_edge, two_edges, triangles)

    @classmethod
    def count_all_subgraphs(cls, G: nx.Graph, nodes=None):
        """
        Count all subgraphs of size 3 with 0, 1, 2, or 3 edges for each node in `G`.

        Parameters
        ----------
        G : nx.Graph
            The graph in which to count subgraphs.
        nodes : iterable of nodes or single node, optional
            Nodes to include in the count. If a single node is given, returns counts for that node only.

        Returns
        -------
        dict
            A dictionary where keys are nodes and values are tuples representing the count of 
            subgraphs with 1 edge, 2 edges, and 3 edges (triangles) for each node.
        """
        if nodes is not None:
            if nodes in G:
                return next(cls._subgraphs_and_degree_iter(G, nodes))
            return {v: (one, two, tri) for v, _, one, two, tri in cls._subgraphs_and_degree_iter(G, nodes)}

        subgraph_counts = Counter(dict.fromkeys(G, (0, 0, 0, 0)))
        for v, _, one, two, tri in cls._subgraphs_and_degree_iter(G):
            subgraph_counts[v] = (one, two, tri)

        return dict(subgraph_counts)

    @classmethod
    def _sub_3_generate_key(cls, G: nx.Graph):
        """
        Generate a unique key for `G` based on sorted subgraph counts of size 3.

        This method computes the counts of subgraphs of size 3 with 1, 2, or 3 edges for each node 
        in `G`, sorts these counts in descending order, and returns them as a tuple to serve as a 
        unique key for `G`.

        Parameters
        ----------
        G : nx.Graph
            The graph for which the key is generated.

        Returns
        -------
        tuple of tuples
            A sorted tuple of subgraph count tuples, where each inner tuple represents the 
            counts for a single node, ordered by the number of triangles, two-edge, and one-edge subgraphs.
        """
        subgraph_counts = cls.count_all_subgraphs(G)

        sorted_counts = sorted(
            subgraph_counts.items(), 
            key=lambda x: (x[1][2], x[1][1], x[1][0]), 
            reverse=True
        )

        tuple_sorted_counts = tuple(x[1] for x in sorted_counts)
        return tuple_sorted_counts
