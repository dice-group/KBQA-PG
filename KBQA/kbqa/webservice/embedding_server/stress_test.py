"""Stress test for the embedding server by consecutively querying >1000 URIs."""

import requests

ENTITY_EMBEDDING_PATH = "/media/jmenzel/INTENSO1/Embeddings/dbp21-03_complex/embeddings/embedding_query/entity_embeddings_dbp21-03_complex.tsv"


def stress_test(path: str, stop_after: int = 1000, status_every: int = 100) -> None:
    """
    Query single URIs from givem entity file.

    :param path: path to entity file
    :param stop_after: total number of entities to query
    :param status_every: number of entities after which to give a progress indication
    """
    with open(
        path,
        "r",
        newline="",
        encoding="utf-8",
    ) as tsv_file:
        for i, line in enumerate(tsv_file):
            line_split = line.split("\t", maxsplit=1)
            uri = line_split[0]
            uri_dict = {"entities": [uri], "relations": []}
            resp = requests.post("http://127.0.0.1/embedding_query/", json=uri_dict)

            recv_entity = resp.json()["entity_embeddings"][0]
            if line != recv_entity:
                print("Found mismatch:")
                print(f"Expected: {line}")
                print(f"Received: {recv_entity}")

            if i % status_every == 0:
                print(f"Gone throught {i}/{stop_after} Embeddings.")
            if i == stop_after:
                break
    print(f"Passed single request stress test after testing {stop_after} entities")


def stress_test_batch(
    path: str, batch_size: int = 50, stop_after: int = 1000, status_every: int = 100
) -> None:
    """
    Query batches of URIs from given entity file.

    :param path: path to entity file
    :param batch_size: number of entities batched together for a single query
    :param stop_after: total number of entities to query
    :param status_every: number of entities after which to give a progress indication
    """
    with open(
        path,
        "r",
        newline="",
        encoding="utf-8",
    ) as tsv_file:
        status_every = 100
        batch: list = []
        expected_embeddings: list = []
        for i, line in enumerate(tsv_file):

            line_split = line.split("\t", maxsplit=1)
            uri = line_split[0]

            if i % batch_size == 0:
                uri_dict = {"entities": batch, "relations": []}
                resp = requests.post("http://127.0.0.1/embedding_query/", json=uri_dict)

                for exp, recv in zip(
                    expected_embeddings, resp.json()["entity_embeddings"]
                ):
                    if exp != recv:
                        print("Found mismatch:")
                        print(f"Expected: {exp}")
                        print(f"Received: {recv}")

                batch = []
                expected_embeddings = []

            batch.append(uri)
            expected_embeddings.append(line)

            if i % status_every == 0:
                print(f"Gone throught {i}/{stop_after} Embeddings.")
            if i == stop_after:
                break
    print(f"Passed batch({batch_size}) after testing {stop_after} entities")


# stress_test(ENTITY_EMBEDDING_PATH)
if __name__ == "__main__":
    stress_test(ENTITY_EMBEDDING_PATH, stop_after=1000)
    stress_test_batch(ENTITY_EMBEDDING_PATH, stop_after=1000)
