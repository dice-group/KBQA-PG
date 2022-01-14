"""Summarizer, which extracts a subgraph of based on one hop and ranked triples."""
from collections import Counter
from collections import defaultdict
from typing import DefaultDict
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple

from data_generator.summarizer import Summarizer
from entity_relation_hops.entity_relation_hops import entity_relation_hops
from entity_relation_hops.entity_relation_hops import get_subgraphs_based_on_relations
from ranking.ranking import get_ranking_tables
from rdflib import Graph
from rdflib.term import URIRef


class OneHopRankSummarizer(Summarizer):
    """OneHopRankSummarizer.

    Summarizer, which combines a one- hop graph with recognized entities
    and relations and ranked triples based on a dataset.

    Parameters
    ----------
    dataset_path : str
        Path to a dataset.
    lower_rank : int, optional
        Lower bound for the ranked triples. Only triples with a rank greater or
        equal to this parameter are summarized (should be at least 1).
    limit : int, optional
        Limit the number of occurences of triples, which have the same subject and
        predictes or the same predicate and object (default: 3).
    extend_preds : bool, optional
        Extend the ranked predicates by their counterpart of "ontology" and "property".
        This might increase the number of triples, but might also be more precise
        (default: False).

    Raises
    ------
    ValueError
        If lower_rank is not greater or equal to 1.
    ValueError
        If dataset_path does not contain qald or lc-quad.
    """

    PRINT = False
    DATASET_PATH = "datasets/"
    EXCLUDE = [
        "http://dbpedia.org/ontology/abstract",
        "http://dbpedia.org/ontology/wikiPageWikiLink",
    ]

    def __init__(
        self,
        dataset_path: Optional[str] = None,
        lower_rank: int = 1,
        limit: int = 3,
        extend_preds: bool = False,
    ) -> None:

        if dataset_path is None:
            qald_8_path = self.DATASET_PATH + "qald-8-train-multilingual.json"
            qald_9_path = self.DATASET_PATH + "qald-9-train-multilingual.json"
            lc_quad_path = self.DATASET_PATH + "lc-quad-train.json"

            qald_8_regular_preds, qald_8_inverse_preds = get_ranking_tables(
                qald_8_path, datasettype="qald"
            )
            qald_9_regular_preds, qald_9_inverse_preds = get_ranking_tables(
                qald_9_path, datasettype="qald"
            )
            lc_quad_regular_preds, lc_quad_inverse_preds = get_ranking_tables(
                lc_quad_path, datasettype="lc-quad"
            )

            self.regular_predicates = combine_predicates(
                qald_8_regular_preds, qald_9_regular_preds, lc_quad_regular_preds
            )
            self.inverse_predicates = combine_predicates(
                qald_8_inverse_preds, qald_9_inverse_preds, lc_quad_inverse_preds
            )

        else:

            if "qald" in dataset_path:
                self.regular_predicates, self.inverse_predicates = get_ranking_tables(
                    dataset_path, datasettype="qald"
                )
            elif "lc-quad" in dataset_path:
                self.regular_predicates, self.inverse_predicates = get_ranking_tables(
                    dataset_path, datasettype="lc-quad"
                )
            else:
                raise ValueError("Dataset does not contain qald or lc-quad.")

        if extend_preds:
            self.regular_predicates = extend_predicates(self.regular_predicates)
            self.inverse_predicates = extend_predicates(self.inverse_predicates)

        if lower_rank < 1:
            raise ValueError("Lower rank cannot be smaller than 1")

        self.regular_predicates = self._filter_predicates(
            self.regular_predicates, lower_rank
        )
        self.inverse_predicates = self._filter_predicates(
            self.inverse_predicates, lower_rank
        )

        self.lower_rank = lower_rank
        self.limit = limit

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
        graph = Graph()

        # triples with one hop and recognized relations
        one_hop_graphs = entity_relation_hops(
            question, hops=1, relation_pos=1, limit=self.limit
        )
        entities = list()

        for sub_graph in one_hop_graphs:
            combined_graph = sub_graph[1] + sub_graph[2]
            graph += combined_graph

            entities.append(sub_graph[0])

        print("Recognized entities:", entities)

        # ranked triples
        regular_rank_graph, inverse_rank_graph = self._get_ranked_triples_for_dataset(
            entities
        )

        regular_rank_graph = aggregate_regular_triples(regular_rank_graph, self.limit)
        inverse_rank_graph = aggregate_inverse_triples(inverse_rank_graph, self.limit)

        graph += regular_rank_graph
        graph += inverse_rank_graph

        if self.PRINT:
            for subj, pred, obj in graph:
                print(subj, pred, obj)

        print("Number of triples:", len(graph))

        triples = format_graph(graph)

        return triples

    def _filter_predicates(
        self, predicates: Dict[str, int], lower_bound: int
    ) -> Dict[str, int]:
        """Filter predicates and remove predicates with rank lower than lower bound.

        Parameters
        ----------
        predicates : dict
            Dictionary with predicates as keys and ranks as values.
        lower_bound : int
            Lower bound for rank of predicates.

        Returns
        -------
        updated_predicates : dict
            Updated dictionary with predicates having ranks greater or equal to lower bound.
        """
        updated_predicates = {}

        for pred, rank in predicates.items():
            if pred not in self.EXCLUDE and rank >= lower_bound:
                updated_predicates[pred] = rank

        return updated_predicates

    def _get_ranked_triples_for_dataset(
        self, entities: List[str]
    ) -> Tuple[Graph, Graph]:
        """Get graphs containing all triples extracted by the ranked predicates.

        Parameters
        ----------
        entities : list
            List of recognized entities from a question.

        Returns
        -------
        regular_graph : Graph
            Graph with outgoing edges from the entities.
        inverse_graph : Graph
            Graph with ingoing edges from the entities.
        """
        regular_graph = Graph()
        inverse_graph = Graph()

        reg_predicates = predicates_to_uriref(self.regular_predicates)
        inv_predicates = predicates_to_uriref(self.inverse_predicates)

        for entity in entities:
            reg_graph, _ = get_subgraphs_based_on_relations(entity, reg_predicates)
            _, inv_graph = get_subgraphs_based_on_relations(entity, inv_predicates)

            regular_graph += reg_graph
            inverse_graph += inv_graph

        return regular_graph, inverse_graph


