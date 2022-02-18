"""Summarizer, which extracts a subgraph of based on one hop and ranked triples."""
from collections import Counter
from collections import defaultdict
from math import inf
import time
from typing import DefaultDict
from typing import Dict
from typing import List
from typing import Tuple

from rdflib import Graph
from rdflib.term import URIRef
from KBQA.appB.data_generator.summarizer import Summarizer
from KBQA.appB.summarizers.entity_relation_hops.entity_relation_hops import (
    entity_relation_hops,
)
from KBQA.appB.summarizers.entity_relation_hops.entity_relation_hops import (
    get_subgraphs_based_on_relations,
)
from KBQA.appB.summarizers.ranking.ranking import get_ranking_tables
from KBQA.appB.summarizers.ranking.ranking import rank_list


class OneHopRankSummarizer(Summarizer):
    """OneHopRankSummarizer.

    Summarizer, which combines a one- hop graph with recognized entities
    and relations and ranked triples based on a dataset.

    Parameters
    ----------
    lower_rank : int, optional
        Lower bound for the ranked triples. Only triples with a rank greater or
        equal to this parameter are summarized (should be at least 1).
    max_triples : int, optional
        Limit the number of occurences of triples, which have the same subject and
        predictes or the same predicate and object (default: 3).
    limit : int, optional
        Limit the number of triples found by the summarizer (use -1 to not use any limit,
        default: -1).
    timeout : float, optional
        Set a timeout in seconds between requests. This might avoid some connection
        errors (default: 0).

    Raises
    ------
    ValueError
        If lower_rank is not greater or equal to 1.
    """

    PRINT = False
    DATASET_PATH = "./../../datasets/"
    EXCLUDE = [
        "http://dbpedia.org/ontology/abstract",
    ]
    # "http://dbpedia.org/ontology/wikiPageWikiLink",

    def __init__(
        self,
        lower_rank: int = 1,
        max_triples: int = 3,
        limit: int = -1,
        timeout: float = 0,
    ) -> None:

        if lower_rank < 1:
            raise ValueError("Lower rank cannot be smaller than 1")

        self.lower_rank = lower_rank
        self.max_triples = max_triples
        self.limit = limit
        self.timeout = timeout

        self._initialize_qald_predicates()
        self._initialize_lc_quad_predicates()

    def summarize(self, question: str) -> List[str]:
        """Summarize a subgraph based on the entities from a question.

        Given a natural langugae question, extract a subgraph based on
        recognized entities and relations from a question and ranked triples
        based on a dataset.

        Parameters
        ----------
        question : str
            A natural language question.

        Returns
        -------
        triples : list
            A list of triples found by the summarizer in the format "<s> <p> <o>"
        """
        entities, summarized_graph = self._get_summarized_graph(question)

        print("Recognized entities:", entities)

        # timeout
        time.sleep(self.timeout)

        # ranked triples
        qald_triples, lc_quad_triples = self._get_ranked_triples(entities)

        # format triples: <subj> <pred> <obj>
        summarizer_formated = format_graph(summarized_graph)

        qald_formated = format_triples_by_order(qald_triples)
        lc_quad_formated = format_triples_by_order(lc_quad_triples)

        ranked_triples_formated = qald_formated + lc_quad_formated

        if self.limit > -1:
            cur_limit = float(self.limit - len(summarized_graph))
        else:
            cur_limit = inf

        limited_ranked_triples_formated = limit_triples(
            ranked_triples_formated, cur_limit
        )

        formated_triples = summarizer_formated + limited_ranked_triples_formated

        if self.PRINT:
            for triple in formated_triples:
                print(triple)

        print("Number of triples:", len(formated_triples))

        return formated_triples

    def _initialize_qald_predicates(self) -> None:
        # qald
        qald_8_train_regular_preds, qald_8_train_inverse_preds = get_ranking_tables(
            self.DATASET_PATH + "qald-8-train-multilingual.json", datasettype="qald"
        )
        qald_9_train_regular_preds, qald_9_train_inverse_preds = get_ranking_tables(
            self.DATASET_PATH + "qald-9-train-multilingual.json", datasettype="qald"
        )

        qald_train_regular_preds = combine_predicates(
            qald_8_train_regular_preds, qald_9_train_regular_preds
        )
        qald_train_inverse_preds = combine_predicates(
            qald_8_train_inverse_preds, qald_9_train_inverse_preds
        )

        qald_8_test_regular_preds, qald_8_test_inverse_preds = get_ranking_tables(
            self.DATASET_PATH + "qald-8-test-multilingual.json", datasettype="qald"
        )
        qald_9_test_regular_preds, qald_9_test_inverse_preds = get_ranking_tables(
            self.DATASET_PATH + "qald-9-test-multilingual.json", datasettype="qald"
        )

        qald_test_regular_preds = combine_predicates(
            qald_8_test_regular_preds, qald_9_test_regular_preds
        )
        qald_test_inverse_preds = combine_predicates(
            qald_8_test_inverse_preds, qald_9_test_inverse_preds
        )

        self.qald_regular_preds = combine_predicates(
            qald_train_regular_preds, qald_test_regular_preds
        )
        self.qald_inverse_preds = combine_predicates(
            qald_train_inverse_preds, qald_test_inverse_preds
        )

        self.qald_regular_preds = combine_predicates(
            qald_train_regular_preds, qald_test_regular_preds
        )
        self.qald_inverse_preds = combine_predicates(
            qald_train_inverse_preds, qald_test_inverse_preds
        )

        self.qald_regular_preds = filter_predicates(
            self.qald_regular_preds, self.EXCLUDE, self.lower_rank
        )
        self.qald_inverse_preds = filter_predicates(
            self.qald_inverse_preds, self.EXCLUDE, self.lower_rank
        )

    def _initialize_lc_quad_predicates(self) -> None:
        # lc-quad
        lc_quad_train_regular_preds, lc_quad_train_inverse_preds = get_ranking_tables(
            self.DATASET_PATH + "lc-quad-train.json", datasettype="lc-quad"
        )

        lc_quad_test_regular_preds, lc_quad_test_inverse_preds = get_ranking_tables(
            self.DATASET_PATH + "lc-quad-test.json", datasettype="lc-quad"
        )

        self.lc_quad_regular_preds = combine_predicates(
            lc_quad_train_regular_preds, lc_quad_test_regular_preds
        )
        self.lc_quad_inverse_preds = combine_predicates(
            lc_quad_train_inverse_preds, lc_quad_test_inverse_preds
        )

        self.lc_quad_regular_preds = filter_predicates(
            self.lc_quad_regular_preds, self.EXCLUDE, self.lower_rank
        )
        self.lc_quad_inverse_preds = filter_predicates(
            self.lc_quad_inverse_preds, self.EXCLUDE, self.lower_rank
        )

    def _get_summarized_graph(self, question: str) -> Tuple[List[URIRef], Graph]:
        summarized_graph = Graph()

        # triples with one hop and recognized relations
        one_hop_graphs = entity_relation_hops(
            question, hops=1, relation_pos=1, limit=self.max_triples
        )
        entities = list()

        for sub_graph in one_hop_graphs:
            combined_graph = sub_graph[1] + sub_graph[2]
            summarized_graph += combined_graph

            entities.append(sub_graph[0])

        if self.limit > -1:
            summarized_graph = limit_graph(summarized_graph, self.limit)

        return entities, summarized_graph

    def _get_ranked_triples(
        self, entities: List[URIRef]
    ) -> Tuple[DefaultDict[int, List], DefaultDict[int, List]]:
        regular_preds = combine_predicates(
            self.qald_regular_preds, self.lc_quad_regular_preds
        )
        inverse_preds = combine_predicates(
            self.qald_inverse_preds, self.lc_quad_inverse_preds
        )

        reg_graph, inv_graph = subgraphs_for_entities(
            entities, regular_preds, inverse_preds
        )

        # remove triples to have at most <max_triples> of the same form
        aggregated_reg_graph = aggregate_regular_triples(reg_graph, self.max_triples)
        aggregated_inv_graph = aggregate_inverse_triples(inv_graph, self.max_triples)

        # triples with ranks
        qald_reg_rank_list = rank_list(self.qald_regular_preds, aggregated_reg_graph)
        qald_reg_rank_list = filter_predicates(
            qald_reg_rank_list, self.EXCLUDE, self.max_triples
        )

        qald_inv_rank_list = rank_list(self.qald_inverse_preds, aggregated_inv_graph)
        qald_inv_rank_list = filter_predicates(
            qald_inv_rank_list, self.EXCLUDE, self.lower_rank
        )

        lc_quad_reg_rank_list = rank_list(
            self.lc_quad_regular_preds, aggregated_reg_graph
        )
        lc_quad_reg_rank_list = filter_predicates(
            lc_quad_reg_rank_list, self.EXCLUDE, self.lower_rank
        )

        lc_quad_inv_rank_list = rank_list(
            self.lc_quad_inverse_preds, aggregated_inv_graph
        )
        lc_quad_inv_rank_list = filter_predicates(
            lc_quad_inv_rank_list, self.EXCLUDE, self.lower_rank
        )

        # combined triples for qald and lc-quad inverted: triples : rank --> rank : triples
        qald_triples = combine_triples_by_rank(qald_reg_rank_list, qald_inv_rank_list)
        lc_quad_triples = combine_triples_by_rank(
            lc_quad_reg_rank_list, lc_quad_inv_rank_list
        )

        return qald_triples, lc_quad_triples


