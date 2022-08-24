"""Provide functions to preprocess summarized triples."""
from .preprocessing_qtq.preprocessing_qtq import preprocessing_qtq
from .preprocessing_qtq.seperate_qtq import QTQ_DATA_DIR
from .preprocessing_qtq.seperate_qtq import seperate_qtq
from .preprocessing_qtq.seperate_qtq import SPLIT_NAME

__all__ = ["preprocessing_qtq", "seperate_qtq", "QTQ_DATA_DIR", "SPLIT_NAME"]
