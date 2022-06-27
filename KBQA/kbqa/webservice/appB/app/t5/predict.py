"""File to perfrom prediction using t5 module."""

from __future__ import absolute_import
import argparse

import os
import re
import sys
import logging

from transformers import pipeline
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(name)s -   %(message)s",
    datefmt="%m/%d/%Y %H:%M:%S",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


parser = argparse.ArgumentParser()

parser.add_argument(
    "--model_checkpoint",
    default= None,
    type=str,
    help="Should the model weights at load_model_path be loaded.",
)
parser.add_argument(
    "--output_dir",
    default="./output/",
    type=str,
    help="The output directory where the model predictions and checkpoints will be written.",
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


def init(args):
    """Intialize model."""
    model_checkpoint = args.model_checkpoint

    model = AutoModelForSeq2SeqLM.from_pretrained(model_checkpoint)
    tokenizer = AutoTokenizer.from_pretrained(model_checkpoint)
    if os.path.exists(args.output_dir) is False:
        os.makedirs(args.output_dir)



def run(args):
    """Run and predict."""
    if os.path.exists(args.output_dir) is False:
        os.makedirs(args.output_dir)
    model_checkpoint = args.model_checkpoint

    model = AutoModelForSeq2SeqLM.from_pretrained(model_checkpoint)
    tokenizer = AutoTokenizer.from_pretrained(model_checkpoint)
    translator = pipeline(
        "translation_xx_to_yy",
        model=model,
        tokenizer=tokenizer
    )
    translate= lambda q: (translator(q, max_length=100)[0]['translation_text'])


    files = []
    if args.predict_filename is not None:
        files.append(args.predict_filename)
    for idx, file in enumerate(files):
        logger.info("Predict file: {}".format(file))
        ques_file = file + "." + args.source
        with open(ques_file, encoding="utf-8") as source_f:
            questions = source_f.read().splitlines()
        preds = []
        for ques in questions:        
            #text to sparql traanslation example
            answer = translate(ques)
            preds.append(answer)
        print(preds)
        pred_str = []
        with open(
                os.path.join(args.output_dir, "predict_{}.output".format(str(idx))), "w", encoding="utf-8"
        ) as f:
            count = 0
            for ref, count in enumerate(pred_str):
                ref = ref.strip().replace("< ", "<").replace(" >", ">")
                ref = re.sub(r' ?([!"#$%&\'(’)*+,-./:;=?@\\^_`{|}~]) ?', r"\1", ref)
                ref = ref.replace("attr_close>", "attr_close >").replace(
                    "_attr_open", "_ attr_open"
                )
                ref = ref.replace(" [ ", " [").replace(" ] ", "] ")
                ref = ref.replace("_obd_", " _obd_ ").replace("_oba_", " _oba_ ")

                pred_str.append(ref.split())
                line = count + "\t" + ref    #modified
                f.write(line + "\n")    # modified
                count += 1
        logger.info("  " + "*" * 20)

if __name__ == "__main__":
    run()