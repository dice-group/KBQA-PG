import os
from KBQA.appB.preprocessing.basic_preprocessor.basic_preprocessor import preprocess_qtq_file, preprocess_triples_file


cwd = os.getcwd()

preprocess_qtq_file('data_files/qtq-updated-qald-8-9-merged-train-multilingual.json', cwd+'/data_files')
preprocess_triples_file('data_files/qtq-updated-qald-8-9-merged-train-multilingual.triple')
