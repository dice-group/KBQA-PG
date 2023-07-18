"""A module to use NES (named entity summarization)."""
from typing import List
from typing import Tuple

from rdflib.graph import Graph
from rdflib.plugins.sparql import prepareQuery
from rdflib.term import URIRef
import requests


def nes_ner_hop(question: str, *, confidence: float = 0.8, limit: int = -1) -> Graph:
    """Given a question, a subgraph of dbpedia is returned based on the entities found in the question.

    Given a question, first, the named entities in dbpedia are recognized. Based on them, a subgraph is returned,
    which consists of the traversed graph while doing a breath-first-search of depth one which starts on each found
    named entity separately.

    :param question: The question as string.
    :param confidence: A confidence value in [0,1] which determines how confident the algorithm is in the found
    entities.
    :param limit: A natural number which limits the number of triples for each found entity.
    :return: A rdflib.graph.Graph which is a set of triples.
    """
    print(question)
    entities = ner_dbpedia_spotlight(question, confidence=confidence)
    subgraph = hop_dbpedia_subgraph(entities, limit=limit)
    return subgraph


def ner_dbpedia_spotlight(question: str, *, confidence: float = 0.8) -> List[URIRef]:
    """Named entities are returned for a given question.

    :param question: The question to be annotated.
    :param confidence: The confidence of the annotation.
    :return: list of rdflib.term.URIRef which are objects for URIs.
    """
    # Ask dbpedia spotlight for an annotation of question
    webserver_address = "https://api.dbpedia-spotlight.org/en/annotate"
    response = requests.post(
        webserver_address,
        data={"text": question, "confidence": confidence},
        headers={"Accept": "application/json"},
        timeout=120,
    ).json()

    named_entities: List[URIRef] = []
    # If no named entity found
    if "Resources" not in response:
        return named_entities
    # Else gather all named entities
    for resource in response["Resources"]:
        named_entities.append(URIRef(resource["@URI"]))

    return named_entities


def hop_dbpedia_subgraph(entities: List[URIRef], *, limit: int = -1) -> Graph:
    """Given entities, a subgraph of dbpedia is returned based on the entities found in the question.

    Given a list of entities, a subgraph from dbpedia is returned which consists of the traversed nodes and edges
    in a breath-first-search of depth one and starting at each given entity individually.

    :param entities: A list of rdflib.term.URIRef where each entity is a root node for breath-first-search.
    :param limit: An optional limit for the number of triples per entity.
    :return: The subgraph of type rdflib.graph.Graph.
    """
    # Determine if we have a limit or not.
    if limit == -1:
        limit_str = ""
    else:
        limit_str = f"LIMIT {limit}"

    query = prepareQuery(
        f"""
        CONSTRUCT {{ ?s ?p ?o }}
        WHERE {{
            SERVICE <http://dbpedia.org/sparql> {{
                ?s ?p ?o .
            }}
        }}
        {limit_str}
        """
    )
    subgraph = Graph()
    for entity in entities:
        # This is only querying the service endpoint and not subgraph.
        subgraph_entity = subgraph.query(query, initBindings={"s": entity})
        subgraph_entity_inverse = subgraph.query(query, initBindings={"o": entity})
        for triple in subgraph_entity:
            subgraph.add(triple)
        for triple in subgraph_entity_inverse:
            subgraph.add(triple)
    return subgraph


def nes_ner_hop_regular_and_inverse_subgraph(
    question: str, *, confidence: float = 0.8, limit: int = -1
) -> Tuple[Graph, Graph]:
    """Given a question, two sub-graphs are returned based on the entities found in the question.

    Given a question, first, the named entities in dbpedia are recognized. Based on them, two sub-graphs are returned,
    which consist of the traversed graph while doing a breath-first-search of depth one which starts on each found
    named entity separately. The first returned subgraph is build by following the relations between entities along the
    relation direction. The second follows the relation inversely.

    :param question: The question as string.
    :param confidence: A confidence value in [0,1] which determines how confident the algorithm is in the found
    entities.
    :param limit: A natural number which limits the number of triples for each found entity.
    :return: A pair (class tuple) of rdflib.graph.Graph which are sets of triples. First for regular and second for
    inverse relations.
    """
    entities = ner_dbpedia_spotlight(question, confidence=confidence)
    regular_subgraph, inverse_subgraph = hop_dbpedia_regular_and_inverse_subgraph(
        entities, limit=limit
    )
    return regular_subgraph, inverse_subgraph