def combine_predicates(
    qald_8: Dict[str, int], qald_9: Dict[str, int], lc_quad: Dict[str, int]
) -> Dict[str, int]:
    """Combine the dictionaries containing the ranked predicates into one dictionary.

    Parameters
    ----------
    qald_8 : dict
        Predicates from QALD-8 dataset.
    qald_9 : dict
        Predicates from QALD-8 dataset.
    lc_quad : dict
        Predicates from QALD-8 dataset.

    Returns
    -------
    combined_dict : dict
        Combined dictionary with all predicates and their ranks added up.
    """
    q_8 = Counter(qald_8)
    q_9 = Counter(qald_9)
    lc_q = Counter(lc_quad)

    combined_dict = q_8 + q_9 + lc_q

    return combined_dict


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


def aggregate_regular_triples(graph: Graph, limit: int) -> Graph:
    """Aggregate similiar triples to <limit> triples.

    Given a graph with triples, extract the first <limit> triples
    of the form <s> <p> <...> to remove triples of the same form.

    Parameters
    ----------
    graph : Graph
        The graph to aggregate.
    limit : int
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
            if regular_dict[(subj, pred)] < limit:
                regular_dict[(subj, pred)] += 1

                updated_graph.add((subj, pred, obj))
        else:
            regular_dict[(subj, pred)] = 0
            updated_graph.add((subj, pred, obj))

    return updated_graph


def aggregate_inverse_triples(graph: Graph, limit: int) -> Graph:
    """Aggregate similiar triples to <limit> triples.

    Given a graph with triples, extract the first <limit> triples
    of the form <...> <p> <o> to remove triples of the same form.

    Parameters
    ----------
    graph : Graph
        The graph to aggregate.
    limit : int
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
            if inverse_dict[(pred, obj)] < limit - 1:
                inverse_dict[(pred, obj)] += 1

                updated_graph.add((subj, pred, obj))
        else:
            inverse_dict[(pred, obj)] = 0
            updated_graph.add((subj, pred, obj))

    return updated_graph


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


def extend_predicates(predicates: Dict[str, int]) -> Dict[str, int]:
    """Extend the predicates by "ontology" and "property".

    Since DBpedia makes a difference between properties from "ontology"
    and "property", it is possible to add the counterpart to the
    predicates.

    Parameters
    ----------
    predicates : dict
        Dictionary containing the predicates and their ranks.

    Returns
    -------
    extended_predicates : dict
        Updated dictionary containing the predicates and their ranks.
    """
    extended_predicates = {}

    for predicate, rank in predicates.items():
        if "ontology" in predicate:
            extended_predicate = predicate.replace("ontology", "property")
            extended_predicates[extended_predicate] = rank

        if "property" in predicate:
            extended_predicate = predicate.replace("property", "ontology")
            extended_predicates[extended_predicate] = rank

        extended_predicates[predicate] = rank

    return extended_predicates
