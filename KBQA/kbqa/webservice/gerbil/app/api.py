"""Website for GERBIL evaluation results."""

import json
import os

from app.main import startup
from flask import Flask
from flask import render_template
from flask import Response

print("--- Start GERBIL")
startup()  # DEBUG
application = Flask(__name__)


@application.route("/gerbil/", methods=["GET"])
def endpoint() -> Response:
    """Endpoint to serve GERBIL results.

    :return: GERBIL results
    :rtype: Response
    """
    results = ""
    data = ""
    repository_url = "https://github.com/dice-group/KBQA-PG/commit/"
    gerbil_url = "http://gerbil-qa.aksw.org/gerbil/experiment?id="
    gerbil_url = "http://gerbil-qa.cs.upb.de:8080/gerbil/experiment?id="
    # TODO: Read gerbil url from file

    with open(
        "./evaluation/summary-appA.json", "r", encoding="utf-8"
    ) as summary_file:  # TODO: Add App B
        data = json.load(summary_file)

    for path, _, files in os.walk("/evaluation"):
        for file in files:
            if file.endswith(".html"):
                file_path = os.path.join(path, file)
                print(path)

                with open(file_path, "r", encoding="utf-8") as result_file:
                    print(result_file)
                    commit_id, gerbil_id = file.split(".")[0].split("-")
                    results += f'<h3><a href="{gerbil_url}{gerbil_id}"> GERBIL #{gerbil_id}</a> on <a href="{repository_url}{commit_id}"> version #{commit_id}</a></h3>.'
                    results += result_file.read()
                    results += "<br>"

    return render_template("index.html", results=results, data=data)
