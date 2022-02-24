# coding=utf-8
# Copyright 2018 The Google AI Language Team Authors and The HuggingFace Inc. team.
# Copyright (c) 2018, NVIDIA CORPORATION.  All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
Using the tokenizer of the given model to tokenize a dataset.
"""

from __future__ import absolute_import

import argparse
from io import open
import logging

from transformers import BertConfig
from transformers import BertModel
from transformers import BertTokenizer
from transformers import RobertaConfig
from transformers import RobertaModel
from transformers import RobertaTokenizer

MODEL_CLASSES = {
    "roberta": (RobertaConfig, RobertaModel, RobertaTokenizer),
    "bert": (BertConfig, BertModel, BertTokenizer),
}

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(name)s -   %(message)s",
    datefmt="%m/%d/%Y %H:%M:%S",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


class Example:
    """A single example."""

    def __init__(self, id_, text):
        self.id_ = id_
        self.text = text


def read_examples(filename):
    """Read examples from file_path."""
    examples = []
    with open(filename, encoding="utf-8") as example_file:
        for id_, line in enumerate(example_file):
            examples.append(
                Example(
                    id_=id_,
                    text=line.strip(),
                )
            )
    return examples


def convert_examples_to_features(examples, tokenizer, args):
    for example_index, example in enumerate(examples):
        tokens = tokenizer.tokenize(example.text)[: args.max_number_tokens]
        ids = tokenizer.convert_tokens_to_ids(tokens)
        mask = [1] * (len(tokens))
        padding_length = args.max_number_tokens - len(ids)
        ids += [tokenizer.pad_token_id] * padding_length
        mask += [0] * padding_length

        logger.info("*** Example ***")
        logger.info("id: {}".format(example.id_))

        logger.info("example: {}".format(example.text))
        logger.info(
            "tokens: {}".format(
                [x.replace("\u0120", "_") for x in tokens]
            )
        )
        if args.print_token_ids:
            logger.info("ids: {}".format(" ".join(map(str, ids))))
        if args.print_mask:
            logger.info("mask: {}".format(" ".join(map(str, mask))))


def main():
    parser = argparse.ArgumentParser()

    # Required parameters
    parser.add_argument(
        "--model_name_or_path",
        type=str,
        required=True,
        help="Path to pre-trained model: e.g. roberta-base",
    )
    parser.add_argument(
        "--model_type",
        type=str,
        required=True,
        help="Model type: e.g. bert",
    )
    parser.add_argument(
        "--filename",
        type=str,
        required=True,
        help="The file which should be tokenized.",
    )
    parser.add_argument(
        "--max_number_tokens",
        type=int,
        required=True,
        help="The maximum number of tokens generated.",
    )

    # Not required
    parser.add_argument(
        "--print_token_ids",
        action="store_true",
        help="Set this flag if you want to have the ids of the tokens printed.",
    )
    parser.add_argument(
        "--print_mask",
        action="store_true",
        help="Set this flag if you want to see the mask of the token sequence printed.",
    )
    parser.add_argument(
        "--tokenizer_name",
        default="",
        type=str,
        help="Pretrained tokenizer name or path if not the same as model_name",
    )
    parser.add_argument(
        "--do_lower_case",
        action="store_true",
        help="Set this flag if you are using an uncased model.",
    )

    # print arguments
    args = parser.parse_args()
    logger.info(args)

    # Load models.
    _, _, tokenizer_class = MODEL_CLASSES[args.model_type]
    tokenizer = tokenizer_class.from_pretrained(
        args.tokenizer_name if args.tokenizer_name else args.model_name_or_path,
        do_lower_case=args.do_lower_case,
    )

    examples = read_examples(
        args.filename
    )
    convert_examples_to_features(
        examples, tokenizer, args
    )


if __name__ == "__main__":
    main()
