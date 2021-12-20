"""Module for executing SPARQL queries to DBPedia."""
import ssl

from SPARQLWrapper import JSON
from SPARQLWrapper import SPARQLWrapper


# pass the query in the function
# return results as dictionary
def get_answer(query: str) -> dict:
    """
    Get results from a "SELECT WHERE" SPARQL query.

    :param query: The SPARQL query
    :return: Results for the SPARQL query
    """
    # to avoid [SSL: CERTIFICATE_VERIFY_FAILED] error
    ssl._create_default_https_context = ssl._create_unverified_context
    # print("get query: ")
    # print(query)
    sparql = SPARQLWrapper("http://dbpedia.org/sparql")
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    # sparql.query() returns HTML response
    # convert() converts response to dictionary
    answers = sparql.query().convert()
    # print(answers)
    # print("results: ")
    # print_result(answers)
    return answers


# print results for query as:
# var1: value, var2: value,...
# var1: value, var2: value,...
def print_result(results: dict) -> None:
    """
    Print SPARQL query results in a human readable form.

    :param results: The results from get_answer
    """
    query_vars = results["head"]["vars"]
    for result in results["results"]["bindings"]:
        for var in query_vars:
            type_value = result.get(var, None)
            if type_value:
                print(var + ": " + type_value["value"], end=", ")
        print("")
