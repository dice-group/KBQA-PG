"""Module to extract subgraphs from DBpedia based one or two hops."""
import argparse
import json
from typing import List
from typing import Tuple

from rdflib import Graph
from rdflib import URIRef
import requests
from SPARQLWrapper import SPARQLWrapper


EXCLUDES = [URIRef("http://dbpedia.org/ontology/country")]


def entity_relation_hops(
    question: str,
    hops: int = 1,
    relation_pos: int = 1,
    limit: int = 10,
    ignore: bool = False,
) -> List[Tuple[str, Graph, Graph]]:
    """Extract subgraphs from DBpedia.

    Given a natural language question, extract a subgraph from DBpedia for each
    recognized entity in this question. If there are any relations (Dbpedia properties)
    recognized, they can be used to decrease the number of triples and, hence, to get a
    more precise graph.

    Parameters
    ----------
    question : str
        Natural language question.
    hops : int
        Number of hops from a recognized entity. Hops in [1, 2] are supported (default: 1).
    relation_pos : int
        Position of the recognized relations in the graph. If this parameter is greater
        than the number of hops, the relations are ignored (default: 1).
    limit : int
        Limit the number of triples in the result graphs. Use -1 to use not any limit (default: 10).
    ignore : bool
        Set this parameter to ignore all recognized relations.

    Return
    ------
    sub_graphs : list
        List of subgraphs. The list contains tuples (entity, subgraph), where entity is the entity, from
        which the subgraph is extracted (i.e. entity is the center node of the subgraph).
    """
    entities, relations = entity_relation_recognition(question)
    entities_dbs = entity_recognition_dbspotlight(question)
    # print("Entities DBS:", entities_dbs)

    entities += entities_dbs
    entities = list(set(entities))

    sub_graphs = get_subgraph(entities, relations, hops, relation_pos, limit, ignore)

    return sub_graphs


def entity_relation_recognition(question: str) -> Tuple[List[URIRef], List[URIRef]]:
    """Extract all entities and relations from a question.

    Given a natural language question, extract all entities as DBpedia-resources
    and all relations as Dbpedia-properties using FALCON 2.0 (https://arxiv.org/abs/1912.11270).

    Parameters
    ----------
    question : str
        Natural language question.

    Returns
    -------
    entities : list
        List of all recognized entities as URIRef.
    relations : list
        List of all recognized relations as URIRef.
    """
    endpoint = "https://labs.tib.eu/falcon/falcon2/api?mode=long&db=1"

    response = requests.post(
        endpoint,
        headers={"Content-Type": "application/json"},
        data=json.dumps({"text": question}),
    ).json()

    dbpedia_entities = response["entities_dbpedia"]
    dbpedia_relations = response["relations_dbpedia"]

    # print("Entities:", dbpedia_entities)
    print("Relations:", dbpedia_relations)

    entities = []
    relations = []

    for entity in dbpedia_entities:
        if len(entity) > 1:
            resource = URIRef(entity[0])

            entities.append(resource)

    for relation in dbpedia_relations:
        if len(relation) > 1:
            prop = URIRef(relation[0])

            # if prop not in EXCLUDES:
            relations.append(prop)

    return entities, relations


def entity_recognition_dbspotlight(
    question: str, confidence: float = 0.8
) -> List[URIRef]:
    """Entity recognition using DB-Spotlight.

    In addition to FALCON 2.0 DB-Spotlight is used to recognize entities in hope
    to be more precise with the entities.

    Parameters
    ----------
    question : str
        Natural language question.
    confidence : float, optional
        Confidence of the recognized entity (default: 0.8)

    Returns
    -------
    entities : list
        List of recognized entities as URIRefs
    """
    endpoint = "https://api.dbpedia-spotlight.org/en/annotate"

    response = requests.post(
        endpoint,
        headers={"Accept": "application/json"},
        data={"text": question, "confidence": confidence},
    ).json()

    if "Resources" not in response:
        return list()

    entities = list()

    for resource in response["Resources"]:
        entities.append(URIRef(resource["@URI"]))

    return entities


