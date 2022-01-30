"""Approach for a QA system."""


class Approach:
    """Approach for a QA system."""

    def __init__(
        self,
        name: str,
        url: str = None,
        experiment_name: str = None,
        experiment_id: int = None,
    ) -> None:
        """Initialize an Approach.

        Parameters
        ----------
        name : str
            Name of the approach
        url : str, optional
            URL to the API endpoint of the approach, by default "http://kbqa-pg.cs.upb.de/{name}/"
        experiment_name : str, optional
            Name of the evaluation of this approach, by default "NIFWS_KBQA-PG-{name}"
        experiment_id : int, optional
            Latest GERBIL experiment id, by default None
        """
        if url is None:
            url = f"http://kbqa-pg.cs.upb.de/{name}/"

        if experiment_name is None:
            experiment_name = f"NIFWS_KBQA-PG-{name}"

        self.name = name
        self.url = url
        self.experiment_name = experiment_name
        self.experiment_id = experiment_id
