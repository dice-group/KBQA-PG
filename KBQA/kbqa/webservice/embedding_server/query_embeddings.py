"""Module for converting triples from QTQ dataset to their corresponding Embeddings."""
import json
from typing import Dict
from typing import List
from typing import Tuple

import numpy as np
import requests


def load_qtq_dataset(dataset_path: str) -> Dict:
    """
    Load qtq dataset from given path.

    :param dataset_path: Path to QTQ dataset
    :return: The dataset in QTQ format
    """
    with open(dataset_path, "r", encoding="utf-8") as file_handle:
        qtq_data = json.load(file_handle)

    return qtq_data


def preprocess_uri(uri: str) -> str:
    """
    Preprocess URI from triples into valid URI for querying.

    Removes surrounding "<", ">",
    In case of a typed string returns the type,
    In case of a lang string returns the w3 langString property
    In case of "dbp" and "a" returns the resolved name

    :param uri: A valid URI
    :return: preprocessed URI
    :raises ValueError: In case the URI is ill-formed
    """
    if uri.startswith("<") and uri.endswith(">"):
        return uri[1:-1]
    elif "^^" in uri:
        uri = uri.split("^^")[0]
        return uri[1:-1]
    elif "@" in uri:
        return "http://www.w3.org/1999/02/22-rdf-syntax-ns#langString"
    elif "dbp" in uri:
        return "http://dbpedia.org/property/"
    elif uri == "a":
        return "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"
    else:
        raise ValueError(f"Cannot extract URI for {uri}")


def extract_uris_from_triples(triples: list) -> Tuple[List, List]:
    """
    Extract all entities and relations from triples for a single question.

    :param triples: Triples from a single question
    :return: List of entity and relation URIs that the triples contained
    """
    entities = []
    relations = []
    for triple in triples:
        triple_uris = triple.split(" ", maxsplit=2)
        sub, pred, obj = triple_uris
        try:
            sub = preprocess_uri(sub)
            pred = preprocess_uri(pred)
            obj = preprocess_uri(obj)
        except ValueError:
            print(f"[ERROR] Triple {triple} is could not be preprocessed. Skipping!")
        else:
            entities.append(sub)
            relations.append(pred)
            entities.append(obj)

    return entities, relations


def gather_uris_from_dataset(dataset: dict) -> Tuple[List, List]:
    """
    Collect unique set of URIs found in QTQ dataset triples.

    :param dataset: QTQ dataset
    :return: List containing all unique URIs in given QTQ dataset
    """
    entities = []
    relations = []
    for question in dataset["questions"]:
        ents, rels = extract_uris_from_triples(question["triples"])
        entities.extend(ents)
        entities = list(set(entities))
        relations.extend(rels)
        relations = list(set(relations))
    return entities, relations


def execute_query(
    uri_dict: dict, server_address: str = "http://kbqa-pg.cs.upb.de/embedding_query/"
) -> Dict:
    """
    Execute query for relations and entities to embedding server.

    :param uri_dict: dict containing list of entities and relations for querying
    :param server_address: address of the embedding server
    :return: server response
    """
    resp = requests.post(server_address, json=uri_dict)
    return resp.json()


def post_process_entitiy_response(response_dict: dict) -> Dict:
    """
    Post-process server response for entity embeddings.

    Converts the received csv rows into numpy arrays.

    :param response_dict: server response
    :return: dict containg the embeddings as numpy arrays accessible via the URIs
    """
    entity_embeddings = {}
    embeddings = response_dict["entity_embeddings"]
    for embedding in embeddings:
        if embedding != "":
            embedding = embedding.replace("\n", "")
            embedding_split = embedding.split("\t")
            uri = embedding_split[0]
            if uri.startswith("http"):
                uri = uri.split("/", maxsplit=2)[2]
            embedding = np.array(embedding_split[1:]).astype(np.float64)
            entity_embeddings[uri] = embedding
    return entity_embeddings


