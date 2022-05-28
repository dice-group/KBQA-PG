"""Script to check how many questions from a QUALD dataset get answered by the DBpedia endpoint."""

from SPARQLWrapper import JSON
from SPARQLWrapper import SPARQLWrapper
from SPARQLWrapper.SPARQLExceptions import SPARQLWrapperException

from .dataset import Dataset

dataset = Dataset()
dataset.load_qald_dataset("../../datasets/qald-9-test-multilingual.json")

answered = 0
unanswered = 0
errored = 0

for question in dataset.questions:
    sparql = SPARQLWrapper("http://dbpedia.org/sparql/")
    sparql.setQuery(question.sparql)
    sparql.setReturnFormat(JSON)

    try:
        result = sparql.query().convert()
    except SPARQLWrapperException as exception:
        errored += 1
        print("(#) SPARQLWrapperException", exception)
        # print("")
        continue

    if (
        "results" in dict(result)
        and len(result["results"]["bindings"]) > 0
        or "boolean" in dict(result)
    ):
        answered += 1
        # print("(+) " + question.text)
    else:
        unanswered += 1
        print("(-) " + question.text + "  ")
        print(question.sparql)

    # print(result)
    # print("")

print(f"total\t\t{len(dataset.questions)}  ")
print(f"answered\t{answered}  ")
print(f"unanswered\t{unanswered}  ")
print(f"errored\t\t{errored}  ")
