"""Main module for the application logic of approach B."""
from app.qald_builder import qald_builder
from app.qald_builder import qald_builder_empty_answer
from SPARQLWrapper import JSON
from SPARQLWrapper import SPARQLWrapper


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
    # ===========================================
    # Add here the logic for approach B and
    # return the answer in the QALD format
    # ===========================================

    # -------------------- Example ----------------------
    # Example in order to check, whether the connection works
    print("Question:", query.encode("utf-8"))

    answer_qald = example(query, lang)

    return answer_qald


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

    # only to make gerbil work for the moment
    qald_answer = qald_builder_empty_answer(sparql_query, question, lang)

    return qald_answer