def post_process_relation_response(response_dict: dict) -> Dict:
    """
    Post-process server response for relation embeddings.

    Converts the received dict entries into numpy arrays.

    :param response_dict: server response
    :return: dict containg the lhs/rhs embeddings as numpy arrays accessible via the URIs
    """
    relation_embeddings: dict = {}
    embeddings = response_dict["relation_embeddings"]
    for embedding in embeddings:
        if embedding != {}:
            uri = embedding["uri"]
            if uri.startswith("http"):
                uri = uri.split("/", maxsplit=2)[2]
            lhs_imag = np.array(embedding["lhs"]["imag"].split("\t")).astype(np.float64)
            lhs_real = np.array(embedding["lhs"]["real"].split("\t")).astype(np.float64)
            rhs_imag = np.array(embedding["rhs"]["imag"].split("\t")).astype(np.float64)
            rhs_real = np.array(embedding["rhs"]["real"].split("\t")).astype(np.float64)
            relation_embeddings[uri] = {}
            relation_embeddings[uri]["lhs"] = {}
            relation_embeddings[uri]["rhs"] = {}
            relation_embeddings[uri]["lhs"]["imag"] = lhs_imag
            relation_embeddings[uri]["lhs"]["real"] = lhs_real
            relation_embeddings[uri]["rhs"]["imag"] = rhs_imag
            relation_embeddings[uri]["rhs"]["real"] = rhs_real
    return relation_embeddings


def query_entities(entities: list) -> Dict:
    """
    Query embeddings for unique list of entites and store in dict.

    :param entities: list of unique URIs.
    :return: Dict containing the embeddings accessible via the URIs
    """
    batch_uris = []
    entity_embeddings = {}
    for i, uri in enumerate(entities):
        batch_uris.append(uri)
        if len(batch_uris) == 100:
            uri_dict = {"entities": batch_uris, "relations": []}
            response_dict = execute_query(
                uri_dict, server_address="http://127.0.0.1/embedding_query/"
            )
            new_embeddings = post_process_entitiy_response(response_dict)
            entity_embeddings.update(new_embeddings)
            batch_uris.clear()
            print(f"Queried {i}/{len(entities)} entities")
    # Query remaining batch
    uri_dict = {"entities": batch_uris, "relations": []}
    response_dict = execute_query(
        uri_dict, server_address="http://127.0.0.1/embedding_query/"
    )
    new_embeddings = post_process_entitiy_response(response_dict)
    entity_embeddings.update(new_embeddings)
    return entity_embeddings


def query_relations(relations: list) -> Dict:
    """
    Query embeddings for unique list of relations and store in dict.

    :param relations: list of unique URIs.
    :return: Dict containing the embeddings accessible via the URIs
    """
    batch_uris = []
    entity_embeddings = {}
    for i, uri in enumerate(relations):
        batch_uris.append(uri)
        if len(batch_uris) == 100:
            uri_dict = {"entities": [], "relations": batch_uris}
            response_dict = execute_query(
                uri_dict, server_address="http://127.0.0.1/embedding_query/"
            )
            new_embeddings = post_process_relation_response(response_dict)
            entity_embeddings.update(new_embeddings)

            batch_uris.clear()
            print(f"Queried {i}/{len(relations)} entities")
    # Query remaining batch
    uri_dict = uri_dict = {"entities": [], "relations": batch_uris}
    response_dict = execute_query(
        uri_dict, server_address="http://127.0.0.1/embedding_query/"
    )
    new_embeddings = post_process_relation_response(response_dict)
    entity_embeddings.update(new_embeddings)
    return entity_embeddings


def check_coverage(
    entities: list, relations: list, entity_embeddings: dict, relation_embeddings: dict
) -> None:
    """
    Check coverage of queried entities and relations.

    :param entities: list of entity URIs
    :param relations: list of relation URIs
    :param entity_embeddings: dict with embeddings corresponding to entities list
    :param relation_embeddings: dict with embeddings corresponding to relations list
    """
    entites_covered = 0
    for entity in entities:
        if entity.startswith("http"):
            entity = entity.split("/", maxsplit=2)[2]
        if entity in entity_embeddings:
            entites_covered += 1

    print(
        f"Entity Coverage: {entites_covered}/{len(entities)} ({entites_covered/len(entities):1.2f}%)"
    )

    relations_covered = 0
    for relation in relations:
        if relation.startswith("http"):
            relation = relation.split("/", maxsplit=2)[2]
        if relation in relation_embeddings:
            relations_covered += 1

    print(
        f"Relation Coverage: {relations_covered}/{len(relations)} ({relations_covered/len(relations):1.2f}%)"
    )


def main(dataset_path: str) -> None:
    """
    Query and store all embeddings for URIs in QTQ dataset.

    :param dataset_path: Path to QTQ dataset
    """
    qtq_dataset = load_qtq_dataset(dataset_path)

    entities, relations = gather_uris_from_dataset(qtq_dataset)
    print(f"Found {len(entities)} entities.")
    print(f"Found {len(relations)} relations.")
    entity_embeddings = query_entities(entities)
    relation_embeddings = query_relations(relations)
    check_coverage(entities, relations, entity_embeddings, relation_embeddings)


if __name__ == "__main__":
    main("../../../datasets/qtq-8-train-multilingual.json")