def hop_dbpedia_regular_and_inverse_subgraph(
    entities: List[URIRef], *, limit: int = -1
) -> Tuple[Graph, Graph]:
    """Given entities, two sub-graphs are returned based on the entities found in the question.

    Given a list of entities, two sub-graphs are returned, which consist of the traversed graph while doing a
    breath-first-search of depth one which starts on each found named entity separately. The first returned subgraph is
    build by following the relations between entities along the relation direction. The second follows the relation
    inversely.

    :param entities: A list of rdflib.term.URIRef where each entity is a root node for breath-first-search.
    :param limit: An optional limit for the number of triples per entity.
    :return: A pair (class tuple) of rdflib.graph.Graph which are sets of triples. First for regular and second for
    inverse relations.
    """
    # Determine if we have a limit or not.
    if limit == -1:
        limit_str = ""
    else:
        limit_str = f"LIMIT {limit}"

    query = prepareQuery(
        f"""
        CONSTRUCT {{ ?s ?p ?o }}
        WHERE {{
            SERVICE <http://dbpedia.org/sparql> {{
                ?s ?p ?o .
            }}
        }}
        {limit_str}
        """
    )
    regular_subgraph = Graph()
    inverse_subgraph = Graph()
    for entity in entities:
        # This is only querying the service endpoint and not subgraph.
        subgraph_entity = regular_subgraph.query(query, initBindings={"s": entity})
        subgraph_entity_inverse = inverse_subgraph.query(
            query, initBindings={"o": entity}
        )
        for triple in subgraph_entity:
            regular_subgraph.add(triple)
        for triple in subgraph_entity_inverse:
            inverse_subgraph.add(triple)
    return regular_subgraph, inverse_subgraph


def main() -> None:
    """Start this module from as __main__ (e.g. from commandline) to invoke this function.

    nes_ner_hop {--question | -q} <question> [{--limit | -l} <limit>] [{--confidence|-c} <confidence>]
    """
    # Gather the given options.
    (opt_args, _) = getopt.getopt(
        sys.argv[1:], "q:c:l:", ["question=", "confidence=", "limit="]
    )

    has_question = False
    has_confidence = False
    has_limit = False
    for opt, value in opt_args:
        if opt in ("-q", "--question"):
            question = value
            has_question = True
        if opt in ("-c", "--confidence"):
            confidence = float(value)
            has_confidence = True
        if opt in ("-l", "--limit"):
            limit = int(value)
            has_limit = True

    # If no question is given.
    if not has_question:
        print(
            f'Provide some question with "{sys.argv[0]} {{-q | --question}} <some_question>".'
        )
        sys.exit()

    # Decide on the right call to nes_ner_hop (Workaround for nes_ner_hop(question_outer, **arguments)).
    if has_confidence and has_limit:
        triples = nes_ner_hop(question, confidence=confidence, limit=limit)
    elif has_confidence and not has_limit:
        triples = nes_ner_hop(question, confidence=confidence)
    elif not has_confidence and has_limit:
        triples = nes_ner_hop(question, limit=limit)
    else:
        triples = nes_ner_hop(question)

    # Print returned triples.
    print("Num\tTriple")
    for i, triple_outer in enumerate(triples):
        print(f"{i + 1}" + "\t", end="")
        print(triple_outer)
    sys.exit()


# Call from shell as main.
if __name__ == "__main__":
    import sys
    import getopt

    main()
