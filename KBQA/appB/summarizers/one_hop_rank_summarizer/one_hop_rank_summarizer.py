"""Summarizer, which combines one hop triples and ranked tripels."""
import os
import time
from typing import Dict
from typing import List
from typing import Tuple

from KBQA.appB.data_generator import Question
from KBQA.appB.summarizers import BaseSummarizer
from rdflib import Graph
from rdflib import URIRef

from .entity_relation_hops import entity_relation_hops
from .multihop_triples import triples_for_predicates_all_datasets


class OneHopRankSummarizer(BaseSummarizer):
    """OneHopRankSummarizer.

    Summarizer, which combines a one- hop graph with recognized entities
    and relations and ranked triples based on a dataset.

    Parameters
    ----------
    datasets : str, optional
        Permuation of the datasets for the ranked predicates (default: qald8_qald9_lcquad).
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
    verbose : bool
        Print some statemets if True (default: True).

    Raises
    ------
    ValueError
        If lower_rank is not greater or equal to 1 or dataset is not supported.
    """

    DATASETS = [
        "qald8_qald9_lcquad",
        "qald9_qald8_lcquad",
        "qald8_lcquad_qald9",
        "qald9_lcquad_qald8",
        "lcquad_qald8_qald9",
        "lcquad_qald9_qald8",
    ]
    EXCLUDE = [
        "<http://dbpedia.org/ontology/abstract>",
        "<http://dbpedia.org/wikiPageWikiLink>",
    ]

    def __init__(
        self,
        datasets: str = "qald8_qald9_lcquad",
        lower_rank: int = 1,
        max_triples: int = 3,
        limit: int = -1,
        timeout: float = 0,
        verbose: bool = True,
    ) -> None:

        if datasets not in self.DATASETS:
            raise ValueError(f"Dataset {datasets} is not supported")

        if lower_rank < 1:
            raise ValueError("Lower rank cannot be smaller than 1")

        self.datasets = datasets
        self.lower_rank = lower_rank
        self.max_triples = max_triples
        self.limit = limit
        self.timeout = timeout
        self.verbose = verbose

    def summarize(self, question: Question) -> List[str]:
        """Summarize a subgraph for a given question.

        Parameters
        ----------
        question : Question
            Question object containing the question to summarize.

        Returns
        -------
        list
            List containing the triples in the format <subj> <pred> <obj>.
        """
        # ------------------------------ one hop triples ------------------------------
        entities, summarized_graph = self._get_summarized_graph(question.text)

        if self.verbose:
            print("Recognized entities:", entities)

        formated_graph = self._format_graph(summarized_graph)
        # ------------------------------ one hop triples ------------------------------

        # timeout
        time.sleep(self.timeout)

        if self.limit > -1:
            cur_limit = self.limit - len(summarized_graph)
        else:
            cur_limit = 9999999

        # ------------------------------ ranking ------------------------------
        # dataset = f"./pickle_objects/{self.datasets}.pickle"
        dataset = os.path.join(
            os.path.dirname(__file__), f"pickle_objects\\{self.datasets}.pickle"
        )

        ranked_triples = triples_for_predicates_all_datasets(
            question.text, dataset, number_of_triples=cur_limit
        )
        filtered_triples = self._filter_triples(ranked_triples)
        aggregated_triples = self._aggregate_triples(filtered_triples)
        formated_triples = self._format_triples(aggregated_triples)
        # ------------------------------ ranking ------------------------------

        result = formated_graph + formated_triples

        return result

    def _get_summarized_graph(self, question: str) -> Tuple[List[URIRef], Graph]:
        summarized_graph = Graph()

        one_hop_graphs = entity_relation_hops(
            question, hops=1, relation_pos=1, limit=self.max_triples
        )
        entities = list()

        for sub_graph in one_hop_graphs:
            combined_graph = sub_graph[1] + sub_graph[2]
            summarized_graph += combined_graph

            entities.append(sub_graph[0])

        if self.limit > -1:
            summarized_graph = self._limit_graph(summarized_graph)

        return entities, summarized_graph

    def _limit_graph(self, graph: Graph) -> Graph:
        """Limit the number of triples in a graph.

        Given a graph, reduce the number of triples to the first
        <limit> triples.

        Parameters
        ----------
        graph : Graph
            Graph containing all triples.

        Returns
        -------
        limited_graph : Graph
            Graph with at most <limit> triples.
        """
        limited_graph = Graph()
        num_triples = 0

        for subj, pred, obj in graph:
            if num_triples < self.limit:
                limited_graph.add((subj, pred, obj))

                num_triples += 1

        return limited_graph

    def _format_graph(self, graph: Graph) -> List[str]:
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

    def _filter_triples(self, triples: List) -> List[Tuple[URIRef, URIRef, URIRef]]:
        updated_triples = list()

        for triple in triples:
            # check rank and predicate
            if triple[1] >= self.lower_rank and triple[0][1].n3() not in self.EXCLUDE:
                updated_triples.append(triple[0])

        return updated_triples

    def _aggregate_triples(
        self, triples: List[Tuple[URIRef, URIRef, URIRef]]
    ) -> List[Tuple[URIRef, URIRef, URIRef]]:
        updated_triples = list()
        counter_dict: Dict[Tuple, int] = dict()

        for triple in triples:
            subj, pred = triple[0], triple[1]
            if (subj, pred) in counter_dict:
                if counter_dict[(subj, pred)] < self.max_triples - 1:
                    counter_dict[(subj, pred)] += 1

                    updated_triples.append(triple)
            else:
                counter_dict[(subj, pred)] = 0
                updated_triples.append(triple)

        return updated_triples

    def _format_triples(
        self, triples: List[Tuple[URIRef, URIRef, URIRef]]
    ) -> List[str]:
        formated_triples = list()

        for triple in triples:
            formated_triple = f"{triple[0].n3()} {triple[1].n3()} {triple[2].n3()}"

            formated_triples.append(formated_triple)

        return formated_triples
