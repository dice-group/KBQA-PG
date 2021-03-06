"""Util functions for the summarizers."""
import json
from json.decoder import JSONDecodeError
from typing import Any
from typing import Dict
from typing import List
from typing import Tuple
from typing import Union

from rdflib import URIRef
import requests
from SPARQLWrapper import JSON
from SPARQLWrapper import SPARQLWrapper


def query_dbspotlight(question: str, confidence: float = 0.5) -> Dict[str, Any]:
    """Query the endpoint of DBspotlight for entity recognition.

    Parameters
    ----------
    question : str
        Natural language question.
    confidence : float, optional
        Lower bound for the confidence of recognized entities (default: 0.5).

    Returns
    -------
    response : dict
        Response of the DBspotlight endpoint without any processing
        as JSON dict.
    """
    endpoint = "https://api.dbpedia-spotlight.org/en/annotate/"

    try:
        response = requests.post(
            endpoint,
            headers={"Accept": "application/json"},
            data={"text": question, "confidence": confidence},
        ).json()
    except JSONDecodeError:
        print("It was not possible to parse the answer.")

        return dict()

    return response


def query_falcon(question: str) -> Dict[str, Any]:
    """Query the endpoint of Falcon 2.0 for entity recognition.

    Parameters
    ----------
    question : str
        Natural language question.

    Returns
    -------
    response : dict
        Response of the Falcon 2.0 endpoint without any processing
        as JSON dict.
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

        return dict()
    return response


def entity_recognition_dbspotlight(
    question: str, confidence: float = 0.5
) -> List[URIRef]:
    """Entity recognition using DB-Spotlight.

    Parameters
    ----------
    question : str
        Natural language question.
    confidence : float, optional
        Lower bound for the confidence of recognized entities (default: 0.5).

    Returns
    -------
    entities : list
        List of recognized entities as URIRefs.
    """
    response = query_dbspotlight(question, confidence)

    if "Resources" not in response:
        return list()

    entities = list()

    for resource in response["Resources"]:
        entities.append(URIRef(resource["@URI"]))

    return entities


def entity_recognition_dbspotlight_confidence(
    question: str, confidence: float = 0.5
) -> List[Tuple[URIRef, float]]:
    """Entity recognition using DBspotlight.

    Compared to the function entity_recognition_dbspotlight this
    function will return the recognized entities and their
    confidence score computed by DBspotlight.

    Parameters
    ----------
    question : str
        Natural language question.
    confidence : float, optional
        Lower bound for the confidence of recognized entities (default: 0.5).

    Returns
    -------
    entities : list
        List of tuples of the form (entity, confidence), where entity is
        a recognized entity as URIRef and confidence is the confidence
        score computed by DBspotlight.
    """
    response = query_dbspotlight(question, confidence)

    if "Resources" not in response:
        return list()

    entities = list()

    for resource in response["Resources"]:
        entity = (URIRef(resource["@URI"]), float(resource["@similarityScore"]))

        entities.append(entity)

    return entities


def query_tagme(question: str) -> Dict[str, Any]:
    """Query the endpoint of the TagMe API.

    Parameters
    ----------
    question : str
        Natural language question.

    Returns
    -------
    response : dict
        Response of the TagMe endpoint without any processing
        as JSON dict.
    """
    endpoint = "https://tagme.d4science.org/tagme/tag"

    data = {
        "text": question,
        "gcube-token": "ad53a3bc-3cff-4350-b766-aced87f26cbd-843339462",
        "include_categories": "false",
    }

    response = requests.post(endpoint, data=data)

    return response.json()


def entity_recognition_tagme(
    question: str, conf: float = 0.5
) -> List[Tuple[URIRef, float]]:
    """Entity recognition using the TagMe API.

    Parameters
    ----------
    question : str
        Natural language question.
    conf : float, optional
        Lower bound for the confidence score. Exclude all entities with a lower
        confidence score.

    Returns
    -------
    list
        List containing objects of the form (entity, confidence), where entity
        is the URIRef of a recognized entity and confidence the corresponding
        confidence score.
    """
    response = query_tagme(question)
    annotations = response["annotations"]

    entities = list()

    for annotation in annotations:
        ann_id = annotation["id"]
        confidence = float(annotation["rho"])

        if confidence >= conf:
            entity = URIRef(get_uri_for_wiki_page_id(ann_id))
            entities.append((entity, confidence))

    return entities


def get_uri_for_wiki_page_id(wiki_page_id: int) -> Union[str, None]:
    """Query DBpedia for the URI corresponding to the wikiPageID wiki_page_id.

    Parameters
    ----------
    wiki_page_id : int
        The wikiPageID of some DBpedia page.

    Returns
    -------
    str or None
        The corresponding URI. None, if no URI was found.
    """
    uri = None
    query = f"""SELECT ?uri WHERE {{
                ?uri dbo:wikiPageID "{wiki_page_id}"^^xsd:integer .
                }}"""
    answer = query_dbpedia(query)
    bindings = answer["results"]["bindings"]
    for binding in bindings:
        uri = binding["uri"]["value"]
    return uri


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
    response = query_falcon(question=question)
    if "entities_dbpedia" not in response or "relations_dbpedia" not in response:
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
