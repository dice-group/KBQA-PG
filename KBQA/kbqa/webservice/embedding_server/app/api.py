"""WSGI endpoint for embedding server."""
from app.embedding_paths import ROOT_PATH
from app.embeddings import EntityHashTable
from app.embeddings import RelationEmbeddings
from app.main import main
from flask import Flask
from flask import jsonify
from flask import request
from flask import Response

application = Flask(__name__)
application.entity_hashtable = EntityHashTable(ROOT_PATH)
application.entity_hashtable.load()
application.relation_embeddings = RelationEmbeddings(ROOT_PATH)
application.relation_embeddings.load()


@application.route("/embedding_query/", methods=["POST"])
def endpoint() -> Response:
    """
    Endpoint for the embedding server.

    Expects a POST request with a json object containing a list of entity URIs called "entities"
    and a list of relation URIs called "relations"
    """
    if request.method == "POST":
        content = request.json
        if (
            content
            and "entities" in content
            and check_uri_list(content["entities"])
            and "relations" in content
            and check_uri_list(content["relations"])
        ):
            embedding_dict = main(
                application.entity_hashtable,
                application.relation_embeddings,
                content["entities"],
                content["relations"],
            )
            return jsonify(embedding_dict)
        else:
            error_dict = {"BAD_FORMAT": ":("}
            return jsonify(error_dict)
    return "GET not supported, use POST"


def check_uri_list(uri_list: list) -> bool:
    """
    Check format of uri_list by validating that it is a list and that every member is a string.

    :param uri_list: list of uris to check
    :return: True/False depending on whether the list is in the correct format
    """
    return isinstance(uri_list, list) and all(isinstance(uri, str) for uri in uri_list)
