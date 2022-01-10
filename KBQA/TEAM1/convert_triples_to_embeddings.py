"""Module for converting triples from QTQ dataset to their corresponding Embeddings."""
import json

import pandas as pd
import requests


def load_qtq_dataset(dataset_path: str) -> dict:
    """
    Load qtq dataset from given path.

    :param dataset_path: Path to QTQ dataset
    :return: The dataset in QTQ format
    """
    with open(dataset_path, "r", encoding="utf-8") as file_handle:
        qtq_data = json.load(file_handle)

    return qtq_data


def extract_uris_from_triples(triples: list) -> list:
    """
    Extract all uris from triples for a single question.

    :param triples: Triples from a single question
    :return: List of URIs that the triples contained
    """
    uris = []
    for triple in triples:
        triple_uris = triple.split(" ", maxsplit=2)
        # print(triple_uris)
        for uri in triple_uris:
            if uri.startswith("<") and uri.endswith(">"):
                uris.append(uri[1:-1])
            elif "^^" in uri:
                uri = uri.split("^^")[0]
                uris.append(uri[1:-1])
            elif "@" in uri:
                uris.append("http://www.w3.org/1999/02/22-rdf-syntax-ns#langString")
            elif "dbp" in uri:
                uris.append("http://dbpedia.org/property/")
            elif uri == "a":
                uris.append("http://www.w3.org/1999/02/22-rdf-syntax-ns#type")
            else:
                print(f"Cannot extract URI for {uri}")
                print(f"and triple: {triple}")
    return uris


def gather_uris_from_dataset(dataset: dict) -> list:
    """
    Collect unique set of URIs found in QTQ dataset triples.

    :param dataset: QTQ dataset
    :return: List containing all unique URIs in given QTQ dataset
    """
    uris = []
    for question in dataset["questions"]:
        new_uris = extract_uris_from_triples(question["triples"])
        uris.extend(new_uris)
        uris = list(set(uris))
    return uris


def query_embeddings(uris: list) -> pd.DataFrame:
    """
    Query embeddings for unique list of URIs and store in pandas Dataframe.

    :param uris: list of unique URIs.
    :return: pandas Dataframe containing the URIs with heir corresponding Embedding
    """
    batch_uris = []
    column_names = ["uri"] + [str(i) for i in range(100)]
    cnt = 0
    embedding_df = pd.DataFrame(columns=column_names)
    for i, uri in enumerate(uris):
        batch_uris.append(uri)
        if len(batch_uris) == 100:
            uri_dict = {"uris": batch_uris}
            resp = requests.post(
                "http://kbqa-pg.cs.upb.de/embedding_query/", json=uri_dict
            )
            embeddings = resp.json()["embeddings"]
            for embedding in embeddings:
                if embedding != "":
                    embedding = embedding.replace("\n", "")
                    embedding_split = embedding.split("\t")
                    embedding_df.loc[cnt] = embedding_split
                    cnt += 1
            batch_uris.clear()
            print(i)
    return embedding_df


def main(dataset_path: str) -> None:
    """
    Query and store all embeddings for URIs in QTQ dataset.

    :param dataset_path: Path to QTQ dataset
    """
    qtq_dataset = load_qtq_dataset(dataset_path)

    unique_uris = gather_uris_from_dataset(qtq_dataset)
    embedding_df = query_embeddings(unique_uris)

    with open("df.out", "w", encoding="UTF-8") as outfile:
        embedding_df.to_csv(outfile, sep="\t")


if __name__ == "__main__":
    main("Data/qtq-9-train-multilingual.json")
