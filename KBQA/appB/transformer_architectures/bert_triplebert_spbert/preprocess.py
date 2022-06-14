import os
from KBQA.appB.preprocessing.labeling_preprocessor.labeling_preprocessor import preprocess_qtq_file


cwd = os.getcwd()

preprocess_qtq_file('data/qald-8-test.json', cwd+'/data/test_data')
