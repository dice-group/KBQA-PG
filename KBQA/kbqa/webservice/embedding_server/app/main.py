"""Main module for extracting embeddings."""
import os

from app.embedding_hashtable import EmbeddingHashtable


def main(hash_table: EmbeddingHashtable, uris: list) -> dict:
    """
    Get embeddings for all requested URIs.

    If an embedding is not found an empty string is return for that embedding

    :param hash_table: hashtable for entity embedding file
    :param uris: list of URIs
    :return: list of embeddings for URIs
    """
    embedding_dict: dict = {"embeddings": []}
    with open(
        os.path.join(hash_table.root_path, hash_table.entity_file),
        "r",
        newline="",
        encoding="utf-8",
    ) as tsv_file:
        for uri in uris:
            print(uri)
            if uri.startswith("http"):
                uri = uri.split("/", maxsplit=2)[2]
            seek_positions = hash_table.lookup(uri)
            for seek_pos in seek_positions:
                tsv_file.seek(seek_pos)
                line = tsv_file.readline()
                comp_uri = line.split(sep="\t", maxsplit=1)[0]
                comp_uri = comp_uri.split("/", maxsplit=2)[2]
                if uri == comp_uri:
                    embedding_dict["embeddings"].append(line)
                    break
            else:
                embedding_dict["embeddings"].append("")
    return embedding_dict
