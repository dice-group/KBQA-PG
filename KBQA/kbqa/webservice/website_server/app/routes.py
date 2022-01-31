"""API for the website server."""
import os
from typing import Dict

from app.handler import process_question
from flask import Flask
from flask import jsonify
from flask import render_template
from flask import request


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
        branch = os.environ["GITHUB_REF_NAME"]
    except KeyError:
        pass

    if branch == "master":
        switch_text = "Check out our development version!"
        switch_url = "/dev/"
    elif branch == "develop":
        switch_text = "Go to our release!"
        switch_url = "/"
    else:
        switch_text = "Local deployment!"
        switch_url = "/"

    return render_template(
        "index.html", branch=branch, switch_text=switch_text, switch_url=switch_url
    )


@application.route("/", methods=["POST"])
def query_fun() -> Dict:
    """Request an answer to some question.

    Returns
    -------
    result : dict
        JSON dict, which contains the asked question, the answers for this questions
        and the generated query.
    """
    question = request.form["question"]
    chosen_app = request.form["approach"]
    answers, query = process_question(question, chosen_app)

    return jsonify({"question": question, "answers": answers, "query": query})


@application.errorhandler(500)
def internal_error(error: str) -> str:
    """If something happens internally, return an HTML with error 500.

    Parameters
    ----------
    error : str
        error object thrown by the actual exception.

    Returns
    -------
    error_page : str
        HTML with error 500.
    """
    print(error)

    return render_template("500.html")
