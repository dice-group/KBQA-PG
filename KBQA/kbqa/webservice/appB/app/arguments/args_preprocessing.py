"""Arguments for the preprocessing step."""
from types import SimpleNamespace

SEPERATE_QTQ = SimpleNamespace(
    **{
        # --data, dest="data_dir", required=True
        "data_dir": "app/data",
        # --subset, dest="subset", required=True
        "subset": "question",
        # --output, dest="output_dir", required=True
        "output_dir": "app/data",
    }
)

PREPROCESSING_QTQ = SimpleNamespace(
    **{
        # --data, dest="data_dir", required=True
        "data_dir": "app/data",
        # --subset, dest="subset", required=True
        "subset": "question",
        # --output, dest="output_dir", required=True
        "output_dir": "app/data",
    }
)
