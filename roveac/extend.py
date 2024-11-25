"""
Searches
=============

This module provides the `Search` class, which defines methods for searching within a given 
Ramsey graph based on specific parameters.

Classes
-------
Search
    Class for performing searches on Ramsey graphs.
"""

from functools import reduce
from tqdm import tqdm
from itertools import islice
from concurrent.futures import ThreadPoolExecutor
import threading
import networkx as nx
from roveac.counter_checker import CounterChecker
from roveac.isomorphism_hasher import IsomorphismHasher
from roveac.mapping_constructor import MappingConstructor
from roveac.key_generator import KeyGenerator

class Extender:
    """
    Class for performing one vertex extension from a given ramsey graph.

    Methods
    -------
    search(method: str, r_s_t_n: set, s: int, t: int, extension_method: str, mapping_constructor_method: str, hash_method: str, check_method: str, generate_key_method: str, dict_early_stopping=None, search_early_stopping=None) -> list
        Searches within R(s, t, n) based on given parameters and returns a list of results.
    """

    @classmethod
    def extend(cls, r_s_t_n: set,  
               s: int, 
               t: int, 
               extension_method: str, 
               mapping_constructor_method: str,
               hash_method: str, 
               check_method: str, 
               generate_key_method: str,
               dict_early_stopping=None, 
               extend_early_stopping=None,
               parallel=False) -> list:
        """
        Perform a search within the graph R(s, t, n) based on the provided parameters.

        Parameters
        ----------
        r_s_t_n : set of nx.Graph
            Set of candidate graphs for the `R(s, t, n)` configuration.
        s : int
            Size parameter for clique checks.
        t : int
            Size parameter for independent set checks.
        extension_method : str
            Denotes which extension method to use.
        mapping_constructor_method : str
            Denotes which `MappingConstructor` method to use.
        hash_method : str
            Denotes which `IsomorphismHasher` method to use.
        check_method : str
            Denotes which `CounterChecker` method to use.
        generate_key_method : str
            Denotes which `KeyGenerator` method to use.
        dict_early_stopping : int, optional
            Stops dictionary construction after a specified number of iterations.
        search_early_stopping : int, optional
            Stops the search after a specified number of iterations.
        parallel: bool, optional
            Performs extension method in parallel. May not be implemented for all methods.    
        
        Returns
        -------
        list
            A list of results from the search within the Ramsey graph.
        """
        if extension_method == "ove":
            return cls._one_vertex_extension(r_s_t_n=r_s_t_n,
                                    mapping_constructor_method=mapping_constructor_method,
                                    hash_method=hash_method,
                                    check_method=check_method,
                                    generate_key_method=generate_key_method,
                                    s=s,
                                    t=t,
                                    dict_early_stopping=dict_early_stopping,
                                    extend_early_stopping=extend_early_stopping,
                                    parallel=parallel)
        raise ValueError("Unknown method provided for extending.")


    @classmethod  
    def _generate_flattened_counterexamples(cls, counterexamples: dict) -> list:
        """
        Given a dictionary of counterexamples where the keys are some property and values are
        lists of counterexamples, flatten the dictionary.

        Parameters
        ----------
        counterexamples : dict
            A dictionary of existing counterexamples

        Returns
        -------
        list
            List of counterexamples
        """
        flattened_counterexamples = []
        for value in counterexamples.values():
            flattened_counterexamples.extend(value)

        return flattened_counterexamples

    @classmethod
    def _one_vertex_extension(cls,
                    r_s_t_n: set, 
                    s: int,
                    t: int,
                    mapping_constructor_method: str,
                    hash_method: str,
                    check_method: str,
                    generate_key_method: str,
                    dict_early_stopping=None,
                    extend_early_stopping=None,
                    parallel=False) -> list:
        """
        Search `R(s, t, n)` for `R(s, t, n+1)` counterexamples through neighbor evaluation.

        This method iterates through graphs in `r_s_t_n`, adding a new node (`v'`) to each 
        graph to produce potential candidates for `R(s, t, n+1)`. It evaluates each candidate's 
        neighbors, performing isomorphism checks and counterexample verification as required.

        Parameters
        ----------
        r_s_t_n : set of nx.Graph
            Set of candidate graphs for the `R(s, t, n)` configuration.
        s : int
            Size parameter for clique checks.
        t : int
            Size parameter for independent set checks.
        mapping_constructor_method : str
            Denotes which `MappingConstructor` method to use.
        hash_method : str
            Denotes which `IsomorphismHasher` method to use.
        check_method : str
            Denotes which `CounterChecker` method to use.
        generate_key_method : str
            Denotes which `KeyGenerator` method to use.
        dict_early_stopping : int, optional
            Stops dictionary construction after a specified number of iterations.
        extend_early_stopping : int, optional
            Stops the extend after a specified number of iterations.

        Returns
        -------
        list
            List of counterexample graphs found in `R(s, t, n+1)`.
        """
        found_counterexamples = {}
        mapping = MappingConstructor.construct_mapping(r_s_t_n=r_s_t_n, method=mapping_constructor_method, early_stopping=dict_early_stopping)

        # Get n
        for G_n in r_s_t_n:
            n = G_n.order()
            break
             
        # Prepare the total number of iterations
        num_counterexamples = len(r_s_t_n)
        total_iterations = num_counterexamples * n

        if parallel:
            lock = threading.Lock()

        def check_and_add_counterexample(G_prime, parallel):
            key = KeyGenerator.generate_key(G_prime, method=generate_key_method)

            def add_counterexample():
                if key in found_counterexamples:
                    new_counterexample = True
                    for counterexample in found_counterexamples[key]:
                        if nx.is_isomorphic(G_prime, counterexample):
                            new_counterexample = False
                            break
                    if new_counterexample:
                        G_prime_copied = G_prime.copy()
                        found_counterexamples[key].append(G_prime_copied)
                else:
                    G_prime_copied = G_prime.copy()
                    found_counterexamples[key] = [G_prime_copied]

            if parallel:
                with lock:
                    add_counterexample()
            else:
                add_counterexample()

        def check_and_update_counterexample(isomorphic_neighbors, keys_j, G_prime, G_n, i, j, parallel):
            if isomorphic_neighbors in reduce(lambda d, key: d[key], keys_j, mapping):
                is_counter = CounterChecker.check(
                    method=check_method,
                    G_n=G_n,
                    G_prime=G_prime,
                    mapping=mapping,
                    hash_method=hash_method,
                    passed_indices=[i, j], # Maybe I add n to this?
                    n=n,
                    s=s,
                    t=t
                )
                if is_counter:
                    check_and_add_counterexample(G_prime, parallel=parallel)

        def process_idx_i(args, parallel):
            idx, G_n, i = args
            G_prime = G_n.copy()
            # Add v_prime
            G_prime.add_node(n)

            # Remove node i
            G_n_min_i = G_n.copy()
            G_n_min_i.remove_node(i)
            keys_i, isomorphism_i = IsomorphismHasher.hash(G=G_n_min_i, mapping=mapping, method=hash_method)

            # Remove node j
            j = (i + 1) % n
            G_n_min_j = G_n.copy()
            G_n_min_j.remove_node(j)
            keys_j, isomorphism_j = IsomorphismHasher.hash(G=G_n_min_j, mapping=mapping, method=hash_method)

            # Process neighbors
            process_neighbors(G_prime, G_n, keys_i, isomorphism_i, keys_j, isomorphism_j, i, j, parallel)

            pbar.update(1)
            pbar.set_postfix(graph=f"{idx}/{num_counterexamples}")

        def process_neighbors(G_prime, G_n, keys_i, isomorphism_i, keys_j, isomorphism_j, i, j, parallel):
            inv_isomorphism_i = {v: k for k, v in isomorphism_i.items()}
            for neighbors in reduce(lambda d, key: d[key], keys_i, mapping):
                # Clear old edges
                G_prime.remove_node(n)
                G_prime.add_node(n)
                # Map neighbors from G_D_i to G_n_minus_one
                inv_iso_neighbors = [inv_isomorphism_i[neighbor] for neighbor in neighbors]
                G_prime.add_edges_from([(n, neighbor) for neighbor in inv_iso_neighbors])
                v_prime_neighbors = set(G_prime.neighbors(n))
                v_prime_neighbors.discard(j)
                isomorphic_neighbors = tuple(sorted((isomorphism_j[neighbor] for neighbor in v_prime_neighbors), reverse=True))

                # Case where (v_i,v') set to 0
                check_and_update_counterexample(isomorphic_neighbors, keys_j, G_prime, G_n, i, j, parallel)

                # Case where (v_i,v') set to 1
                isomorphic_i = isomorphism_j[i]
                G_prime.add_edge(n, i)
                isomorphic_neighbors = tuple(sorted((*isomorphic_neighbors, isomorphic_i), reverse=True))

                check_and_update_counterexample(isomorphic_neighbors, keys_j, G_prime, G_n, i, j, parallel)

        # Adjust total iterations if early stopping is set
        if extend_early_stopping is not None:
            total_iterations = min(total_iterations, extend_early_stopping)

        # TODO: remove compliments from G_n iteration
        # Create an iterator over all combinations of idx and i
        idx_i_iterator = ((idx, G_n, i) for idx, G_n in enumerate(r_s_t_n, start=1) for i in range(n))

        # Apply early stopping using islice
        if extend_early_stopping is not None:
            idx_i_iterator = islice(idx_i_iterator, extend_early_stopping)

        args_list = list(idx_i_iterator)

        with tqdm(total=total_iterations, desc="Searching dict") as pbar:
            if not parallel:
                with tqdm(total=total_iterations, desc="OVE") as pbar:
                    for args in args_list:
                        process_idx_i(args, parallel=False)
            else:
                with ThreadPoolExecutor() as executor:
                    list(executor.map(lambda args: process_idx_i(args, parallel=True), args_list))

        flattened_counterexamples = cls._generate_flattened_counterexamples(found_counterexamples)

        return flattened_counterexamples