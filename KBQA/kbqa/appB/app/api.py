from app.main import main
from flask import Flask
from flask import request


application = Flask(__name__)


@application.route("/appB/", methods=["GET", "POST"])
def endpoint():

    if request.method == "POST":
        query = request.form["query"]

        # check, whether the language parameter is set
        if "lang" in request.form.keys():
            lang = request.form["lang"]

            answer = main(query, lang)
        else:
            answer = main(query)

        return answer

    # TODO also allow GET-requests
    return "<h1>This is the endpoint of approach B. There is nothing to see here</h1>"
