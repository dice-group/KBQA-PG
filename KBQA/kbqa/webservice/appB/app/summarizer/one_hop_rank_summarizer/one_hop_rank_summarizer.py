"""Summarizer, which combines one hop triples and ranked tripels."""
from math import inf
import os
import time
from typing import Dict
from typing import List
from typing import Tuple

from app.summarizer import BaseSummarizer
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
    confidence : float, optional
        Confidence for entity recognition (default: 0.5).
    lower_rank : int, optional
        Lower bound for the ranked triples. Only triples with a rank greater or
        equal to this parameter are summarized (should be at least 1).
    max_triples : int, optional
        Limit the number of occurences of triples, which have the same subject and
        predictes or the same predicate and object (default: 3).
    limit : int, optional
        Limit the number of triples found by the summarizer (use -1 to not use any limit,
        default: -1).
    filtering : bool, optional
        Filter all resources and predicates, which don't have an @en tag (default: True).
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
        confidence: float = 0.5,
        lower_rank: int = 1,
        max_triples: int = 3,
        limit: int = -1,
        filtering: bool = True,
        timeout: float = 0,
        verbose: bool = True,
    ) -> None:

        if datasets not in self.DATASETS:
            raise ValueError(f"Dataset {datasets} is not supported")

        if lower_rank < 1:
            raise ValueError("Lower rank cannot be smaller than 1")

        self.datasets = datasets
        self.confidence = confidence
        self.lower_rank = lower_rank
        self.max_triples = max_triples
        self.limit = limit
        self.filtering = filtering
        self.timeout = timeout
        self.verbose = verbose

    def summarize(self, question: str) -> List[str]:
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
        triples = self.summarize_ranks_confidence(question)

        formated_triples = self._format_triples(triples)

        return formated_triples

    def summarize_ranks_confidence(
        self, question: str
    ) -> List[Tuple[Tuple[URIRef, URIRef, URIRef], float, float]]:
        """Summarize triples and their ranks and confidence score for a given question.

        Parameters
        ----------
        question : Question
            Question object containing the question to summarize.

        Returns
        -------
        list
            List containing objects of the form (triple, rank, confidence), where triple
            is of the form (URIRef, URIRef, URIRef), rank is the corresponding rank of
            the triple and confidence is the confidence score of the recognized entity
            in the triple.
        """
        # ------------------------------ one hop triples ------------------------------
        entities, graph_triples = self._get_graph_triples(question)

        if self.verbose:
            print(
                "Recognized entities:",
                [str(entity).encode("utf-8") for entity in entities],
            )
        # ------------------------------ one hop triples ------------------------------

        # timeout
        time.sleep(self.timeout)

        # ------------------------------ ranking ------------------------------
        dataset = os.path.join(
            os.path.dirname(__file__), f"pickle_objects/{self.datasets}.pickle"
        )
        ranked_triples = triples_for_predicates_all_datasets(
            question, dataset, self.filtering, number_of_triples=9999999
        )
        # ------------------------------ ranking ------------------------------

        all_triples = graph_triples + ranked_triples

        filtered_triples = self._filter_triples(all_triples)
        aggregated_triples = self._aggregate_triples(filtered_triples)

        if self.limit > -1:
            limited_triples = self._limit_triples(aggregated_triples)
        else:
            limited_triples = aggregated_triples

        return limited_triples

    def _get_graph_triples(
        self, question: str
    ) -> Tuple[List[URIRef], List[Tuple[Tuple[URIRef, URIRef, URIRef], float, float]]]:
        entities = list()
        triples = list()

        one_hop_graphs = entity_relation_hops(
            question,
            confidence=self.confidence,
            hops=1,
            relation_pos=1,
            limit=self.max_triples,
        )

        for one_hop_graph in one_hop_graphs:
            entity = one_hop_graph[0]
            regular_graph = one_hop_graph[1]
            inverse_graph = one_hop_graph[2]
            confidence = one_hop_graph[3]

            entities.append(entity)

            for subj, pred, obj in regular_graph:
                triple = (subj, pred, obj)

                triples.append((triple, inf, confidence))

            for subj, pred, obj in inverse_graph:
                triple = (subj, pred, obj)

                triples.append((triple, inf, confidence))

        return entities, triples

    def _filter_triples(
        self, triples: List[Tuple[Tuple[URIRef, URIRef, URIRef], float, float]]
    ) -> List[Tuple[Tuple[URIRef, URIRef, URIRef], float, float]]:
        updated_triples = list()

        for triple in triples:
            # check rank, predicate and confidence
            if (
                triple[1] >= self.lower_rank
                and triple[0][1].n3() not in self.EXCLUDE
                and triple[2] >= self.confidence
            ):
                updated_triples.append(triple)

        return updated_triples

    def _aggregate_triples(
        self, triples: List[Tuple[Tuple[URIRef, URIRef, URIRef], float, float]]
    ) -> List[Tuple[Tuple[URIRef, URIRef, URIRef], float, float]]:
        updated_triples = list()
        counter_dict: Dict[Tuple, int] = dict()

        for triple in triples:
            subj, pred = triple[0][0], triple[0][1]
            if (subj, pred) in counter_dict:
                if counter_dict[(subj, pred)] < self.max_triples - 1:
                    counter_dict[(subj, pred)] += 1

                    updated_triples.append(triple)
            else:
                counter_dict[(subj, pred)] = 0
                updated_triples.append(triple)

        return updated_triples

    def _limit_triples(
        self, triples: List[Tuple[Tuple[URIRef, URIRef, URIRef], float, float]]
    ) -> List[Tuple[Tuple[URIRef, URIRef, URIRef], float, float]]:
        result = list()
        counter = 0

        for triple in triples:
            if counter < self.limit:
                result.append(triple)

                counter += 1

        return result

    def _format_triples(
        self, triples: List[Tuple[Tuple[URIRef, URIRef, URIRef], float, float]]
    ) -> List[str]:
        formated_triples = list()

        for triple in triples:
            formated_triple = (
                f"{triple[0][0].n3()} {triple[0][1].n3()} {triple[0][2].n3()}"
            )

            formated_triples.append(formated_triple)

        return formated_triples
