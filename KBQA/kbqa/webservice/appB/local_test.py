"""Local test module to simulate the behaviour of approach B."""
import argparse

import requests


parser = argparse.ArgumentParser(description="Test the functionality of approach B")
parser.add_argument(
    "question",
    type=str,
    help="Natural language question, which might be asked by the enduser",
)


if __name__ == "__main__":
    args = parser.parse_args()

    query = args.question

    r = requests.post("http://localhost:24802/appB/", {"query": query})
    print(r.text, "\n")