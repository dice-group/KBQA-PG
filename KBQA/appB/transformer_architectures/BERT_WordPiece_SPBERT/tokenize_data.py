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
Fine-tuning the library models for language modeling on a text file (BERT, RoBERTa).
BERT and RoBERTa are fine-tuned using a masked language modeling (MLM) loss.
"""

from __future__ import absolute_import

import argparse
from io import open
import logging
import os
import random
import re

from model import BertSeq2Seq
from model import Seq2Seq
from nltk.translate.bleu_score import corpus_bleu
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from torch.utils.data import RandomSampler
from torch.utils.data import SequentialSampler
from torch.utils.data import TensorDataset
from torch.utils.data.distributed import DistributedSampler
from tqdm import tqdm
from transformers import AdamW
from transformers import BertConfig
from transformers import BertModel
from transformers import BertTokenizer
from transformers import get_linear_schedule_with_warmup
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
    """A single training/test example."""

    def __init__(self, idx, source, triples, target):
        self.idx = idx
        self.source = source
        self.triples = triples
        self.target = target


def read_examples(source_file, triples_file, target_file):
    """Read examples from filename."""
    examples = []
    with open(source_file, encoding="utf-8") as source_f:
        with open(triples_file, encoding="utf-8") as triples_f:
            with open(target_file, encoding="utf-8") as target_f:
                for idx, (source, triples, target) in enumerate(
                    zip(source_f, triples_f, target_f)
                ):
                    examples.append(
                        Example(
                            idx=idx,
                            source=source.strip(),
                            triples=triples.strip(),
                            target=target.strip(),
                        )
                    )
    return examples


def read_examples_without_target(source_file, triples_file):
    """Read examples from filename."""
    examples = []
    with open(source_file, encoding="utf-8") as source_f:
        with open(triples_file, encoding="utf-8") as triples_f:
            for idx, (source, triples) in enumerate(
                zip(source_f, triples_f)
            ):
                examples.append(
                    Example(
                        idx=idx,
                        source=source.strip(),
                        triples=triples.strip(),
                        target="",
                    )
                )
    return examples


class InputFeatures:
    """A single training/test features for a example."""

    def __init__(
        self,
        example_id,
        source_ids,
        triples_ids,
        target_ids,
        source_mask,
        triples_mask,
        target_mask,
    ):
        self.example_id = example_id
        self.source_ids = source_ids
        self.triples_ids = triples_ids
        self.target_ids = target_ids
        self.source_mask = source_mask
        self.triples_mask = triples_mask
        self.target_mask = target_mask


def convert_examples_to_features(examples, tokenizer, args, stage=None):
    features = []
    for example_index, example in enumerate(examples):
        # source
        source_tokens = tokenizer.tokenize(example.source)[: args.max_source_length - 2]
        source_tokens = [tokenizer.cls_token] + source_tokens + [tokenizer.sep_token]
        source_ids = tokenizer.convert_tokens_to_ids(source_tokens)
        source_mask = [1] * (len(source_tokens))
        padding_length = args.max_source_length - len(source_ids)
        source_ids += [tokenizer.pad_token_id] * padding_length
        source_mask += [0] * padding_length

        # triples
        triples_tokens = tokenizer.tokenize(example.triples)[: args.max_triples_length]
        triples_ids = tokenizer.convert_tokens_to_ids(triples_tokens)
        triples_mask = [1] * (len(triples_tokens))
        padding_length = args.max_triples_length - len(triples_ids)
        triples_ids += [tokenizer.pad_token_id] * padding_length
        triples_mask += [0] * padding_length

        # target
        if stage == "test" or stage == "predict":
            target_tokens = tokenizer.tokenize("None")
        else:
            target_tokens = tokenizer.tokenize(example.target)[
                : args.max_target_length - 2
            ]
        target_tokens = [tokenizer.cls_token] + target_tokens + [tokenizer.sep_token]
        target_ids = tokenizer.convert_tokens_to_ids(target_tokens)
        target_mask = [1] * len(target_ids)
        padding_length = args.max_target_length - len(target_ids)
        target_ids += [tokenizer.pad_token_id] * padding_length
        target_mask += [0] * padding_length

        if stage == "train":
            logger.info("*** Example ***")
            logger.info("idx: {}".format(example.idx))

            logger.info("source_example: {}".format(example.source))
            logger.info(
                "source_tokens: {}".format(
                    [x.replace("\u0120", "_") for x in source_tokens]
                )
            )
            # logger.info("source_ids: {}".format(" ".join(map(str, source_ids))))
            # logger.info("source_mask: {}".format(" ".join(map(str, source_mask))))

            logger.info("triples_example: {}".format(example.triples))
            logger.info(
                "triples_tokens: {}".format(
                    [x.replace("\u0120", "_") for x in triples_tokens]
                )
            )
            # logger.info("triples_ids: {}".format(" ".join(map(str, triples_ids))))
            # logger.info("triples_mask: {}".format(" ".join(map(str, triples_mask))))

            logger.info("target_example: {}".format(example.target))
            logger.info(
                "target_tokens: {}".format(
                    [x.replace("\u0120", "_") for x in target_tokens]
                )
            )
            # logger.info("target_ids: {}".format(" ".join(map(str, target_ids))))
            # logger.info("target_mask: {}".format(" ".join(map(str, target_mask))))

        features.append(
            InputFeatures(
                example_index,
                source_ids,
                triples_ids,
                target_ids,
                source_mask,
                triples_mask,
                target_mask,
            )
        )
    return features

def main():
    parser = argparse.ArgumentParser()

    ## Required parameters
    parser.add_argument(
        "--encoder_model_name_or_path",
        default=None,
        type=str,
        required=True,
        help="Path to pre-trained model: e.g. roberta-base",
    )
    parser.add_argument(
        "--decoder_model_name_or_path",
        default=None,
        type=str,
        required=True,
        help="Path to pre-trained model: e.g. roberta-base",
    )

    ## Other parameters
    parser.add_argument(
        "--load_model_checkpoint",
        default='Dynamic',
        type=str,
        choices=['Yes', 'No'],
        help="Should the model weights at load_model_path be loaded. Defaults to \"No\" in training and \"Yes\" in "
             "testing",
    )
    parser.add_argument(
        "--load_model_path",
        default="./output/checkpoint-best-bleu/pytorch_model.bin",
        type=str,
        help="Path to trained model: Should contain the .bin files",
    )
    parser.add_argument(
        "--model_type",
        default="bert",
        type=str,
        help="Model type: e.g. roberta",
    )
    parser.add_argument(
        "--model_architecture",
        default='bert2bert',
        type=str,
        help="Model architecture: e.g. bert2bert, bert2rnd",
    )
    parser.add_argument(
        "--output_dir",
        default="./output/",
        type=str,
        help="The output directory where the model predictions and checkpoints will be written.",
    )
    parser.add_argument(
        "--train_filename",
        default=None,
        type=str,
        help="The train filename. Should contain the .jsonl files for this task.",
    )
    parser.add_argument(
        "--dev_filename",
        default=None,
        type=str,
        help="The dev filename.",
    )
    parser.add_argument(
        "--test_filename",
        default=None,
        type=str,
        help="The test filename.",
    )
    parser.add_argument(
        "--predict_filename",
        default=None,
        type=str,
        help="The prediction filename.",
    )
    parser.add_argument(
        "--source",
        default="en",
        type=str,
        help="The source language (for file extension)",
    )
    parser.add_argument(
        "--target",
        default="sparql",
        type=str,
        help="The target language (for file extension)",
    )
    parser.add_argument(
        "--config_name",
        default="",
        type=str,
        help="Pretrained config name or path if not the same as model_name",
    )
    parser.add_argument(
        "--tokenizer_name",
        default="",
        type=str,
        help="Pretrained tokenizer name or path if not the same as model_name",
    )
    parser.add_argument(
        "--max_source_length",
        default=64,
        type=int,
        help="The maximum total source sequence length after tokenization. Sequences longer "
        "than this will be truncated, sequences shorter will be padded.",
    )
    parser.add_argument(
        "--max_triples_length",
        default=128,
        type=int,
        help="The maximum total triples sequence length after tokenization. Sequences longer "
             "than this will be truncated, sequences shorter will be padded.",
    )
    parser.add_argument(
        "--max_target_length",
        default=32,
        type=int,
        help="The maximum total target sequence length after tokenization. Sequences longer "
        "than this will be truncated, sequences shorter will be padded.",
    )

    parser.add_argument(
        "--do_train", action="store_true", help="Whether to run training."
    )
    parser.add_argument(
        "--do_eval", action="store_true", help="Whether to run eval on the dev set."
    )
    parser.add_argument(
        "--do_test", action="store_true", help="Whether to run test on the test set."
    )
    parser.add_argument(
        "--do_predict", action="store_true", help="Whether to run prediction on the predict set."
    )
    parser.add_argument(
        "--do_lower_case",
        action="store_true",
        help="Set this flag if you are using an uncased model.",
    )
    parser.add_argument(
        "--no_cuda", action="store_true", help="Avoid using CUDA when available"
    )

    parser.add_argument(
        "--train_batch_size",
        default=8,
        type=int,
        help="Batch size per GPU/CPU for training.",
    )
    parser.add_argument(
        "--eval_batch_size",
        default=8,
        type=int,
        help="Batch size per GPU/CPU for evaluation.",
    )
    parser.add_argument(
        "--gradient_accumulation_steps",
        type=int,
        default=1,
        help="Number of updates steps to accumulate before performing a backward/update pass.",
    )
    parser.add_argument(
        "--learning_rate",
        default=5e-5,
        type=float,
        help="The initial learning rate for Adam.",
    )
    parser.add_argument(
        "--beam_size", default=10, type=int, help="beam size for beam search"
    )
    parser.add_argument(
        "--weight_decay", default=0.0, type=float, help="Weight deay if we apply some."
    )
    parser.add_argument(
        "--adam_epsilon", default=1e-8, type=float, help="Epsilon for Adam optimizer."
    )
    parser.add_argument(
        "--max_grad_norm", default=1.0, type=float, help="Max gradient norm."
    )
    parser.add_argument(
        "--num_train_epochs",
        default=3,
        type=int,
        help="Total number of training epochs to perform.",
    )
    parser.add_argument(
        "--max_steps",
        default=-1,
        type=int,
        help="If > 0: set total number of training steps to perform. Override num_train_epochs.",
    )
    parser.add_argument("--eval_steps", default=-1, type=int, help="")
    parser.add_argument("--train_steps", default=-1, type=int, help="")
    parser.add_argument(
        "--warmup_steps", default=0, type=int, help="Linear warmup over warmup_steps."
    )
    parser.add_argument(
        "--local_rank",
        type=int,
        default=-1,
        help="For distributed training: local_rank",
    )
    parser.add_argument(
        "--seed", type=int, default=42, help="random seed for initialization"
    )
    parser.add_argument(
        "--save_inverval", type=int, default=1, help="save checkpoint every N epochs"
    )
    # print arguments
    args = parser.parse_args()
    logger.info(args)

    # Load models.
    config_class, model_class, tokenizer_class = MODEL_CLASSES[args.model_type]
    tokenizer = tokenizer_class.from_pretrained(
        args.tokenizer_name if args.tokenizer_name else args.encoder_model_name_or_path,
        do_lower_case=args.do_lower_case,
    )

    train_examples = read_examples(
        args.train_filename + "." + args.source,
        args.train_filename + ".triple",
        args.train_filename + "." + args.target,
    )
    train_features = convert_examples_to_features(
        train_examples, tokenizer, args, stage="train"
    )

if __name__ == "__main__":
    main()
