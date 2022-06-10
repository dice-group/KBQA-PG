from typing import Dict, List

from allennlp.data.fields.field import DataArray
from allennlp.data.fields.field import Field
from allennlp.data.vocabulary import Vocabulary
from overrides import overrides

SEPERATOR = "*"


class DictField(Field):
    """
    dict with values as fields
    """

    def __init__(self, field_dict: Dict[str, Field]) -> None:
        self.field_dict = field_dict

    @overrides
    def count_vocab_items(self, counter: Dict[str, Dict[str, int]]) -> None:
        for field in self.field_dict.values():
            field.count_vocab_items(counter)

    @overrides
    def index(self, vocab: Vocabulary) -> None:
        for field in self.field_dict.values():
            field.index(vocab)

    @overrides
    def get_padding_lengths(self) -> Dict[str, int]:
        padding_lengths = {}
        for key, field in self.field_dict.items():
            for sub_key, val in field.get_padding_lengths().items():
                padding_lengths[key + SEPERATOR + sub_key] = val
        return padding_lengths

    @overrides
    def as_tensor(self, padding_lengths: Dict[str, int]) -> DataArray:
        # padding_lengths is flattened from the nested structure -- unflatten
        pl : Dict = {}
        for full_key, val in padding_lengths.items():
            key, _, sub_key = full_key.partition(SEPERATOR)
            if key not in pl:
                pl[key] = {}
            pl[key][sub_key] = val

        ret = {}
        for key, field in self.field_dict.items():
            ret[key] = field.as_tensor(pl[key])

        return ret

    @overrides
    def empty_field(self) -> Field:
        return DictField(
            {key: field.empty_field() for key, field in self.field_dict.items()}
        )

    @overrides
    def batch_tensors(self, tensor_list: List[DataArray]) -> Dict:
        ret = {}
        for key, field in self.field_dict.items():
            ret[key] = field.batch_tensors([t[key] for t in tensor_list])
        return ret

    def __str__(self) -> str:
        return ""
