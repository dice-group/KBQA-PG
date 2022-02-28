"""A module to get ranking of triples for predicates from QALD dataset."""
import pickle
from typing import List

from nes_ner_hop import ner_dbpedia_spotlight
from rdflib.graph import Graph
from rdflib.plugins.sparql import prepareQuery
from rdflib.term import URIRef


def ask_for_entities(question: str, *, confidence: float = 0.8) -> List[URIRef]:
    """
    Given a question string. List of entities is returned.

    :param question: question string.
    :param confidence: A confidence value in [0,1] which determines how confident the algorithm is in the found
    entities.
    :return: List of entities in URIref.
    """
    entities = ner_dbpedia_spotlight(question, confidence=confidence)
    return entities


def get_ranked_triples(
    entities: List[URIRef],
    *,
    limit: int = -1,
    number_of_triples: int = 100,
    number_triples_each_predicate: int = 10,
) -> List[URIRef]:
    """
    Given a list of entities from the question. List with necessary number of triples in ranked order is returned..

    :param entities: list of URIref of entities.
    :param limit: A natural number which limits the number of triples for each found entity.
    :param number_of_triples: necessary number of triples.
    :param number_triples_each_predicate: boundary of triples for each predicate and for each entity.
    :return: List of triples in URIref.
    """
    # Determine if we have a limit or not.
    if limit == -1:
        limit_str = ""
    else:
        limit_str = f"LIMIT {limit}"

    query_1hop = prepareQuery(
        f"""
        CONSTRUCT {{ ?s1 ?p1 ?o1 }}
        WHERE {{
            SERVICE <http://dbpedia.org/sparql> {{
                ?s1 ?p1 ?o1.
            }}
        }}
        {limit_str}
        """
    )
    query_2hop = prepareQuery(
        f"""
        CONSTRUCT {{ ?s1 ?p1 ?o1. ?o1 ?p2 ?o2 }}
        WHERE {{
            SERVICE <http://dbpedia.org/sparql> {{
                ?s1 ?p1 ?o1. ?o1 ?p2 ?o2
            }}
        }}
        {limit_str}
        """
    )
    with open("predicates_rank.pickle", "rb") as file:
        rank_table = pickle.load(file)
        tripleslist = []
    for triples in rank_table:
        # query for one hope predicate and add triples from subgraph
        for entity in entities:
            subgraph = Graph()
            # This is only querying the service endpoint and not subgraph.
            if len(triples) == 1:
                subgraph_entity = subgraph.query(
                    query_1hop, initBindings={"s1": entity, "p1": triples[0]}
                )
            elif len(triples) == 2:
                # query for two hopes predicates, add triples from subgraph
                subgraph_entity = subgraph.query(
                    query_2hop,
                    initBindings={"s1": entity, "p1": triples[0], "p2": triples[1]},
                )
            for triple in subgraph_entity:
                if len(subgraph) == number_triples_each_predicate:
                    break
                subgraph.add(triple)
            for triple in subgraph:
                tripleslist.append(triple)
                if len(tripleslist) == number_of_triples:
                    return tripleslist
    return tripleslist


def main() -> None:
    """Call get_ranket_triples to get triples with highest rank."""
    entities = ask_for_entities("Where live Jennifer Lopez and Barack Obama?")
    triples = get_ranked_triples(entities)
    print(len(triples))
    for item in triples:
        print(item)
        print("\n")


# Call from shell as main.
if __name__ == "__main__":
    main()
