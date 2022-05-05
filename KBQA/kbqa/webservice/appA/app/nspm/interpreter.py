import os

# from app.nspm.generator_utils import decode, fix_URI
# from app.nspm.spotlight import *

from generator_utils import decode, fix_URI
from spotlight import *
from transformers import pipeline


# checkpoint_path = "output_model/checkpoint"

# for local test
checkpoint_path = os.path.dirname(__file__) + '/../../../../resources/approach_a/data/checkpoint-1000'

# for docker
# checkpoint_path = "/data/checkpoint-1000"

def init_summarizer():
    summarizer = pipeline("summarization", model=checkpoint_path)
    return summarizer

summarizer = init_summarizer()

def preprocess_question(question):
    entities = find_entity(question)
    question_ph = replace_entities(question, entities)
    return question_ph, entities

def postprocess_query(query, entities):
    query = restore_entity(query, entities)
    query = decode(query)
    query = fix_URI(query)
    return query


def process_question(question):
    finaltrans = "input qurey: \n"
    finaltrans += question

    question_ph, entities = preprocess_question(question)

    finaltrans += "\n\n\ninput query with placeholder:\n"
    finaltrans += question_ph

    finaltrans += "\n\n\nentities:\n"
    for placeholder, (entity, uri) in entities.items():
        finaltrans += "{},  {},  {}".format(placeholder, entity, uri)


    finaltrans += "\n\n\noutput qurey with placeholder:\n"
    output_query = summarizer(question_ph)[0]['summary_text']
    finaltrans += output_query

    output_query = postprocess_query(output_query, entities)
    finaltrans += "\n\n\noutput qurey:\n"
    finaltrans += output_query

    print(finaltrans)

    return output_query

process_question("Name the alma mater of Barack Obama?")