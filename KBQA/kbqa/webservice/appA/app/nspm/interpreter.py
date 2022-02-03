import sys

import tensorflow as tf
import argparse

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

import numpy as np
import pickle
from app.nspm.prepare_dataset import preprocess_sentence
from app.nspm.nmt import Encoder,Decoder
from app.nspm.generator_utils import decode, fix_URI

from airML import airML
import json
from numpy import random as np_random
import gensim
from gensim.models.fasttext import FastText

def evaluate(sentence):
  attention_plot = np.zeros((max_length_targ, max_length_inp))

  sentence = preprocess_sentence(sentence)
  
  # data_en = [i for i in sentence.split(' ') if i not in w2v_model.wv.vocab]

  # if len(data_en) > 0:

  #   print('New word',data_en)

  #   # print('Before', len(w2v_model.wv.vocab))

  #   # old_vector = w2v_model.wv[data_en[0]]

  #   w2v_model.build_vocab(sentences=[data_en], update=True)
  #   w2v_model.train(sentences=[data_en], total_examples=len(data_en), epochs=100)

  #   # print('After ',len(w2v_model.wv.vocab))
    
  #   # new_vector = w2v_model.wv[data_en[0]]

  #   # print('close? ',np.allclose(old_vector, new_vector, atol=1e-4))

  #   # print('In Vocabulary?',data_en[0] in w2v_model.wv.vocab)

  #   inputs = [w2v_model.wv.vocab[i].index for i in sentence.split(' ')]

  # else:  
  try:  
    inputs = [w2v_model.wv.vocab[i].index for i in sentence.split(' ')]
    # inputs = [inp_lang.word_index[i] for i in sentence.split(' ')]
    # inputs = [w2v_model.vocab[i].index for i in sentence.split(' ')]
    inputs = tf.keras.preprocessing.sequence.pad_sequences([inputs],
                                                          maxlen=max_length_inp,
                                                          padding='post')


    inputs = tf.convert_to_tensor(inputs)

    result = ''

    hidden = [tf.zeros((1, units))]
    enc_out, enc_hidden = encoder(inputs, hidden)

    dec_hidden = enc_hidden
    # dec_input = tf.expand_dims([targ_lang.word_index['<start>']], 0)
    dec_input = tf.expand_dims([w2v_model_spql.wv.vocab['<start>'].index], 0)

    for t in range(max_length_targ):
      predictions, dec_hidden, attention_weights = decoder(dec_input,
                                                          dec_hidden,
                                                          enc_out)

      # storing the attention weights to plot later on
      attention_weights = tf.reshape(attention_weights, (-1, ))
      attention_plot[t] = attention_weights.numpy()

      predicted_id = tf.argmax(predictions[0]).numpy()

      # result += targ_lang.index_word[predicted_id] + ' '
      result += w2v_model_spql.wv.index2word[predicted_id] + ' '

      # if targ_lang.index_word[predicted_id] == '<end>':
      if w2v_model_spql.wv.index2word[predicted_id] == '<end>':
        return result, sentence, attention_plot

      # the predicted ID is fed back into the model
      dec_input = tf.expand_dims([predicted_id], 0)
  except KeyError:
    result = ""
  return result, sentence, attention_plot

def mkdir_p(mypath):
    '''Creates a directory. equivalent to using mkdir -p on the command line'''

    from errno import EEXIST
    from os import makedirs,path

    try:
        makedirs(mypath)
    except OSError as exc: # Python >2.5
        if exc.errno == EEXIST and path.isdir(mypath):
            pass
        else: raise

def plot_attention(attention, sentence, predicted_sentence,ou_dir):
  fig = plt.figure(figsize=(10,10))
  ax = fig.add_subplot(1, 1, 1)
  ax.matshow(attention, cmap='viridis')

  fontdict = {'fontsize': 14}

  ax.set_xticklabels([''] + sentence, fontdict=fontdict, rotation=90)
  ax.set_yticklabels([''] + predicted_sentence, fontdict=fontdict)

  ax.xaxis.set_major_locator(ticker.MultipleLocator(1))
  ax.yaxis.set_major_locator(ticker.MultipleLocator(1))

  plt.show()
  fig = plt.figure()
  mkdir_p(ou_dir)
  fig.savefig('{}/graph.png'.format(ou_dir))


