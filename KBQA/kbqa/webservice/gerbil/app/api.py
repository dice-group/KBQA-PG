"""Website for GERBIL evaluation results."""

import json
import os
from typing import Tuple

from app.config import Approach
from app.config import approaches
from app.config import decode_experiment_filename
from app.evaluation import evaluate_approaches
from flask import Flask
from flask import render_template
from flask import Response


def load_evaluation(approach: Approach) -> Tuple[str, str]:
    """Load evaluation files and compile website data.

    Parameters
    ----------
    approach : Approach
        Selected approach

    Returns
    -------
    Tuple[str, str]
        Tuple of GERBIL evaluations and a JSON summary
    """
    evaluations = ""
    summary = ""
    repository_url = "https://github.com/dice-group/KBQA-PG/commit/"

    try:
        with open(
            f"/evaluation/summary-{approach.name}.json", "r", encoding="utf-8"
        ) as summary_file:  # TODO: Add App B
            summary = json.load(summary_file)
    except OSError:
        print("No evaluation summary found.")

    for path, _, files in os.walk("/evaluation"):
        for file in files:
            if file.endswith(".html"):
                file_path = os.path.join(path, file)
                print(path)

                with open(file_path, "r", encoding="utf-8") as result_file:
                    print(result_file)
                    gerbil_url, gerbil_id, _, commit_id = decode_experiment_filename(
                        file
                    )
                    evaluations += f'<h3><a href="{gerbil_url}{gerbil_id}"> GERBIL #{gerbil_id}</a> on <a href="{repository_url}{commit_id}"> version #{commit_id}</a></h3>.'
                    evaluations += result_file.read()
                    evaluations += "<br>"

    return evaluations, summary


data = dict()


def reload_evaluations() -> None:
    """Reload evaluations of all approaches."""
    for our_approach in approaches:
        data[our_approach.name] = load_evaluation(our_approach)


reload_evaluations()
application = Flask(__name__)


@application.route("/gerbil/", methods=["GET"])
def endpoint() -> Response:
    """
    Endpoint to serve GERBIL results.

    Returns
    -------
    Response
        Evaluation webpage
    """
    return render_template("index.html", evaluations=data)


@application.route("/gerbil/start/", methods=["GET"])
def start_evaluation() -> Response:
    """
    Endpoint to start a new GERBIL evaluation.

    Returns
    -------
    Response
        When finished
    """
    evaluate_approaches("dice")
    reload_evaluations()
    return "Finished"


start_evaluation()
