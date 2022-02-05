"""Arguments for the summarizers."""
from types import SimpleNamespace

ONE_HOP_RANK_SUMMARIZER = SimpleNamespace(
    **{
        # lowest rank of triples
        "lower_rank": 1,
        # maximum number of triples of the same form
        "max_triples": 3,
        # maximum triples
        "limit": 50,
        # timeout between requests
        "timeout": 0,
    }
)