def combine_predicates(
    dataset_1: Dict[str, int], dataset_2: Dict[str, int]
) -> Dict[str, int]:
    """Combine the dictionaries containing the ranked predicates into one dictionary.

    Parameters
    ----------
    dataset_1 : dict
        Predicates from QALD-8 dataset.
    dataset_2 : dict
        Predicates from QALD-9 dataset.

    Returns
    -------
    combined_dict : dict
        Combined dictionary with all predicates and their ranks added up.
    """
    d_1 = Counter(dataset_1)
    d_2 = Counter(dataset_2)

    combined_dict = d_1 + d_2

    return combined_dict


def filter_predicates(
    predicates: Dict[str, int], exclude: List, lower_bound: int
) -> Dict[str, int]:
    """Filter predicates and remove predicates with rank lower than lower bound.

    Parameters
    ----------
    predicates : dict
        Dictionary with predicates as keys and ranks as values.
    exclude : list
        List of predicates (DBpedia-relations), which should be removed.
    lower_bound : int
        Lower bound for rank of predicates.

    Returns
    -------
    updated_predicates : dict
        Updated dictionary with predicates having ranks greater or equal to lower bound.
    """
    updated_predicates = {}

    for pred, rank in predicates.items():
        if pred not in exclude and rank >= lower_bound:
            updated_predicates[pred] = rank

    return updated_predicates


