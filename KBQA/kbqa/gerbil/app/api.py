import os

from app.main import main
from flask import Flask
from flask import render_template

print("--- Start GERBIL")
main()
application = Flask(__name__)


@application.route("/gerbil/", methods=["GET", "POST"])
def endpoint():
    """Endpoint to serve GERBIL results

    :return: GERBIL results
    :rtype: Response
    """
    results = ""

    for file in os.listdir("/evaluation"):
        print(file)
        if file.endswith(".html"):
            path = os.path.join("/evaluation", file)
            print(path)

            with open(path, "r") as f:
                print(f.name)
                results += f.name
                results += f.read()
                results += "<br>"

    return render_template("index.html", results=results)
