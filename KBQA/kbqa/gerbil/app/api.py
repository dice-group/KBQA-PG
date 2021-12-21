from flask import Flask
from werkzeug.utils import send_from_directory


application = Flask(__name__)


@application.route("/gerbil/", methods=["GET", "POST"])
def endpoint():
    """Endpoint to serve GERBIL results

    :return: GERBIL results
    :rtype: Response
    """
    return send_from_directory("experiments", "latest.html")
