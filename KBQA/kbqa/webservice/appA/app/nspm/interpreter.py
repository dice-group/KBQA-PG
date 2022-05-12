from ast import Dict, Tuple
import os

from app.nspm.generator_utils import decode, fix_URI
from app.nspm.spotlight import *

from transformers import pipeline

# for local test
# checkpoint_path = os.path.dirname(__file__) + '/../../../../resources/approach_a/data/checkpoint'

# for docker
checkpoint_path = "/data/checkpoint"

def init_summarizer():
    """Initialize the summarizer pipeline

    initialize the summarizer pipeline with the checkpoint file in checkpoint_path. 

    Parameters
    ----------
    None

    Returns
    -------
    summarizer : pipeline.Pipeline
        Summarizer pipeline with the model in checkpoint_path.
    """
    summarizer = pipeline("summarization", model=checkpoint_path)
    return summarizer

summarizer = init_summarizer()

def preprocess_question(question : str) -> Tuple[str, Dict[str, Tuple[str, str]]]:
    """Preprocess the question
    
    preprocess the question by extracting the entities and replacing the placeholders with the entities. 

    Parameters
    ----------
    question : str
        Natural language question asked by an enduser.
    
    Returns
    -------
    question_ph : str
        Question with the placeholders replaced with the entities.
    entities : dict
        Dictionary with the placeholders as keys and the entities as values.
    """
    entities = find_entity(question)
    question_ph = replace_entities(question, entities)
    return question_ph, entities

def postprocess_query(query, entities):
    """Postprocess the query
    
    Postprocess the query by replacing the placeholders with the entities, 
    convert to normal sparql query with punctuation and 
    fix URIs. 

    Parameters
    ----------
    query : str
        Query with the placeholders from transformer. 
    entities : dict
        Dictionary with the placeholders as keys and the entities as values.
    
    Returns
    -------
    query : str
        Query with the placeholders replaced with the entities.
    """
    query = restore_entity(query, entities)
    query = decode(query)
    query = fix_URI(query)
    return query


def process_question(question):
    """Process the question
    
    Process the question by extracting the entities,  
    replacing the placeholders with the entities, 
    summarize to a sparql query and
    postprocess the query.

    Parameters
    ----------
    question : str
        Natural language question asked by an enduser.
    
    Returns
    -------
    query : str
        Sparql Query with the placeholders replaced with the entities.
    """
    # finaltrans = "input qurey: \n" +question

    question_ph, entities = preprocess_question(question)

    # finaltrans += "\n\n\ninput query with placeholder:\n" + question_ph

    # finaltrans += "\n\n\nentities:\n"
    # for placeholder, (entity, uri) in entities.items():
    #     finaltrans += "{},  {},  {}".format(placeholder, entity, uri)

    output_query = summarizer(question_ph)[0]['summary_text']

    # finaltrans += "\n\n\noutput qurey with placeholder:\n" + output_query

    output_query = postprocess_query(output_query, entities)
    
    # finaltrans += "\n\n\noutput qurey:\n" + output_query

    # print(finaltrans)

    return output_query