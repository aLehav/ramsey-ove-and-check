"""
Searches
=============

This module provides the `Search` class, which defines methods for searching within a given 
Ramsey graph based on specific parameters.

Classes
-------
Search : ABC
    Abstract base class for performing searches on Ramsey graphs.
"""

from functools import reduce
from tqdm import tqdm
from itertools import islice
from concurrent.futures import ThreadPoolExecutor
import threading
import networkx as nx

class Search:
    """
    Abstract base class for performing searches within a Ramsey graph.

    Methods
    -------
    search(method: str, r_s_t_n: set, s: int, t: int) -> list
        Searches within R(s, t, n) based on given parameters and returns a list of results.
    """

    @classmethod
    def search(cls, method: str, r_s_t_n: set, s: int, t: int) -> list:
        """
        Perform a search within the graph R(s, t, n) based on the provided parameters.

        Parameters
        ----------
        method: str
            Denotes which method to use to construct the dictionary.
        r_s_t_n : set
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

class BaseSearch(Search):
    """
    Determines the existence of `R(s, t, n+1)` counterexamples within a given `R(s, t, n)` set.

    This class extends `Search` to evaluate if a set of candidate graphs contains any 
    counterexamples for `R(s, t, n+1)`. Depending on the results, it concludes either 
    that all counterexamples exist within the set (indicating `R(s, t) > n+1`), or that 
    more elements may need to be examined or generated to fully determine `R(s, t) = n+1`.

    Methods
    -------
    search(r_s_t_n: set, construct_dict, hash, check, generate_key, s: int, t: int, dict_early_stopping=None, search_early_stopping=None) -> list
        Searches `R(s, t, n)` for any `R(s, t, n+1)` counterexamples by examining each graph's 
        potential neighbors and checking against specific conditions.
    """
    @classmethod
    def search(cls, r_s_t_n: set, construct_dict, hash, check, generate_key, s:int, t:int, dict_early_stopping=None, search_early_stopping=None) -> list:
        """
        Search `R(s, t, n)` for `R(s, t, n+1)` counterexamples through neighbor evaluation.

        This method iterates through graphs in `r_s_t_n`, adding a new node (`v'`) to each 
        graph to produce potential candidates for `R(s, t, n+1)`. It evaluates each candidate's 
        neighbors, performing isomorphism checks and counterexample verification as required.

        Parameters
        ----------
        r_s_t_n : set of nx.Graph
            Set of candidate graphs for the `R(s, t, n)` configuration.
        construct_dict : callable
            Function to construct a dictionary `D` of subgraphs for efficient retrieval.
        hash : callable
            Hash function for identifying isomorphic subgraphs.
        check : callable
            Function for verifying if a graph qualifies as a counterexample.
        generate_key : callable
            Function to generate unique keys for identifying graph configurations.
        s : int
            Size parameter for clique checks.
        t : int
            Size parameter for independent set checks.
        dict_early_stopping : int, optional
            Stops dictionary construction after a specified number of iterations.
        search_early_stopping : int, optional
            Stops the search after a specified number of iterations.

        Returns
        -------
        list
            List of counterexample graphs found in `R(s, t, n+1)`.
        """
        def check_and_add_counterexample(G_prime, L):
            key = generate_key(G_prime)
            if key in L:
                new_counterexample = True
                for counterexample in L[key]:
                    if nx.isomorphism.is_isomorphic(G_prime, counterexample):
                        new_counterexample = False
                        break
                if new_counterexample:
                    G_prime_copied = G_prime.copy()
                    L[key].append(G_prime_copied)
            else:
                G_prime_copied = G_prime.copy()
                L[key] = [G_prime_copied]

        def process_neighbors(G_prime, G_n, G_n_min_i, keys_i, isomorphism_i, G_n_min_j, keys_j, isomorphism_j, i, j):
            inv_isomorphism_i = {v: k for k, v in isomorphism_i.items()}
            for neighbors in reduce(lambda d, key: d[key], keys_i, D):
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
                check_and_update_counterexample(isomorphic_neighbors, keys_j, G_prime, G_n, i, j)
                
                # Case where (v_i,v') set to 1
                assert not G_prime.has_edge(n, i)
                isomorphic_i = isomorphism_j[i]
                G_prime.add_edge(n, i)
                # TODO: Find faster way to add i
                isomorphic_neighbors = list(isomorphic_neighbors)
                isomorphic_neighbors.insert(0, isomorphic_i)
                isomorphic_neighbors = tuple(sorted(isomorphic_neighbors, reverse=True))
                    
                check_and_update_counterexample(isomorphic_neighbors, keys_j, G_prime, G_n, i, j)

        def check_and_update_counterexample(isomorphic_neighbors, keys_j, G_prime, G_n, i, j):
            if isomorphic_neighbors in reduce(lambda d, key: d[key], keys_j, D):
                is_counter = check(
                    G_n=G_n,
                    G_prime=G_prime,
                    D=D,
                    hash=hash,
                    passed_indices=[i, j], # Maybe I add n to this?
                    n=n,
                    s=s,
                    t=t
                )
                if is_counter:
                    check_and_add_counterexample(G_prime, L)

        L = {}
        D = construct_dict(r_s_t_n=r_s_t_n, early_stopping=dict_early_stopping)
        # print_set_lengths(D)

        # Get n
        for G_n in r_s_t_n:
            n = G_n.order()
            break

        total_graphs = len(r_s_t_n)
        total_combinations = n*total_graphs

        # TODO: remove compliments from G_n iteration
        with tqdm(total=total_combinations, desc="Searching dict") as pbar:
            pbar.set_postfix(graph=f"0/{total_graphs}")
            iterations = 0
            for idx, G_n in enumerate(r_s_t_n, start=1):
                G_prime = G_n.copy()
                assert not n in G_n
                # Add v_prime
                G_prime.add_node(n)
                for i in range(n):
                    G_n_min_i = G_n.copy()
                    G_n_min_i.remove_node(i)
                    keys_i, isomorphism_i = hash(G=G_n_min_i,D=D)
                    G_n_min_j = G_n.copy()
                    j = (i+1) % n
                    G_n_min_j.remove_node(j)
                    keys_j, isomorphism_j = hash(G=G_n_min_j,D=D)
                    process_neighbors(G_prime, G_n, G_n_min_i, keys_i, isomorphism_i, G_n_min_j, keys_j, isomorphism_j, i, j)
                    pbar.update(1)
                    iterations += 1
                    if (search_early_stopping is not None) and (iterations >= search_early_stopping):
                        break

                if (search_early_stopping is not None) and (iterations >= search_early_stopping):
                    break
                pbar.set_postfix(graph=f"{idx}/{total_graphs}")

        flattened_L = []
        for key, value in L.items():
            flattened_L.extend(value)

        return flattened_L
    
class ImprovedSearch(Search):
    """
    Searches `R(s, t, n)` to identify any `R(s, t, n+1)` counterexamples within a given set of graphs.

    This class extends `Search` to perform an optimized, parallelized search for potential counterexamples.
    It provides a conclusion of either "yes, L has all counterexamples" (implying `R(s, t) > n+1`) or "no," 
    suggesting that `R(s, t, n)` might need additional elements or that `R(s, t) = n+1`.

    Parameters
    ----------
    r_s_t_n : set
        The full set of counterexample graphs to evaluate.
    construct_dict : callable
        Function to construct the dictionary `D` of subgraphs.
    hash : callable
        Hash function used to identify isomorphic subgraphs.
    check : callable
        Function that checks if a graph qualifies as a counterexample.
    generate_key : callable
        Function for generating a unique key for each graph.
    s : int
        Parameter defining the size of cliques to check.
    t : int
        Parameter defining the size of independent sets to check.
    dict_early_stopping : int or None, optional
        Limits the number of dictionary construction iterations if specified.
    search_early_stopping : int or None, optional
        Limits the total search iterations if specified.

    Methods
    -------
    search(r_s_t_n: set, construct_dict, hash, check, generate_key, s: int, t: int, dict_early_stopping=None, search_early_stopping=None) -> list
        Conducts a parallelized search for counterexamples in `R(s, t, n+1)` using neighbor-based evaluations.
    """
    @classmethod
    def search(cls, r_s_t_n: set, construct_dict, hash, check, generate_key, s:int, t:int, dict_early_stopping=None, search_early_stopping=None) -> list:
        """
        Perform a parallelized search on `R(s, t, n)` to identify `R(s, t, n+1)` counterexamples.

        This method iterates through each graph in `r_s_t_n`, adding a new node (`v'`) to each 
        to create candidate graphs for `R(s, t, n+1)`. It evaluates neighbors, applies isomorphism 
        checks, and identifies potential counterexamples.

        Parameters
        ----------
        r_s_t_n : set of nx.Graph
            Set of graphs representing the current counterexample candidates.
        construct_dict : callable
            Function for constructing a dictionary `D` of subgraphs to optimize lookups.
        hash : callable
            Function for hashing subgraphs to identify isomorphic structures.
        check : callable
            Function to verify if a graph qualifies as a counterexample.
        generate_key : callable
            Function to generate unique keys for identifying graph configurations.
        s : int
            The size of cliques to check.
        t : int
            The size of independent sets to check.
        dict_early_stopping : int, optional
            Stops dictionary construction early if specified.
        search_early_stopping : int, optional
            Limits the number of search iterations if specified.

        Returns
        -------
        list
            List of identified counterexample graphs.
        """
        lock = threading.Lock()
        L = {}
        D = construct_dict(r_s_t_n=r_s_t_n, early_stopping=dict_early_stopping)

        # Get n
        for G_n in r_s_t_n:
            n = G_n.order()
            break

        # Prepare the total number of iterations
        num_counterexamples = len(r_s_t_n)
        total_iterations = num_counterexamples * n

        # Adjust total iterations if early stopping is set
        if search_early_stopping is not None:
            total_iterations = min(total_iterations, search_early_stopping)

        # Create an iterator over all combinations of idx and i
        idx_i_iterator = ((idx, G_n, i) for idx, G_n in enumerate(r_s_t_n, start=1) for i in range(n))

        # Apply early stopping using islice
        if search_early_stopping is not None:
            idx_i_iterator = islice(idx_i_iterator, search_early_stopping)

        args_list = list(idx_i_iterator)

        with tqdm(total=total_iterations, desc="Searching dict") as pbar:

            def process_idx_i(args):
                idx, G_n, i = args
                G_prime = G_n.copy()
                # Add v_prime
                G_prime.add_node(n)

                # Remove node i
                G_n_min_i = G_n.copy()
                G_n_min_i.remove_node(i)
                keys_i, isomorphism_i = hash(G=G_n_min_i, D=D)

                # Remove node j
                j = (i + 1) % n
                G_n_min_j = G_n.copy()
                G_n_min_j.remove_node(j)
                keys_j, isomorphism_j = hash(G=G_n_min_j, D=D)

                # Process neighbors
                process_neighbors(G_prime, G_n, keys_i, isomorphism_i, keys_j, isomorphism_j, i, j)

                pbar.update(1)
                pbar.set_postfix(graph=f"{idx}/{num_counterexamples}")

            def process_neighbors(G_prime, G_n, keys_i, isomorphism_i, keys_j, isomorphism_j, i, j):
                inv_isomorphism_i = {v: k for k, v in isomorphism_i.items()}
                for neighbors in reduce(lambda d, key: d[key], keys_i, D):
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
                    check_and_update_counterexample(isomorphic_neighbors, keys_j, G_prime, G_n, i, j)

                    # Case where (v_i,v') set to 1
                    isomorphic_i = isomorphism_j[i]
                    G_prime.add_edge(n, i)
                    isomorphic_neighbors = tuple(sorted((*isomorphic_neighbors, isomorphic_i), reverse=True))

                    check_and_update_counterexample(isomorphic_neighbors, keys_j, G_prime, G_n, i, j)

            def check_and_update_counterexample(isomorphic_neighbors, keys_j, G_prime, G_n, i, j):
                if isomorphic_neighbors in reduce(lambda d, key: d[key], keys_j, D):
                    is_counter = check(
                        G_n=G_n,
                        G_prime=G_prime,
                        D=D,
                        hash=hash,
                        passed_indices=[i, j, n],
                        n=n,
                        s=s,
                        t=t
                    )
                    if is_counter:
                        check_and_add_counterexample(G_prime)

            def check_and_add_counterexample(G_prime):
                key = generate_key(G_prime)
                with lock:
                    if key in L:
                        new_counterexample = True
                        for counterexample in L[key]:
                            if nx.is_isomorphic(G_prime, counterexample):
                                new_counterexample = False
                                break
                        if new_counterexample:
                            G_prime_copied = G_prime.copy()
                            L[key].append(G_prime_copied)
                    else:
                        G_prime_copied = G_prime.copy()
                        L[key] = [G_prime_copied]

            with ThreadPoolExecutor() as executor:
                list(executor.map(process_idx_i, args_list))

        flattened_L = []
        for key, value in L.items():
            flattened_L.extend(value)

        return flattened_L