def subgraphs_for_entities(
    entities: List[URIRef],
    regular_preds: Dict[str, int],
    inverse_preds: Dict[str, int],
) -> Tuple[Graph, Graph]:
    """Get graphs containing all triples extracted by the ranked predicates.

    Parameters
    ----------
    entities : list
        List of recognized entities from a question.
    regular_preds : dict
        Dictionary containing the ranked regular predicates.
    inverse_preds : Graph
        Dictionary containing the ranked inverse predicates.

    Returns
    -------
    regular_graph : Graph
        Graph with outgoing edges from the entities.
    inverse_graph : Graph
        Graph with ingoing edges to the entities.
    """
    regular_graph = Graph()
    inverse_graph = Graph()

    reg_predicates = predicates_to_uriref(regular_preds)
    inv_predicates = predicates_to_uriref(inverse_preds)

    for entity in entities:
        reg_graph, _ = get_subgraphs_based_on_relations(entity, reg_predicates)
        _, inv_graph = get_subgraphs_based_on_relations(entity, inv_predicates)

        regular_graph += reg_graph
        inverse_graph += inv_graph

    return regular_graph, inverse_graph


def predicates_to_uriref(predicates: Dict[str, int]) -> List[str]:
    """Convert a dictionary with ranked predicates into list of URIRefs.

    Parameters
    ----------
    predicates : dict
        Dictionary with predicates (URIs) as keys and ranks as values.

    Returns
    -------
    result : list
        List of URIRefs of predicates in the dictionary.
    """
    result = list()

    for pred, _ in predicates.items():
        result.append(URIRef(pred))

    return result


def aggregate_regular_triples(graph: Graph, max_triples: int) -> Graph:
    """Aggregate similiar triples to <limit> triples.

    Given a graph with triples, extract the first <limit> triples
    of the form <s> <p> <...> to remove triples of the same form.

    Parameters
    ----------
    graph : Graph
        The graph to aggregate.
    max_triples : int
        The maximum number of triples of the form <s> <p> <...>.

    Returns
    -------
    updated_graph : Graph
        Graph with at most <limit> triples of the form <s> <p> <...>.
    """
    updated_graph = Graph()
    regular_dict: DefaultDict = defaultdict(int)

    for subj, pred, obj in graph:
        if subj == "" or obj == "":
            continue

        if (subj, pred) in regular_dict:
            if regular_dict[(subj, pred)] < max_triples - 1:
                regular_dict[(subj, pred)] += 1

                updated_graph.add((subj, pred, obj))
        else:
            regular_dict[(subj, pred)] = 0
            updated_graph.add((subj, pred, obj))

    return updated_graph


