"""Test embedding webserver with entities from QALD dataset."""
import json

import requests

if __name__ == "__main__":
    with open(
        "../../TEAM1/Data/qald-9-test-multilingual.json", "r", encoding="UTF-8"
    ) as qald8_file:
        data = json.load(qald8_file)
    uris = []
    for question in data["questions"]:
        if "bindings" in question["answers"][0]["results"]:
            for answer in question["answers"][0]["results"]["bindings"]:
                if "uri" in answer:
                    uris.append(answer["uri"]["value"])
    embedding_dict = {"uris": uris}
    print(f"#uris: {len(uris)}")
    # print(embedding_dict)
    r = requests.post("http://localhost:24805/embedding_query/", json=embedding_dict)
    results = r.json()
    valid_embeddings = sum(1 for embedding in results["embeddings"] if embedding != "")
    failed_embeddings = [
        uris[i]
        for i in range(len(results["embeddings"]))
        if results["embeddings"][i] == ""
    ]
    print(f"#valid: {valid_embeddings} ({valid_embeddings/len(uris) * 100.0:.1f}%)")
    print("Failed for")
    print("\n".join(failed_embeddings))

    print("Testing post without json")
    r = requests.post("http://localhost:24805/embedding_query/")
    print(r.json())
    print("Testing bad json 1")
    r = requests.post("http://localhost:24805/embedding_query/", json={"uri": ["uri"]})
    print(r.json())
    print("Testing bad json 2")
    r = requests.post("http://localhost:24805/embedding_query/", json={"uri": 1})
    print(r.json())
    print("Testing bad json 3")
    r = requests.post(
        "http://localhost:24805/embedding_query/", json={"uri": ["uri", 4]}
    )
    print(r.json())
