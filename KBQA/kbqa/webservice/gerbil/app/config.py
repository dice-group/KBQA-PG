"""Config for the gerbil service."""


from typing import Optional
from typing import Tuple


class Approach:
    """Approach for a QA system."""

    def __init__(
        self,
        name: str,
        url: Optional[str] = None,
        experiment_name: Optional[str] = None,
        experiment_id: int = 0,
    ) -> None:
        """Initialize an Approach.

        Parameters
        ----------
        name : str
            Name of the approach
        url : str, optional
            URL to the API endpoint of the approach, by default "http://kbqa-pg.cs.upb.de/{name}"
        experiment_name : str, optional
            Name of the evaluation of this approach, by default "NIFWS_KBQA-PG-{name}"
        experiment_id : int, optional
            Latest GERBIL experiment id, by default None
        """
        if url is None:
            url = f"http://kbqa-pg.cs.upb.de/{name}"

        if experiment_name is None:
            experiment_name = f"NIFWS_KBQA-PG-{name}"

        self.name = name
        self.url = url
        self.experiment_name = experiment_name
        self.experiment_id = experiment_id


approaches = [Approach("appA"), Approach("appB")]

gerbil_systems = {
    "aksw": "http://gerbil-qa.aksw.org/gerbil",
    "dice": "http://gerbil-qa.cs.upb.de:8080/gerbil",
}

gerbil_datasets = [
    "LCQUAD",
    "NLQ",
    "QALD1 Test DBpedia",
    "QALD1 Test Musicbrainz",
    "QALD1 Train DBpedia",
    "QALD1 Train Musicbrainz",
    "QALD3 Test DBpedia",
    "QALD3 Train DBpedia",
    "QALD4 Test Hybrid",
    "QALD4 Test Multilingual",
    "QALD4 Train Hybrid",
    "QALD4 Train Multilingual",
    "QALD5 Test Hybrid",
    "QALD5 Test Multilingual",
    "QALD5 Train Hybrid",
    "QALD5 Train Multilingual",
    "QALD6 Test Hybrid",
    "QALD6 Test Multilingual",
    "QALD6 Train Hybrid",
    "QALD6 Train Multilingual",
    "QALD7 Test Multilingual",
    "QALD7 Test Wikidata en",
    "QALD7 Train Hybrid",
    "QALD7 Train Multilingual",
    "QALD7 Train Wikidata en",
    "QALD8 Test Multilingual",
    "QALD8 Train Multilingual",
    "QALD9 Test Multilingual",
    "QALD9 Train Multilingual",
]  # "DBpedia Entity INEX","DBpedia Entity QALD2","DBpedia Entity SemSearch","DBpedia Entity TREC Entity" can not be loaded

# gerbil_datasets = ["QALD9 Test Multilingual"] # DEBUG


def decode_experiment_filename(filename: str) -> Tuple[str, int, str, str]:
    """Decode the given filename into its parameters.

    :param filename: Filename with file extension
    :type filename: str
    :return: Returns the gerbil_id, gerbil_system, commit_id
    :rtype: Tuple[str, int, str, str]
    """
    gerbil_id, gerbil_system, commit_id = filename.split(".")[0].split("-")
    gerbil_url = f"{gerbil_systems[gerbil_system]}/experiment?id="

    return gerbil_url, int(gerbil_id), gerbil_system, commit_id


def encode_experiment_filename(
    gerbil_id: int, gerbil_system: str, commit_id: str
) -> str:
    """Encode the given parameter into a filename.

    :param gerbil_id: The GERBIL ID
    :type gerbil_id: int
    :param gerbil_system: The GERBIL system key
    :type gerbil_system: str
    :param commit_id: The commit id
    :type commit_id: str
    :return: Filename without extension
    :rtype: str
    """
    return f"{gerbil_id}-{gerbil_system}-{commit_id}"
