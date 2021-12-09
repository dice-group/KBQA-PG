import requests

from SPARQLWrapper import SPARQLWrapper, JSON
from app.qald_builder import qald_builder, qald_builder_empty_answer
from app.nspm.interpreter_pt_model import process_question


def main(query, lang='en'):
    '''
    Process the query, which contains the question asked by an user and a language
    Query in format "query=What is the capital of Germany?&lang=en"
    returns answer in qald format
    '''

    answer, sparql_query = interprete(query)

    if sparql_query == "":
        answer_qald = qald_builder_empty_answer(sparql_query, query, lang)
    else:        
        answer_qald = qald_builder(sparql_query, answer, query, lang)

    return answer_qald

def interprete(question):
    # TODO do not allow None types
    try:
        sparql_query = process_question(question)
    
        print('Predicted SPARQL-Query:', sparql_query)
        sparql = SPARQLWrapper("http://dbpedia.org/sparql/")
        sparql.setReturnFormat(JSON)
        sparql.setQuery(sparql_query)
        answer = sparql.query().convert()

    except Exception as e:
        print('Exception', e)
        return "", ""
    
    return answer, sparql_query
