"""
Mapping Constructors
=======================

This module provides the `MappingConstructor` class, which defines method for generating a mapping
with keys in a decremented Ramsey graph.

Classes
-------
MappingConstructor
    Class for constructing a mapping from a given counterexample set.
"""

import math
from itertools import combinations
from tqdm import tqdm
import networkx as nx
from roveac.key_generator import KeyGenerator

def _add_isomorphic_neighbors(mapping, G, G_minus_one, i):
    """
    Add isomorphic neighbor mappings to the mapping for a given subgraph.

    This helper function performs isomorphism checks between a subgraph `G_minus_one` 
    and itself to ensure consistency in stored mappings. It then stores the 
    neighbors of `G` that are isomorphic to the nodes in `G_minus_one`, enabling 
    future subgraph retrieval based on neighbor mappings.

    Parameters
    ----------
    mapping : dict
        mapping from subgraphs to their associated isomorphic neighbor mappings.
    G : nx.Graph
        The original graph containing `G_minus_one` as a subgraph.
    G_minus_one : nx.Graph
        The subgraph of `G` formed by removing one node.
    i : int
        The node index removed from `G` to form `G_minus_one`.
    """
    isomorphisms = list(nx.isomorphism.vf2pp_all_isomorphisms(G_minus_one, G_minus_one))
    neighbors = set(G.neighbors(i))
    for isomorphism in isomorphisms:
        isomorphic_neighbors = tuple(sorted((isomorphism[neighbor] for neighbor in neighbors), reverse=True))
        if G_minus_one in mapping:
            mapping[G_minus_one].add(isomorphic_neighbors)
        else:
            mapping[G_minus_one] = set([isomorphic_neighbors])