def get_subgraph(
    entities: List[URIRef],
    relations: List[URIRef],
    hops: int,
    relation_pos: int,
    limit: int,
    ignore: bool,
) -> List[Tuple[URIRef, Graph, Graph]]:
    """Extract a subgraph for all entities using the relations.

    Given a list of entities and relations, extract a subgraph for each entity.
    Depending on the chosen parameters the relations can also be excluded from the subgraph.

    Parameters
    ----------
    entities : list
        List of entities as URIRef.
    relations : list
        List of relations as URIRef.
    hops : int
        Number of hops. This value should be in [1,2].
    relation_pos : int
        Position of the relation in the subgraph. This value should be in [1,2].
    limit : int
        Limit the number of triples in the subgraphs. Use -1 to not use any limit.
    ignore : bool
        Setting this parameter will ignore all relations.

    Returns
    -------
    sub_graphs : list
        List of all subgraphs. An element is a tuple (entity, subgraph), where subgraph is the
        corresponding subgraph to an entity with entity as the center node.

    Raises
    ------
    ValueError
        If a parameter is not supported.
    """
    if hops not in [1, 2]:
        raise ValueError("Only hops of size 1 and 2 are supported.")

    if relation_pos not in [1, 2]:
        raise ValueError("Relation can be only at position 1 or 2.")

    if hops == 1 and relation_pos == 2:
        raise ValueError("Relation cannot be at position 2, if there is only one hop.")

    sub_graphs = []

    for entity in entities:
        if len(relations) > 0 and not ignore:
            (
                regular_subgraph,
                inverse_subgraph,
            ) = get_subgraphs_for_entity_with_relations(
                entity, relations, hops, relation_pos, limit
            )

            sub_graphs.append((entity, regular_subgraph, inverse_subgraph))
        elif len(relations) == 0 and not ignore:
            sub_graphs.append((entity, Graph(), Graph()))
        else:
            (
                regular_subgraph,
                inverse_subgraph,
            ) = get_subgraphs_for_entity_without_relations(entity, hops, limit)

            sub_graphs.append((entity, regular_subgraph, inverse_subgraph))

    return sub_graphs


def get_subgraphs_for_entity_with_relations(
    entity: URIRef, relations: List[URIRef], hops: int, relation_pos: int, limit: int
) -> Graph:
    """Extract a subgraph, which takes all relations into consideration.

    Given an entity as the center node, extract a subgraph, which contains
    the given relations as edges at the defined positions.

    Parameters
    ----------
    entity : URIRef
        The entity, which is the center node of the subgraph.
    relations : list
        List of DBpedia-properties describing the relations.
    hops : int
        Number of hops.
    relation_pos : int
        Position of the relations. Setting this parameter to 1 puts the relations
        in the first hop and setting this parameter to 2 puts the relations in the
        second hop.
    limit : int
        Limit the number of triples in the subgraphs. Use -1 to not use any limit.

    Returns
    -------
    subgraph : Graph
        The resulting subgraph.

    Raises
    ------
    ValueError
        If a parameter is not valid.
    """
    regular_subgraph = Graph()
    inverse_subgraph = Graph()

    for relation in relations:
        if hops == 1:
            regular_subgraph += get_regular_subgraph_for_one_hop(
                entity.n3(), relation.n3(), limit
            )
            inverse_subgraph += get_inverse_subgraph_for_one_hop(
                entity.n3(), relation.n3(), limit
            )
        elif hops == 2:
            if relation_pos == 1:
                regular_subgraph += get_regular_subgraph_for_two_hops(
                    entity.n3(), relation.n3(), "?p2", limit
                )
                inverse_subgraph += get_inverse_subgraph_for_two_hops(
                    entity.n3(), relation.n3(), "?p2", limit
                )
            elif relation_pos == 2:
                regular_subgraph += get_regular_subgraph_for_two_hops(
                    entity.n3(), "?p1", relation.n3(), limit
                )
                inverse_subgraph += get_inverse_subgraph_for_two_hops(
                    entity.n3(), "?p1", relation.n3(), limit
                )
            else:
                raise ValueError("Relation can be only at position 1 or 2.")
        else:
            raise ValueError("Number of hops should be in [1, 2]")

    return regular_subgraph, inverse_subgraph


