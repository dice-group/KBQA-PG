"""API for the website server."""
import os
from typing import Dict
from typing import Tuple

from app.handler import process_question
from flask import abort
from flask import Flask
from flask import jsonify
from flask import render_template
from flask import request
from werkzeug.exceptions import HTTPException


application = Flask(__name__)


@application.route("/", methods=["GET"])
def index() -> str:
    """Home website.

    Returns
    -------
    website : str
        HTML home website.
    """
    switch_text = ""
    switch_url = ""
    branch = "local"
    try:
        branch = os.environ["BRANCH"]
    except KeyError:
        branch = ""

    if branch == "master":
        switch_text = "Check out our development version!"
        switch_url = "/dev/"
    elif branch == "dev":
        switch_text = "Go to our release!"
        switch_url = "/"
    else:
        switch_text = "Local deployment!"
        switch_url = "/"

    return render_template(
        "index.html", branch=branch, switch_text=switch_text, switch_url=switch_url
    )


@application.route("/", methods=["POST"])
def query_fun() -> Dict[str, str]:
    """Request an answer to some question.

    Returns
    -------
    result : dict
        JSON dict, which contains the asked question, the answers for this questions
        and the generated query.
    """
    question = request.form.get("question")
    chosen_app = request.form.get("approach")

    if question is None:
        abort(400, description="Missing parameter 'question'")

    if chosen_app is None:
        abort(400, description="Missing parameter 'approach'")

    if chosen_app not in ["A", "B"]:
        abort(400, description="Approach should be 'A' or 'B'")

    answers, query = process_question(question, chosen_app)

    return jsonify(
        {"status": "200", "question": question, "answers": answers, "query": query}
    )


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
    """Error handler for internal errors.

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


@application.errorhandler(502)
def bad_gateway(error: HTTPException) -> Tuple[Dict[str, str], int]:
    """Error handler for bad gateway errors.

    Parameters
    ----------
    error : HTTPException
        HTTPException with status code 502.

    Returns
    -------
    dict
        Dictionary containing the information that a bad gateway error occured.
    """
    return jsonify({"status": "502", "msg": str(error)}), 502


@application.errorhandler(504)
def gateway_timeout(error: HTTPException) -> Tuple[Dict[str, str], int]:
    """Error handler for gateway timeouts.

    Parameters
    ----------
    error : HTTPException
        HTTPException with status code 504.

    Returns
    -------
    dict
        Dictionary containing the information that an gateway timeout error occured.
    """
    return jsonify({"status": "504", "msg": str(error)}), 504
