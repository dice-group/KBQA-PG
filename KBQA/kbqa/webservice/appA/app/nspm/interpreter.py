"""Interperter module for translate english to sparql query."""
# pylint: disable=E0401
# pylint: disable=W0621
from typing import Tuple

from app.nspm.generator_utils import decode
from app.nspm.generator_utils import fix_URI
from app.nspm.spotlight import find_entity
from app.nspm.spotlight import replace_entity
from app.nspm.spotlight import restore_entity
from transformers import Pipeline
from transformers import pipeline

# for local test
# checkpoint_path = os.path.dirname(__file__) + '/../../../../resources/approach_a/data/checkpoint'

# for docker
checkpoint_path = "/data/checkpoint"


def init_summarizer() -> Pipeline:
    """Initialize the summarizer pipeline.

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


def preprocess_question(question: str) -> Tuple:
    """Preprocess the question.

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
    question_ph = replace_entity(question, entities)
    return question_ph, entities


def postprocess_query(query: str, entities: dict) -> str:
    """Postprocess the query.

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
    # query = restore_entity(query, entities)
    # query = decode(restore_entity(query, entities))
    query = fix_URI(decode(restore_entity(query, entities)))
    return query


def process_question(question: str) -> str:
    """Process the question.

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
    question_ph, entities = preprocess_question(question)
    # output_query = summarizer(question_ph)[0]['summary_text']
    output_query = postprocess_query(
        summarizer(question_ph)[0]["summary_text"], entities
    )

    return output_query


summarizer = init_summarizer()
