"""Main module for the application logic of approach B."""

from typing import Dict
from typing import Tuple

from app.t5.sparql_predictor import process_question
from app.qald_builder import qald_builder
from app.qald_builder import qald_builder_empty_answer
from SPARQLWrapper import JSON
from SPARQLWrapper import SPARQLWrapper, SPARQLWrapperException


def main(query: str, lang: str = "en") -> str:
    """Start main method of the application logic for approach A.

    Process the query, which contains the question asked by an enduser and an
    optional language tag.

    Parameters
    ----------
    query : str
        Natural language question asked by an enduser.
    lang : str, optional
        Language tag (default is "en", i.e. an english question is asked).

    Returns
    -------
    answer_qald : dict
        Answers for the given question formatted in the QALD-format.
    """
    answer, sparql_query = get_answer(query)
    if sparql_query == "":
        answer_qald = qald_builder_empty_answer(sparql_query, query, lang)
    else:
        answer_qald = qald_builder(sparql_query, answer, query, lang)

    return answer_qald


def get_answer(question: str) -> Tuple[Dict, str]:
    """Interprete an asked question using the Neural SPARQL Machine.
    Parameters
    ----------
    question : str
        Natural language question asked by an enduser.
    Returns
    -------
    answer : dict
        Bindings of the variables from the generated SPARQL-query, which contain
        the answers for the given question.
    sparql_query : str
        Generated SPARQL-query by the Neural SPARQL Machine.
    """

    sparql_query = process_question(question)

    print("Predicted SPARQL-Query:", sparql_query)

    try:
        sparql = SPARQLWrapper("http://dbpedia.org/sparql/")
        sparql.setReturnFormat(JSON)
        sparql.setQuery(sparql_query)
        answer = sparql.query().convert()
    except SPARQLWrapperException as exception:
        # Unfortunately, the NSPM does not always return a valid SPARQL query.
        print("SPARQLWrapperException", exception)

        return {}, ""

    return answer, sparql_query



def example(question: str, lang: str) -> str:
    """Use this function as an example to return an answer, when approach B is chosen.

    Parameters
    ----------
    question : str
        Natural language question asked by an enduser.
    lang : str, optional
        Language tag (default is "en", i.e. an english question is asked).

    Returns
    -------
    answer_qald : str
        Answers for the given question formatted in the QALD-format.
    """
    # QALD-test-8, id 46
    # What other books have been written by the author of The Fault in Our Stars?
    sparql_query = "PREFIX dbo: <http://dbpedia.org/ontology/> SELECT ?books WHERE { ?books dbo:author <http://dbpedia.org/resource/John_Green_(author)> }"

    print("SPARQL-Query:", sparql_query)

    sparql = SPARQLWrapper("http://dbpedia.org/sparql/")
    sparql.setReturnFormat(JSON)
    sparql.setQuery(sparql_query)
    answer = sparql.query().convert()

    if not answer:
        qald_answer = qald_builder_empty_answer(sparql_query, question, lang)
    else:
        qald_answer = qald_builder(sparql_query, answer, question, lang)

    return qald_answer
