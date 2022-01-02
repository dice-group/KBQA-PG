# QALD Dataset: Question, SPARQL, Answer

# summarizer(QALD Dataset):
#   --> [KB Triples]


# generator(QALD Dataset, summarizer):
#  --> ^


# Dataset
#     readData(file)

# SummarizerABC
#     summarize(question)

#     summarize(questions[])

# Generator
#     generate(Dataset, Summarizer)

import os

from dataset import Dataset
from nes import NES
from summarizer import Summarizer


def generateTriples(dataset: Dataset, summarizer: Summarizer):
    triples = []

    for quesiton in dataset.questions:
        t = summarizer.summarize(question.text)
        question.triples.append(t)

cwd = os.getcwd()
print(cwd)

dataset = Dataset()
dataset.load_dataset("KBQA/data-generator/qald-9-train-multilingual.json")
summarizer = NES()
generateTriples(dataset, summarizer)
