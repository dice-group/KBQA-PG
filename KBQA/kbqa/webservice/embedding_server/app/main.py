"""Main module for extracting embeddings."""
import os

from app.embeddings import EntityHashTable
from app.embeddings import RelationEmbeddings


def main(
    hash_table: EntityHashTable,
    relation_embeddings: RelationEmbeddings,
    entities: list,
    relations: list,
) -> dict:
    """
    Get embeddings for all requested URIs.

    For entity embeddings the embedding is returned.
    For relations both the lhs and rhs embedding split into real and imaginary part is returned.
    If an entity embedding is not found an empty string is returned.
    If a relation embedding is not found an empty dict is returned

    :param hash_table: hashtable for entity embedding file
    :param relation_embeddings: class storing the relation embedding information for querying
    :param entities: list of entitiy URIs
    :param relations: list of relation URIs
    :return: list of embeddings for URIs
    """
    embedding_dict: dict = {"entity_embeddings": [], "relation_embeddings": []}

    # Query entity embeddings
    with open(
        os.path.join(hash_table.root_path, hash_table.entity_file),
        newline="",
        encoding="utf-8",
    ) as tsv_file:
        for uri in entities:
            if uri.startswith("http"):
                uri = uri.split("/", maxsplit=2)[2]
            seek_positions = hash_table.lookup(uri)
            for seek_pos in seek_positions:
                tsv_file.seek(seek_pos)
                line = tsv_file.readline()
                comp_uri = line.split(sep="\t", maxsplit=1)[0]
                comp_uri = comp_uri.split("/", maxsplit=2)[2]
                if uri == comp_uri:
                    embedding_dict["entity_embeddings"].append(line)
                    break
            else:
                embedding_dict["entity_embeddings"].append("")

    # Query relation embeddings
    for uri in relations:
        if uri.startswith("http"):
            uri = uri.split("/", maxsplit=2)[2]
        embedding = relation_embeddings.lookup(uri)
        embedding_dict["relation_embeddings"].append(embedding)

    return embedding_dict
