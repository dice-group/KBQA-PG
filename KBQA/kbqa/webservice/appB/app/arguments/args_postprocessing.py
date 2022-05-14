"""Arguments for the postprocessing step."""
from types import SimpleNamespace

POSTPROCESSING = SimpleNamespace(
    **{
        # path tp predict_file
        "predict_dir": "app/output/",
        # predict file
        "predict_file": "predict_0.output",
    }
)
