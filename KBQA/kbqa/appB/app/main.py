from app.qald_builder import qald_builder
from app.qald_builder import qald_builder_empty_answer
from SPARQLWrapper import JSON
from SPARQLWrapper import SPARQLWrapper


def main(query, lang="en"):
    """
    Process the query, which contains the question asked by an user
    """

    # ===========================================
    # TODO add here the logic for approach B and
    # return the answer in the QALD format
    # ===========================================

    # -------------------- Example ----------------------
    # Example in order to check, whether the connection works

    answer_qald = example(query, lang)

    return answer_qald


def example(query, lang):
    # QALD-test-8, id 46
    # What other books have been written by the author of The Fault in Our Stars?
    sparql_query = "PREFIX dbo: <http://dbpedia.org/ontology/> SELECT ?books WHERE { ?books dbo:author <http://dbpedia.org/resource/John_Green_(author)> }"

    sparql = SPARQLWrapper("http://dbpedia.org/sparql/")
    sparql.setReturnFormat(JSON)
    sparql.setQuery(sparql_query)
    answer = sparql.query().convert()

    if answer == "":
        qald_answer = qald_builder_empty_answer(sparql_query, query, lang)
    else:
        qald_answer = qald_builder(sparql_query, answer, query, lang)

    return qald_answer
