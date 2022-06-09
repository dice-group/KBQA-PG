"""API for approach A. There is only a POST endpoint."""
from typing import Dict
from typing import Tuple

from app.main import main
from flask import abort
from flask import Flask
from flask import jsonify
from flask import request
from flask import Response
from werkzeug.exceptions import HTTPException


application = Flask(__name__)


@application.route("/appA/", methods=["POST"])
def endpoint() -> Response:
    """Endpoint for approach A.

    This endpoint only accepts POST requests, which sets a
    parameter query for the asked natural language question
    and an optional language tag.

    Returns
    -------
    answer : dict
        JSON-dict, which contains the question, the answers and the
        query in the QALD format.
    """
    query = request.form.get("query")

    if query is None:
        abort(400, description="Missing parameter 'query'")

    answer = main(query)

    return jsonify(answer)


@application.errorhandler(400)
def bad_request(error: HTTPException) -> Tuple[Dict[str, str], int]:
    """Error handler for wrong requests (Bad Request).

    Parameters
    ----------
    error : HTTPException
        HTTPException with status code 400.

    Returns
    -------
    dict
        Dictionary containing the information with the wrong parameter.
    """
    return jsonify({"status": "400", "msg": str(error)}), 400


@application.errorhandler(500)
def internal_error(error: HTTPException) -> Tuple[Dict[str, str], int]:
    """Error handler for internal error from the app.

    Parameters
    ----------
    error : HTTPException
        HTTPException with status code 500.

    Returns
    -------
    dict
        Dictionary containing the information that an internal error occured.
    """
    return jsonify({"status": "500", "msg": str(error)}), 500
