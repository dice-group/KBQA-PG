"""Util functions for the summarizers."""
import json
from json.decoder import JSONDecodeError
from typing import Any
from typing import Dict
from typing import List
from typing import Tuple

from rdflib import URIRef
import requests
from SPARQLWrapper import JSON
from SPARQLWrapper import SPARQLWrapper


def entity_recognition_dbspotlight(
    question: str, confidence: float = 0.8
) -> List[URIRef]:
    """Entity recognition using DB-Spotlight.

    Parameters
    ----------
    question : str
        Natural language question.
    confidence : float, optional
        Confidence of the recognized entity (default: 0.8).

    Returns
    -------
    entities : list
        List of recognized entities as URIRefs.
    """
    endpoint = "https://api.dbpedia-spotlight.org/en/annotate"

    try:
        response = requests.post(
            endpoint,
            headers={"Accept": "application/json"},
            data={"text": question, "confidence": confidence},
        ).json()
    except JSONDecodeError:
        print("It was not possible to parse the answer.")

        return list()

    if "Resources" not in response:
        return list()

    entities = list()

    for resource in response["Resources"]:
        entities.append(URIRef(resource["@URI"]))

    return entities


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

    try:
        response = requests.post(
            endpoint,
            headers={"Content-Type": "application/json"},
            data=json.dumps({"text": question}),
        ).json()
    except JSONDecodeError:
        print("It was not possible to parse the response.")

        return list(), list()

    dbpedia_entities = response["entities_dbpedia"]
    dbpedia_relations = response["relations_dbpedia"]

    # print("Entities:", dbpedia_entities)
    # print("Relations:", dbpedia_relations)

    entities = []
    relations = []

    for entity in dbpedia_entities:
        if len(entity) > 1:
            resource = URIRef(entity[0])

            entities.append(resource)

    for relation in dbpedia_relations:
        if len(relation) > 1:
            prop = URIRef(relation[0])

            relations.append(prop)

    return entities, relations


def build_sparql_query_for_one_hop_predicates(entity: str, predicates: List) -> str:
    """Build a sparql query for one hop triples.

    Parameters
    ----------
    entity : str
        URI for a DBpedia resource.
    predicates : list
        List of predicates with one only one predicate.

    Returns
    -------
    str
        The formated SPARQL-query.
    """
    predicate_str = ""

    for predicate in predicates:
        predicate_str += predicate[0].n3() + ","

    query = f"""CONSTRUCT WHERE {{
        <{entity}> ?p ?o .
        FILTER( ?p IN ({predicate_str[:-1]}) )
    }}
    """

    return query


def build_sparql_query_for_two_hop_predicates(entity: str, predicates: List) -> str:
    """Build a sparql query for two hop triples.

    Parameters
    ----------
    entity : str
        URI for a DBpedia resource.
    predicates : list
        List of predicates with one only one predicate.

    Returns
    -------
    str
        The formated SPARQL-query.
    """
    const_str = ""
    where_str = ""

    for num, predicate in enumerate(predicates):
        cur_str = f"<{entity}> <{predicate[0][0]}> ?o{num} . ?o{num} <{predicate[0][1]}> ?o{num}1 ."

        const_str += f"{cur_str} "
        where_str += f"{{ {cur_str} }} UNION "

    query = f"CONSTRUCT {{ {const_str} }} WHERE {{ {where_str[:-6]} }}"

    return query


def query_dbpedia(query: str, ret_format: str = JSON) -> Dict[str, Any]:
    """Query DBpedia with a POST request.

    Parameters
    ----------
    query : str
        SPARQL-query.
    ret_format : str
        Return format from the SPARQL Wrapper.

    Returns
    -------
    dict
        Response from DBpedia.
    """
    endpoint = "https://dbpedia.org/sparql/"

    sparql = SPARQLWrapper(endpoint)
    sparql.setMethod("POST")
    sparql.setQuery(query)
    sparql.setReturnFormat(ret_format)

    answer = sparql.query().convert()

    return answer
