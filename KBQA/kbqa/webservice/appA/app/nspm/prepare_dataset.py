import tensorflow as tf

import unicodedata
import re
import io
from gensim.models.fasttext import FastText

def unicode_to_ascii(s):
  return ''.join(c for c in unicodedata.normalize('NFD', s)
      if unicodedata.category(c) != 'Mn')


def preprocess_sentence(w):
  w = unicode_to_ascii(w.strip())

  # creating a space between a word and the punctuation following it
  # eg: "he is a boy." => "he is a boy ."
  # Reference:- https://stackoverflow.com/questions/3645931/python-padding-punctuation-with-white-spaces-keeping-punctuation
  w = re.sub(r"([?.!,¿])", r" \1 ", w)
  w = re.sub(r'[" "]+', " ", w)

  # replacing everything with space except (a-z, A-Z, ".", "?", "!", ",")
  w = re.sub(r"[^a-zA-Z?.!,¿_]+", " ", w)

  w = w.strip()

  # adding a start and an end token to the sentence
  # so that the model know when to start and stop predicting.
  w = '<start> ' + w + ' <end>'
  return w

def create_dataset(path, num_examples):
  lines = io.open(path, encoding='UTF-8').read().strip().split('\n')

  word_pairs = [[preprocess_sentence(w) for w in l.split('\t')]  for l in lines[:num_examples]]

  return zip(*word_pairs)

def tokenize(lang):
  lang_tokenizer = tf.keras.preprocessing.text.Tokenizer(
      filters='',lower=False)
  lang_tokenizer.fit_on_texts(lang)

  tensor = lang_tokenizer.texts_to_sequences(lang)

  tensor = tf.keras.preprocessing.sequence.pad_sequences(tensor,
                                                         padding='post')

  return tensor, lang_tokenizer

def word_embedding(lang,model):
  data_en = [i.split() for i in lang]
  data = []
  tensor = []
  for j in data_en:
    data = [model.wv.vocab[i].index for i in j]
    tensor.append(data)
  tensor = tf.keras.preprocessing.sequence.pad_sequences(tensor,
                                                          padding='post',
                                                          dtype='float32')
  return tensor

def load_dataset(path, num_examples=None):
  # creating cleaned input, output pairs

    print('Inside Load Dataset')
    
    inp_lang, targ_lang  = create_dataset(path, num_examples)

    data_en = [text.split() for text in inp_lang] 

    data_spql = [text.split() for text in targ_lang]

    model_nl = FastText(size=300, window=2, min_count=1,min_n=3)

    model_spql = FastText(size=300, window=2, min_count=1,min_n=3)

    model_nl.build_vocab(data_en)

    model_spql.build_vocab(data_spql)
    
    print('Starting Word Embedding for Natural language and Length of the Vocabulary is ',len(model_nl.wv.vocab))
    
    model_nl.train(data_en,total_examples=len(data_en),epochs=5)  
    
    print('Starting Word Embedding for SPARQL and Length of the Vocabulary is ',len(model_spql.wv.vocab))

    model_spql.train(data_spql,total_examples=len(data_spql),epochs=5)
    
    print('Training Completed !!!')

    input_tensor = word_embedding(inp_lang,model_nl)

    target_tensor = word_embedding(targ_lang,model_spql)

  # input_tensor, inp_lang_tokenizer = tokenize(inp_lang)
  # target_tensor, targ_lang_tokenizer = tokenize(targ_lang)

    return input_tensor, target_tensor, model_nl, model_spql

def convert(lang, tensor):
  for t in tensor:
    if t!=0:
      print ("%d ----> %s" % (t, lang.index_word[t]))

def merging_datafile(input_dir,output_dir):
    input_diren=input_dir+'/data.en'
    input_dirspq=input_dir+'/data.sparql'
    output_dir+='/data.txt'
    file1 = open(input_diren,'r',encoding="utf8")
    Lines1 = file1.readlines()
    file2 = open(input_dirspq,'r',encoding="utf8")
    Lines2 = file2.readlines()
    s=[]
    for i in range(len(Lines1)):
        s.append(Lines1[i].replace('\n'," ")+"\t "+Lines2[i])

    filef = open(output_dir,'w',encoding="utf8")
    filef.writelines(s)
    file1.close()
    file2.close()
    filef.close()
    return output_dir