def translate(sentence):
  result, sentence, attention_plot = evaluate(sentence)

  print('Input: %s' % (sentence))
  print('Predicted translation: {}'.format(result))

  attention_plot = attention_plot[:len(result.split(' ')), :len(sentence.split(' '))]
#   plot_attention(attention_plot, sentence.split(' '), result.split(' '),ou_dir) #modified to disable plotting
  return result


def install_model(url):
    output = airML.install(url, format='nspm')
    output = json.loads(output)
    if output['status_code'] == 200:
        print(output['message'])
    else:
        raise Exception(output['message'])


def locate_model(url):
    install_model(url)
    output = airML.locate(url, format='nspm')
    output = json.loads(output)
    if output['status_code'] == 200:
        print(output['message'])
        model_dir = output['results'][0]
        return model_dir
    else:
        raise Exception(output['message'])

def process_question(question):

    inputs = question

    finaltrans = "input qurey : \n"
    finaltrans += inputs
    finaltrans += "\n \n \n output qurey : \n"
    finaltranso = translate(inputs)
    finaltrans += finaltranso
    finaltrans += '\n \n \n output query decoded : \n'
    finaltranso = decode(finaltranso)
    finaltranso = fix_URI(finaltranso)
    # print('Decoded translation: {}'.format(finaltranso))
    finaltrans += finaltranso
    # outputfile = open((input_dir+'/output_query.txt'),'w',encoding="utf8")
    # outputfile.writelines([finaltrans])
    # outputfile.close()
    print(finaltrans)
    return(finaltranso.split('<end>')[0])

def load_model():
    global max_length_targ,max_length_inp,encoder,decoder,units,w2v_model,w2v_model_spql, checkpoint

    model_dir = 'data/new_qald8'
    input_dir = 'data/new_qald8'

    model_dir += '/training_checkpoints'
    pic_dir = input_dir + '/pickle_objects'

    # print(model_dir)
    embedding_dim = 300
    units = 1024

    global w2v_model, w2v_model_spql
    w2v_model = FastText.load(pic_dir+'/model_nl.model')
    w2v_model_spql = FastText.load(pic_dir+'/model_spql.model')

    # with open(pic_dir+'/BATCH_SIZE.pickle', 'rb') as f:
    #     BATCH_SIZE=pickle.load(f)
    with open(pic_dir+'/embedding_matrix.pickle', 'rb') as f:
      embedding_matrix=pickle.load(f)
    with open(pic_dir+'/embedding_matrix_spql.pickle', 'rb') as f:
      embedding_matrix_spql=pickle.load(f)
    with open(pic_dir+'/input_tensor.pickle', 'rb') as f:
      input_tensor=pickle.load(f)
    with open(pic_dir+'/target_tensor.pickle', 'rb') as f:
      target_tensor=pickle.load(f)

    # Calculate max_length of the target tensors'
    max_length_targ = input_tensor.shape[1]
    # print('max_length_targ', max_length_targ)
    max_length_inp = target_tensor.shape[1]

    BATCH_SIZE = 32

    vocab_inp_size = len(embedding_matrix)
    vocab_tar_size = len(embedding_matrix_spql)

    encoder = Encoder(vocab_inp_size, embedding_dim, units, BATCH_SIZE,embedding_matrix)
    decoder = Decoder(vocab_tar_size, embedding_dim, units, BATCH_SIZE,embedding_matrix_spql)

    optimizer = tf.keras.optimizers.Adam()
    checkpoint = tf.train.Checkpoint(optimizer=optimizer,
                                 encoder=encoder,
                                 decoder=decoder)

    checkpoint.restore(tf.train.latest_checkpoint(model_dir)).expect_partial()

load_model()