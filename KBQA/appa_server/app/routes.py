from app import application
from flask import request
from get_answer import get_answer
from get_query import QA_query_generation


def get_single_answer(answers):
    """
    Return from all answers the first valid answer
    """
    for answer in answers:
        if answer["results"]["bindings"]:
            answer["head"].pop("link", None)
            answer["results"].pop("distinct", None)
            answer["results"].pop("ordered", None)
            return answer
    return None


@application.route("/", methods=["POST"])
def post_query():
    """
    Requesting an answer to some question.
    :return: JSON for GERBIL
    """
    query_generator = QA_query_generation()

    question = request.form["query"]

    json_answers = []
    for query in query_generator.get_query(question):
        json_answer = get_answer(query)
        json_answers.append(json_answer)
    return get_single_answer(json_answers)
