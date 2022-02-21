"""Generator to generate a qtql dataset from a qtq dataset."""
import pickle
from typing import Dict

from KBQA.appB.labeling.qtql_dataset import QTQLDataset
from KBQA.appB.transformer_architectures.BERT_WordPiece_SPBERT.generator_utils import (
    get_label_for_uri,
)


class QTQLGenerator:
    """Generator to generate a qtql dataset from a qtq dataset.

    Parameters
    ----------
    qtq_path : str
        Path to a qtq dataset.
    """

    def __init__(self, qtq_path: str) -> None:
        self.qtql_dataset = QTQLDataset()
        self.qtql_dataset.load_qtq_dataset(qtq_path)

        self.label_store: Dict[str, str] = dict()
        with open("./store/uri_to_label.pickle", "wb") as handle:
            pickle.dump(self.label_store, handle, protocol=pickle.HIGHEST_PROTOCOL)

    def generate_qtql_dataset(self, dest_path: str) -> None:
        """Generate the qtql dataset and store it.

        Parameters
        ----------
        dest_path : str
            File, where is the qtql dataset is stored.
        """
        questions = self.qtql_dataset.questions

        for question in questions:
            labels = list()
            triples = question.triples

            print(question.text)

            for triple in triples:
                # read already found labels
                with open("./store/uri_to_label.pickle", "rb") as handle:
                    self.label_store = pickle.load(handle)

                uris = triple.split()

                labeled_triple = self._get_labels_for_triple(uris)

                labels.append(labeled_triple)

                with open("./store/uri_to_label.pickle", "wb") as handle:
                    pickle.dump(
                        self.label_store, handle, protocol=pickle.HIGHEST_PROTOCOL
                    )

            question.labels = labels

        self.qtql_dataset.save_qtql_dataset(dest_path)

    def _get_labels_for_triple(self, uris: str) -> str:
        """Find labels for a triple.

        A triple should be a list of 3 elements [subj, pred, obj].

        Parameters
        ----------
        uris : list
            List containing one triple.

        str
            Triple containing the labels from the given triple.
        """
        subj_uri = uris[0][1:-1]
        pred_uri = uris[1][1:-1]

        # distinguish between literals and resources
        if "^^" in uris[2]:
            obj_uri = uris[2].split("^^")[0][1:-1]
        else:
            obj_uri = uris[2][1:-1]

        # check for subject
        if subj_uri in self.label_store:
            subj = self.label_store[subj_uri]
        else:
            subj = get_label_for_uri(subj_uri)

            if subj == "":
                self.label_store[subj_uri] = subj_uri
                subj = subj_uri
            else:
                self.label_store[subj_uri] = subj

        # check for predicate
        if pred_uri in self.label_store:
            pred = self.label_store[pred_uri]
        else:
            pred = get_label_for_uri(pred_uri)

            if pred == "":
                self.label_store[pred_uri] = pred_uri
                pred = pred_uri
            else:
                self.label_store[pred_uri] = pred

        # check of object
        if obj_uri in self.label_store:
            obj = self.label_store[obj_uri]
        else:
            obj = get_label_for_uri(obj_uri)

            if obj == "":
                self.label_store[obj_uri] = obj_uri
                obj = obj_uri
            else:
                self.label_store[obj_uri] = obj

        return f"{subj} {pred} {obj}"


if __name__ == "__main__":
    QTQDATASETPATH = "./../../datasets/qtq-8-test-multilingual.json"

    qtql_generator = QTQLGenerator(QTQDATASETPATH)
    qtql_generator.generate_qtql_dataset(
        "./../../datasets/qtql-8-test-multilingual.json"
    )
