"""Main module for the application logic of approach A."""
from typing import Any
from typing import Dict
from typing import Tuple

from app.nspm.interpreter import process_question
from app.qald_builder import qald_builder_ask_answer
from app.qald_builder import qald_builder_empty_answer
from app.qald_builder import qald_builder_select_answer
from SPARQLWrapper import JSON
from SPARQLWrapper import SPARQLWrapper
from SPARQLWrapper.SPARQLExceptions import SPARQLWrapperException


def main(query: str, lang: str = "en") -> Dict[str, Any]:
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
    print("Question:", query.encode("utf-8"))

    sparql_query = interprete(query)
    answer_qald = ask_dbpedia(query, sparql_query, lang)

    return answer_qald

def interprete(question: str) -> Tuple[Dict, str]:
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
    try:
        # Unfortunately, the NSPM throws an error if it is not able
        # to find a SPARQL query.
        sparql_query = process_question(question)
    except TypeError as type_error:
        print("Type Error", type_error)
        return {}, ""

    print("Predicted SPARQL-Query:", sparql_query)
    return sparql_query

def ask_dbpedia(question: str, sparql_query: str, lang: str) -> Dict[str, Any]:
    """Send a SPARQL-query to DBpedia and return a formated QALD-string containing the answers.

    Parameters
    ----------
    question : str
        Natural language question asked by an enduser.
    sparql_query : str
        SPARQL-query to be sent to DBpedia. Should correspond to the question.
    lang : str
        Language tag for the question (should always be "en").

    Returns
    -------
    qald_answer : str
        Formated string in the QALD-format containing the answers for the sparql_query.
    """
    print("SPARQL-Query:", sparql_query.encode("utf-8"))

    try:
        sparql = SPARQLWrapper("http://dbpedia.org/sparql/")
        sparql.setReturnFormat(JSON)
        sparql.setQuery(sparql_query)
        answer = sparql.query().convert()
    except SPARQLWrapperException as exception:
        print("SPARQLWrapperException", exception)
        qald_answer = qald_builder_empty_answer("", question, lang)
        return qald_answer

    if "results" in dict(answer):
        # SELECT queries
        if len(answer["results"]["bindings"]) == 0:
            qald_answer = qald_builder_empty_answer(sparql_query, question, lang)
        else:
            qald_answer = qald_builder_select_answer(
                sparql_query, answer, question, lang
            )
    elif "boolean" in dict(answer):
        # ASK queries
        qald_answer = qald_builder_ask_answer(sparql_query, answer, question, lang)
    else:
        print("No results and boolean found.")
        qald_answer = qald_builder_empty_answer("", question, lang)

    return qald_answer