def get_subgraphs_for_entity_without_relations(
    entity: URIRef, hops: int, limit: int
) -> Graph:
    """Extract a subgraph only based on an entity.

    Given an entity as the center node, extract a subgraph with all outgoing and
    ingoing edges on one or two hops.

    Parameters
    ----------
    entity : URIRef
        The entity, which is the center node of the subgraph.
    hops : int
        Number of hops.
    limit : int
        Limit the number of triples in the subgraphs. Use -1 to not use any limit.

    Returns
    -------
    subgraph : Graph
        The resulting subgraph.

    Raises
    ------
    ValueError
        If a parameter is not valid.
    """
    regular_subgraph = Graph()
    inverse_subgraph = Graph()

    if hops == 1:
        regular_subgraph += get_regular_subgraph_for_one_hop(entity.n3(), "?p", limit)
        inverse_subgraph += get_inverse_subgraph_for_one_hop(entity.n3(), "?p", limit)
    elif hops == 2:
        regular_subgraph += get_regular_subgraph_for_two_hops(
            entity.n3(), "?p1", "?p2", limit
        )
        inverse_subgraph += get_inverse_subgraph_for_two_hops(
            entity.n3(), "?p1", "?p2", limit
        )
    else:
        raise ValueError("Number of hops should be in [1, 2]")

    return regular_subgraph, inverse_subgraph


def ask_dbpedia(query: str) -> Graph:
    """Send a SPARQL-query to DBpedia and get the resulting subgraph.

    The query is expected to be a CONSTRUCT-query s.t. a subgraph can be returned.

    Parameters
    ----------
    query : str
        A CONSTRUCT-SPARQL-query.

    Returns
    -------
    result : Graph
        Subgraph contructed by the SPARQL-query.
    """
    sparql = SPARQLWrapper("http://dbpedia.org/sparql/")
    sparql.setQuery(query)

    result = sparql.query().convert()

    return result


def get_regular_subgraph_for_one_hop(entity: str, relation: str, limit: int) -> Graph:
    """Get the subgraph for a given entity with one hop in regular direction.

    Given an entity, get the the subgraph of the form
        entity ---> e1
    where e1 is an entity found by DBpedia.

    Parameters
    ----------
    entity : str
        Entity as DBpedia-resource or as variable.
    relation : str
        Relation as DBpedia-property or as variable.
    limit : int
        Limit the number of triples in the graph (use -1 to not use any limit).

    Returns
    -------
    regular_graph : Graph
        Graph, which contains all triples (entity, relation, e1).
    """
    regular_graph = Graph()

    # entity --relation--> ?o
    query = get_query_for_one_hop(entity, relation, "?o", limit)

    regular_graph += ask_dbpedia(query)

    return regular_graph


def get_inverse_subgraph_for_one_hop(entity: str, relation: str, limit: int) -> Graph:
    """Get the subgraph for a given entity with one hop in inverse direction.

    Given an entity, get the the subgraph of the form
        e1 ---> entity
    where e1 is an entity found by DBpedia.

    Parameters
    ----------
    entity : str
        Entity as DBpedia-resource or as variable.
    relation : str
        Relation as DBpedia-property or as variable.
    limit : int
        Limit the number of triples in the graph (use -1 to not use any limit).

    Returns
    -------
    regular_graph : Graph
        Graph, which contains all triples (e1, relation, entity).
    """
    inverse_graph = Graph()

    # ?s --relation--> entity
    query = get_query_for_one_hop("?s", relation, entity, limit)

    inverse_graph += ask_dbpedia(query)

    return inverse_graph


