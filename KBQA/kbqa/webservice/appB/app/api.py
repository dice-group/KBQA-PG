"""API for approach B. There is only a POST endpoint."""
from app.main import main
from flask import Flask
from flask import request


application = Flask(__name__)


@application.route("/appB/", methods=["POST"])
def endpoint() -> str:
    """Endpoint for approach B.

    This endpoint only accepts POST requests, which sets a
    parameter query for the asked natural language question
    and an optional language tag.

    Returns
    -------
    answer : dict
        JSON-dict, which contains the question, the answers and the
        query in the QALD format.
    """
    query = request.form["query"]

    # check, whether the language parameter is set
    if "lang" in request.form.keys():
        lang = request.form["lang"]

        answer = main(query, lang)
    else:
        answer = main(query)

    return answer