def aggregate_inverse_triples(graph: Graph, max_triples: int) -> Graph:
    """Aggregate similiar triples to <limit> triples.

    Given a graph with triples, extract the first <limit> triples
    of the form <...> <p> <o> to remove triples of the same form.

    Parameters
    ----------
    graph : Graph
        The graph to aggregate.
    max_triples : int
        The maximum number of triples of the form <...> <p> <o>.

    Returns
    -------
    updated_graph : Graph
        Graph with at most <limit> triples of the form <...> <p> <o>.
    """
    updated_graph = Graph()
    inverse_dict: DefaultDict = defaultdict(int)

    for subj, pred, obj in graph:
        if (pred, obj) in inverse_dict:
            if inverse_dict[(pred, obj)] < max_triples - 1:
                inverse_dict[(pred, obj)] += 1

                updated_graph.add((subj, pred, obj))
        else:
            inverse_dict[(pred, obj)] = 0
            updated_graph.add((subj, pred, obj))

    return updated_graph


def combine_triples_by_rank(
    reg_triples: Dict[str, int],
    inv_triples: Dict[str, int],
) -> DefaultDict[int, List]:
    """Combine regular and inverse triples by their rank into a new dictionary.

    Parameters
    ----------
    reg_triples : dict
        Dictionary containing regular triples as key and their ranks as value.
    inv_triples : dict
        Dictionary containing inverse triples as key and their ranks as value.

    Returns
    -------
    combined_triples : defaultdict
        Dictionary containing the ranks as keys and all triples in a list with this rank as value.
    """
    combined_triples = defaultdict(list)

    for triple, rank in reg_triples.items():
        combined_triples[rank].append(triple)

    for triple, rank in inv_triples.items():
        combined_triples[rank].append(triple)

    return combined_triples


def limit_graph(graph: Graph, limit: int) -> Graph:
    """Limit the number of triples in a graph.

    Given a graph, reduce the number of triples to the first
    <limit> triples.

    Parameters
    ----------
    graph : Graph
        Graph containing all triples.
    limit : int
        Number of maximal triples in the given graph.

    Returns
    -------
    limited_graph : Graph
        Graph with at most <limit> triples.
    """
    limited_graph = Graph()
    num_triples = 0

    for subj, pred, obj in graph:
        if num_triples < limit:
            limited_graph.add((subj, pred, obj))

            num_triples += 1

    return limited_graph


def format_graph(graph: Graph) -> List[str]:
    """Format triples in a graph into the <s> <p> <o> format.

    Parameters
    ----------
    graph : Graph
        The graph to format.

    Returns
    -------
    triples : list
        List of strings for each triple in the correct format.
    """
    triples = list()

    for subj, pred, obj in graph:
        triple = f"<{subj}> <{pred}> <{obj}>"

        triples.append(triple)

    return triples


def limit_triples(triples: List[str], limit: float) -> List[str]:
    """Limit the number of triples.

    Given a list of triples, extract the <limit> triples from this list.

    Parameters
    ----------
    triples : list
        List of triples in the format <subj> <pred> <obj>.
    limit : int
        Number of maximal triples in the list.

    Returns
    -------
    limited_triples : list
        List with the first <limit> triples from the given triple list.
    """
    limited_triples = list()
    num_triples = 0

    for triple in triples:
        if num_triples < limit:
            limited_triples.append(triple)

            num_triples += 1

    return limited_triples


def format_triples_by_order(
    triples: Dict[int, List[Tuple[URIRef, URIRef, URIRef]]]
) -> List[str]:
    """Sort the triples by their ranks and store them in a list in the correct output format.

    Parameters
    ----------
    triples : dict
        Dictionary containing the ranks as keys and the triples in a list as values.

    Returns
    -------
    formated_triples : list
        List of strings for each triple in the correct order.
    """
    sorted_triples = sorted(triples.items(), reverse=True)
    ordered_triple_list = list()

    for _, triple_list in sorted_triples:
        ordered_triple_list += triple_list

    formated_triples = list()

    for triple in ordered_triple_list:
        formated_triple = f"{triple[0].n3()} {triple[1].n3()} {triple[2].n3()}"

        formated_triples.append(formated_triple)

    return formated_triples