def get_regular_subgraph_for_two_hops(
    entity: str, p_1: str, p_2: str, limit: int
) -> Graph:
    """Get subgraph for an entity with two hops in forward direction.

    Given an entity, contruct a subgraph of the form
        e1 ---> e2 ---> entity ---> e3 ---> e4
    where e1, e2, e3, e4 are entities found by DBpedia. In order to
    increase the performance, the contruction of this graph is splitted
    into two parts. In the first part a subgraph of the form
        entity --p_1--> e3 --p-2--> e4
    is contructed. In the second part a subgraph of the form
        e1 --p_2--> e2 --p_1--> entity
    is contructed. Combining these two subgraphes gives the whole
    graph with the entity as the center node and all outgoing edges
    of length one or two (length one, if the second hop cannot be found).

    Parameters
    ----------
    entity : str
        Entity as DBpedia-resource or as variable.
    p_1 : str
        Relation in the first hop as DBpedia-property or as variable.
    p_2 : str
        Relation in the second hop as DBpedia-property or as variable.
    limit : int
        Limit the number of triples in the graph (use -1 to not use any limit).

    Returns
    -------
    result_graph : Graph
        Graph with the entity as center node and outgoing edges of length one or two.
    """
    regular_graph = Graph()

    # entity --p1--> e1 --p2--> e2
    query = get_query_for_two_hops(entity, p_1, p_2, limit)
    regular_graph += ask_dbpedia(query)

    return regular_graph


def get_inverse_subgraph_for_two_hops(
    entity: str, p_1: str, p_2: str, limit: int
) -> Graph:
    """Extract subgraph from entity with two hops.

    e2 --p_2--> e1 --p_1--> entity

    """
    inverse_graph = Graph()

    # e1 --p2--> e2 --p1--> entity
    query = get_query_for_two_hops_inverse(entity, p_1, p_2, limit)
    inverse_graph += ask_dbpedia(query)

    return inverse_graph


def get_query_for_one_hop(subj: str, pred: str, obj: str, limit: int) -> str:
    """Get the query for extracting a subgraph with one hop.

    Get the CONSTRUCT-query, which constructs triples of the form
        <subj> <pred> <obj>.

    Parameters
    ----------
    subj : str
        The subject of the triples as DBpedia-resource or as variable.
    pred : str
        The predicate of the triples as DBpedia-property or as variable.
    obj : str
        The object of the triples as DBpedia-resource or as variable.
    limit : int
        Limit the number of triples in the graph (use -1 to not use any limit).

    Returns
    -------
    query : str
        The CONSTRUCT-SPARQL query.
    """
    if limit == -1:
        limit_str = ""
    else:
        limit_str = f"LIMIT {limit}"

    # FILTER(STRSTARTS(STR({pred}), "http://dbpedia.org/ontology/") || STRSTARTS(STR({pred}), "http://dbpedia.org/property/"))
    # FILTER(STR({pred}) != STR(<http://dbpedia.org/ontology/wikiPageWikiLink>))
    query = f"""CONSTRUCT WHERE {{
        {subj} {pred} {obj}
    }} {limit_str}"""

    return query


def get_query_for_two_hops(entity: str, p_1: str, p_2: str, limit: int) -> str:
    """Get the query for extracting a subgraph with two hops in forward direction.

    Get the CONSTRUCT-query, which constructs triples of the form
        <entity> <p_1> ?e1 and ?e1 <p_2> ?e2

    Parameters
    ----------
    entity : str
        Entity as DBpedia-resource or as variable.
    p_1 : str
        Relation in the first hop as DBpedia-property or as variable.
    p_2 : str
        Relation in the second hop as DBpedia-property or as variable.
    limit : int
        Limit the number of triples in the graph (use -1 to not use any limit).

    Returns
    -------
    query : str
        The CONSTRUCT-SPARQL-query.
    """
    if limit == -1:
        limit_str = ""
    else:
        limit_str = f"LIMIT {limit}"

    # FILTER(STRSTARTS(STR({p_1}), "http://dbpedia.org/ontology/") || STRSTARTS(STR({p_1}), "http://dbpedia.org/property/"))
    # FILTER(STRSTARTS(STR({p_2}), "http://dbpedia.org/ontology/") || STRSTARTS(STR({p_2}), "http://dbpedia.org/property/"))

    query = f"""CONSTRUCT WHERE {{
        {entity} {p_1} ?e2 .
        ?e2 {p_2} ?e3 .
    }} {limit_str}"""

    return query