class MappingConstructor:
    """
    Class for constructing a mapping with keys in a decremented Ramsey graph.

    Methods
    -------
    construct_dict(r_s_t_n: set, method: str, early_stopping: tuple[None, int]) -> dict
        Generates a mapping with keys in R(s, t, n-1) based on the input graph.
    """

    @classmethod
    def construct_mapping(cls, r_s_t_n: set, method: str = "triangle", early_stopping: tuple[None, int] = None) -> dict:
        """
        Given R(s, t, n), generate a mapping with keys in R(s, t, n-1).

        Parameters
        ----------
        r_s_t_n : set
            The current set representing R(s, t, n).
        method : str
            Denotes which method to use to construct the mapping.
        early_stopping : tuple[None, int]
            A parameter for optional early stopping, with an integer or None.

        Returns
        -------
        dict
            A mapping with keys in the decremented Ramsey graph R(s, t, n-1).
        """
        if method in ["triangle","sub_3"]:
            return cls._single_key_construct_mapping(method, r_s_t_n, early_stopping)
        if method == "flat":
            return cls._flat_construct_mapping(r_s_t_n, early_stopping)
        if method == "double_key":
            return cls._double_key_construct_mapping(r_s_t_n, early_stopping)
        raise ValueError("Unknown method provided for constructing")

    @classmethod
    def _single_key_construct_mapping(cls, method: str, r_s_t_n: set, early_stopping=None) -> dict:
        """
        Generate a mapping of subgraphs hashed by a single key for isomorphism-based grouping.

        This method iterates over each graph in `r_s_t_n`, removing one node at a time to 
        produce subgraphs of size `n-1`. Each subgraph is hashed using the `TriangleGenerator` or
        `Sub3Generator` key and is checked for isomorphism with existing entries in the mapping. 
        Neighbor mappings are stored for each unique subgraph to support additional operations.

        Parameters
        ----------
        method : str
            Denotes which method to use to hash.
        r_s_t_n : set of nx.Graph
            Set of graphs to process into subgraphs of size `n-1`, grouped by isomorphism.
        early_stopping : int, optional
            Limits the total number of iterations, halting early if the limit is reached.

        Returns
        -------
        dict
            A mapping where keys are triangle-based subgraph hashes, and values are dictionaries 
            mapping subgraphs to sets of tuples, representing isomorphic neighbor mappings for 
            each unique subgraph.
        """
        mapping = {}

        # Get n
        for G_n in r_s_t_n:
            n = G_n.order()
            break

        total_graphs = len(r_s_t_n)
        total_combinations = n * total_graphs

        with tqdm(total=total_combinations, desc="Constructing dict") as pbar:
            pbar.set_postfix(graph=f"0/{total_graphs}")
            iterations = 0
            for idx, G_n in enumerate(r_s_t_n, start=1):
                for i in range(n):
                    G_n_minus_one = G_n.copy()
                    G_n_minus_one.remove_node(i)
                    key = KeyGenerator.generate_key(G_n_minus_one, method=method)
                    G_index = G_n_minus_one
                    if key in mapping:
                        found_isomorphism = False
                        for G_star in mapping[key].keys():
                            isomorphisms = list(nx.isomorphism.vf2pp_all_isomorphisms(G_n_minus_one, G_star))
                            if isomorphisms:
                                found_isomorphism = True
                                G_index = G_star
                                break
                        if not found_isomorphism:
                            isomorphisms = list(nx.isomorphism.vf2pp_all_isomorphisms(G_n_minus_one, G_index))    
                    else:
                        isomorphisms = list(nx.isomorphism.vf2pp_all_isomorphisms(G_n_minus_one, G_index))
                        neighbors = set(G_n.neighbors(i))
                        mapping[key] = {}
                        for isomorphism in isomorphisms:           
                            isomorphic_neighbors = tuple(sorted((isomorphism[neighbor] for neighbor in neighbors), reverse=True))
                            if G_n_minus_one in mapping[key]:
                                mapping[key][G_n_minus_one].add(isomorphic_neighbors)
                            else:
                                mapping[key][G_n_minus_one] = set([isomorphic_neighbors])
                    if G_index not in mapping[key]:
                        mapping[key][G_index] = {}
                    neighbors = set(G_n.neighbors(i))
                    for isomorphism in isomorphisms:
                        isomorphic_neighbors = tuple(sorted((isomorphism[neighbor] for neighbor in neighbors), reverse=True))
                        mapping[key][G_index].add(isomorphic_neighbors)
                    pbar.update(1)
                    iterations += 1
                    if (early_stopping is not None) and (iterations >= early_stopping):
                        break

                if (early_stopping is not None) and (iterations >= early_stopping):
                    break
                pbar.set_postfix(graph=f"{idx}/{total_graphs}")
        return mapping

    @classmethod
    def _flat_construct_mapping(cls, r_s_t_n: set, early_stopping=None) -> dict:
        """
        Generate a mapping of unique subgraphs based on isomorphism checks.

        For each graph in `r_s_t_n`, this method removes one node at a time to produce 
        subgraphs of size `n-1`. It then checks if each subgraph is isomorphic to any 
        existing subgraph in the mapping. If a new unique subgraph is found, it is added 
        along with its isomorphic neighbor mappings.

        Parameters
        ----------
        r_s_t_n : set of nx.Graph
            Set of graphs to process into unique subgraphs of size `n-1`.
        early_stopping : int, optional
            Limits the total number of iterations, halting early if the limit is reached.

        Returns
        -------
        dict
            A mapping where keys are unique subgraphs, and values are sets of tuples
            representing isomorphic neighbor mappings for each subgraph.
        """
        mapping = {}

        # Get n
        for G_n in r_s_t_n:
            n = G_n.order()
            break

        total_graphs = len(r_s_t_n)
        total_combinations = n*total_graphs

        with tqdm(total=total_combinations, desc="Constructing dict") as pbar:
            pbar.set_postfix(graph=f"0/{total_graphs}")
            iterations = 0
            for idx, G_n in enumerate(r_s_t_n, start=1):
                for i in range(n):
                    G_n_minus_one = G_n.copy()
                    G_n_minus_one.remove_node(i)
                    if len(mapping) > 0:
                        found_isomorphism = False
                        for G_star, mapping_at_G_star in mapping.items():
                            isomorphisms = list(nx.isomorphism.vf2pp_all_isomorphisms(G_n_minus_one, G_star))
                            if isomorphisms:
                                neighbors = set(G_n.neighbors(i))
                                for isomorphism in isomorphisms:
                                    isomorphic_neighbors = tuple(sorted((isomorphism[neighbor] for neighbor in neighbors), reverse=True))
                                    mapping_at_G_star.add(isomorphic_neighbors)
                                found_isomorphism = True
                                break
                        if not found_isomorphism:
                            _add_isomorphic_neighbors(mapping, G_n, G_n_minus_one, i)
                    else:
                        _add_isomorphic_neighbors(mapping, G_n, G_n_minus_one, i)
                    pbar.update(1)
                    iterations += 1
                    if (early_stopping is not None) and (iterations >= early_stopping):
                        break

                if (early_stopping is not None) and (iterations >= early_stopping):
                    break
                pbar.set_postfix(graph=f"{idx}/{total_graphs}")
        return mapping
    
    @classmethod
    def _double_key_construct_mapping(cls, r_s_t_n: set, early_stopping=None) -> dict:
        """
        Generates a mapping with nested hash keys for efficient subgraph isomorphism checks.

        This function iterates over combinations of nodes in each graph in `r_s_t_n`,
        producing subgraphs by node removal. Subgraphs are hashed first by primary keys 
        generated by `TriangleGenerator`, then grouped by isomorphic mappings of pairs 
        of subgraphs. The resulting mapping structure, enables efficient lookup 
        by double-key hashing.

        Parameters
        ----------
        r_s_t_n : set of nx.Graph
            Set of graphs used for generating the subgraphs with double-key hashing.
        early_stopping : int, optional
            Stops execution early after a set number of iterations.

        Returns
        -------
        tuple
            Returns `mapping` with all isomorphic mappings and `reduced_mapping`, a subset 
            containing one representative per isomorphism group.
        """
        mapping = {}
        reduced_mapping = {}

        # Get n
        for G_n in r_s_t_n:
            n = G_n.order()
            break

        total_graphs = len(r_s_t_n)
        total_combinations = sum(math.comb(G_n.order(), G_n.order()//2) for G_n in r_s_t_n)

        with tqdm(total=total_combinations, desc="Processing combinations") as pbar:
            pbar.set_postfix(graph=f"0/{total_graphs}")
            iterations = 0
            for idx, G_n in enumerate(r_s_t_n, start=1):
                nodes = list(G_n.nodes())
                
                for comb in combinations(nodes, n//2):
                    inv_comb = [node for node in nodes if node not in comb]
                    edges_across = [(u,v) for u, v in G_n.edges(comb) if v in inv_comb]
                    G_1 = G_n.copy()
                    G_1.remove_nodes_from(inv_comb)
                    key_1 = KeyGenerator.generate_key(G_1, method="triangle")
                    G_2 = G_n.copy()
                    G_2.remove_nodes_from(comb)
                    key_2 = KeyGenerator.generate_key(G_2, method="triangle")
                    # These are the graphs used to index, by default G_1 and G_2 but if an isomorphism is found then it becomes that val.
                    G_index_1 = G_1
                    G_index_2 = G_2
                    if key_1 in mapping:
                        found_isomorphism_1 = False
                        for G_star_1 in mapping[key_1].keys():
                            isomorphisms_1 = list(nx.isomorphism.vf2pp_all_isomorphisms(G_1, G_star_1))
                            if isomorphisms_1:
                                G_index_1 = G_star_1
                                found_isomorphism_1 = True
                                break
                        if found_isomorphism_1:
                            if key_2 in mapping[key_1][G_index_1]:
                                found_isomorphism_2 = False
                                for G_star_2 in mapping[key_1][G_index_1][key_2].keys():
                                    isomorphisms_2 = list(nx.isomorphism.vf2pp_all_isomorphisms(G_2, G_star_2))
                                    if isomorphisms_2:
                                        G_index_2 = G_star_2
                                        found_isomorphism_2 = True
                                        break
                                if not found_isomorphism_2:
                                    G_index_2 = G_2
                                    isomorphisms_2 = list(nx.isomorphism.vf2pp_all_isomorphisms(G_2, G_2))
                            else:
                                G_index_2 = G_2
                                isomorphisms_2 = list(nx.isomorphism.vf2pp_all_isomorphisms(G_2, G_2))
                        else:
                            G_index_1 = G_1
                            G_index_2 = G_2
                            isomorphisms_1 = list(nx.isomorphism.vf2pp_all_isomorphisms(G_1, G_1))
                            isomorphisms_2 = list(nx.isomorphism.vf2pp_all_isomorphisms(G_2, G_2))
                    else:
                        G_index_1 = G_1
                        G_index_2 = G_2
                        isomorphisms_1 = list(nx.isomorphism.vf2pp_all_isomorphisms(G_1, G_1))
                        isomorphisms_2 = list(nx.isomorphism.vf2pp_all_isomorphisms(G_2, G_2))
                    
                    if key_1 not in mapping:
                        mapping[key_1] = {}
                    if G_index_1 not in mapping[key_1]:
                        mapping[key_1][G_index_1] = {}
                    if key_2 not in mapping[key_1][G_index_1]:
                        mapping[key_1][G_index_1][key_2] = {}
                    if G_index_2 not in mapping[key_1][G_index_1][key_2]:
                        mapping[key_1][G_index_1][key_2][G_index_2] = set()
                    for isomorphism_1 in isomorphisms_1:
                        for isomorphism_2 in isomorphisms_2:
                            isomorphic_edges_across = tuple(sorted([(isomorphism_1[u], isomorphism_2[v]) for (u, v) in edges_across]))
                            mapping[key_1][G_index_1][key_2][G_index_2].add(isomorphic_edges_across)

                    # Reduced mapping only has 1 val per isomorphism group.
                    if key_1 not in reduced_mapping:
                        reduced_mapping[key_1] = {}
                    if G_index_1 not in reduced_mapping[key_1]:
                        reduced_mapping[key_1][G_index_1] = {}
                    if key_2 not in reduced_mapping[key_1][G_index_1]:
                        reduced_mapping[key_1][G_index_1][key_2] = {}
                    if G_index_2 not in reduced_mapping[key_1][G_index_1][key_2]:
                        reduced_mapping[key_1][G_index_1][key_2][G_index_2] = set()
                    for isomorphism_1 in isomorphisms_1:
                        for isomorphism_2 in isomorphisms_2:
                            isomorphic_edges_across = tuple(sorted([(isomorphism_1[u], isomorphism_2[v]) for (u, v) in edges_across]))
                            reduced_mapping[key_1][G_index_1][key_2][G_index_2].add(isomorphic_edges_across)
                            break
                        break

                    pbar.update(1)
                    iterations += 1
                    if (early_stopping is not None) and (iterations >= early_stopping):
                        break

                if (early_stopping is not None) and (iterations >= early_stopping):
                    break
                pbar.set_postfix(graph=f"{idx}/{total_graphs}")

        return mapping, reduced_mapping