"""WSGI endpoint for embedding server."""

from app.embedding_hashtable import EmbeddingHashtable
from app.embedding_paths import ROOT_PATH
from app.main import main
from flask import Flask
from flask import jsonify
from flask import request
from flask import Response

application = Flask(__name__)
application.embedding_hashtable = EmbeddingHashtable(ROOT_PATH)
application.embedding_hashtable.load()


@application.route("/embedding_query/", methods=["POST"])
def endpoint() -> Response:
    """
    Endpoint for the embedding server.

    Expects a POST request with a json object containing a list of URIs called "uris"
    """
    if request.method == "POST":
        content = request.json
        if (
            content
            and "uris" in content
            and isinstance(content["uris"], list)
            and all(isinstance(uri, str) for uri in content["uris"])
        ):
            embedding_dict = main(application.embedding_hashtable, content["uris"])
            return jsonify(embedding_dict)
        else:
            error_dict = {"BAD_FORMAT": ":("}
            return jsonify(error_dict)
    return "GET not supported, use POST"