def get_query_for_two_hops_inverse(entity: str, p_1: str, p_2: str, limit: int) -> str:
    """Get the query for extracting a subgraph with two hops in inverse direction.

    Get the CONSTRUCT-query, which constructs triples of the form
        ?e2 <p_2> ?e1 and ?e1 <p_1> <entity>

    Parameters
    ----------
    entity : str
        Entity as DBpedia-resource or as variable.
    p_1 : str
        Relation in the first hop as DBpedia-property or as variable.
    p_2 : str
        Relation in the second hop as DBpedia-property or as variable.
    limit : int
        Limit the number of triples in the graph (use -1 to not use any limit).

    Returns
    -------
    query : str
        The CONSTRUCT-SPARQL-query.
    """
    if limit == -1:
        limit_str = ""
    else:
        limit_str = f"LIMIT {limit}"

    # FILTER(STRSTARTS(STR({p_1}), "http://dbpedia.org/ontology/") || STRSTARTS(STR({p_1}), "http://dbpedia.org/property/"))
    # FILTER(STRSTARTS(STR({p_2}), "http://dbpedia.org/ontology/") || STRSTARTS(STR({p_2}), "http://dbpedia.org/property/"))

    query = f"""CONSTRUCT WHERE {{
        ?e1 {p_1} {entity} .
        ?e2 {p_2} ?e1 .
    }} {limit_str}"""

    return query


def get_subgraphs_based_on_relations(
    entity: URIRef, relations: List[URIRef]
) -> Tuple[Graph, Graph]:
    """Additional function to get subgraphs for an entity based on relations.

    Given an entity and relations, extract a subgraph with the entity as central node
    and all outgoing edges with the specified relations and a subgraph with the entity
    as central node and all ingoing edges with the specified relations.

    Parameters
    ----------
    entity : URIRef
        Entity, which is used as central node, as URIRef
    relations : list
        List of relations as URIRefs.

    Returns
    -------
    regular_graph : Graph
        Subgraph with entity as central node and all relations as outgoing edges.
    inverse_graph : Graph
        Subgraph with entity as central node and all relations as ingoing edges.
    """
    relation_str = ""

    for relation in relations:
        relation_str += relation.n3() + ","

    query_regular = f"""CONSTRUCT WHERE {{
        {entity.n3()} ?p ?o
        FILTER( ?p IN ({relation_str[:-1]}) )
    }}
    """

    query_inverse = f"""CONSTRUCT WHERE {{
        ?s ?p {entity.n3()}
        FILTER( ?p IN ({relation_str[:-1]}) )
    }}
    """

    regular_graph = Graph()
    inverse_graph = Graph()

    sparql = SPARQLWrapper("http://dbpedia.org/sparql/")
    sparql.setQuery(query_regular)
    regular_graph += sparql.query().convert()

    sparql.setQuery(query_inverse)
    inverse_graph += sparql.query().convert()

    return regular_graph, inverse_graph


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("question", type=str, help="Natural language question")
    parser.add_argument(
        "-j",
        "--jumps",
        type=int,
        default=1,
        choices=[1, 2],
        help="Number of hops/jumps (in [1, 2])",
    )
    parser.add_argument(
        "-p",
        "--position",
        type=int,
        default=1,
        choices=[1, 2],
        help="Position of relations",
    )
    parser.add_argument(
        "-l",
        "--limit",
        type=int,
        default=10,
        help="Limit the number of triples (use -1 to show all triples)",
    )
    parser.add_argument(
        "-i",
        "--ignore",
        default=False,
        action="store_true",
        help="Get subgraph without any restrictions to relations",
    )

    args = parser.parse_args()

    subgraphs = entity_relation_hops(
        args.question,
        hops=args.jumps,
        relation_pos=args.position,
        limit=args.limit,
        ignore=args.ignore,
    )

    print("-" * 30)

    if len(subgraphs) > 0:
        subgraph = subgraphs[0][1] + subgraphs[0][2]

        for s, p, o in subgraph:
            print(s, p, o)

        print("Found triples:", len(subgraph))
    else:
        print("No entities found. Hence no subgraph found.")
    print("-" * 30)
