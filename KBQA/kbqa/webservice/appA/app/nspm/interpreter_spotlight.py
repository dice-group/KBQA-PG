import os
import pickle

import numpy as np
import spacy_dbpedia_spotlight
import tensorflow as tf

from app.nspm.generator_utils import decode, fix_URI
from app.nspm.nmt import Decoder, Encoder
from app.nspm.prepare_dataset import preprocess_sentence


def evaluate(sentence):
    attention_plot = np.zeros((max_length_targ, max_length_inp))

    sentence = preprocess_sentence(sentence)

    inputs = [inp_lang.word_index[i] for i in sentence.split(' ')]
    inputs = tf.keras.preprocessing.sequence.pad_sequences([inputs],
                                                           maxlen=max_length_inp,
                                                           padding='post')
    inputs = tf.convert_to_tensor(inputs)

    result = ''

    hidden = [tf.zeros((1, units))]
    enc_out, enc_hidden = encoder(inputs, hidden)

    dec_hidden = enc_hidden
    dec_input = tf.expand_dims([targ_lang.word_index['<start>']], 0)

    for t in range(max_length_targ):
        predictions, dec_hidden, attention_weights = decoder(dec_input,
                                                             dec_hidden,
                                                             enc_out)

        # storing the attention weights to plot later on
        attention_weights = tf.reshape(attention_weights, (-1, ))
        attention_plot[t] = attention_weights.numpy()

        predicted_id = tf.argmax(predictions[0]).numpy()

        result += targ_lang.index_word[predicted_id] + ' '

        if targ_lang.index_word[predicted_id] == '<end>':
            return result, sentence, attention_plot

        # the predicted ID is fed back into the model
        dec_input = tf.expand_dims([predicted_id], 0)

    return result, sentence, attention_plot


def mkdir_p(mypath):
    '''Creates a directory. equivalent to using mkdir -p on the command line'''

    from errno import EEXIST
    from os import makedirs, path

    try:
        makedirs(mypath)
    except OSError as exc:  # Python >2.5
        if exc.errno == EEXIST and path.isdir(mypath):
            pass
        else:
            raise


def translate(sentence):
    result, _, _ = evaluate(sentence)
    return result


def find_entity(sentence):
    nlp = spacy_dbpedia_spotlight.create('en')
    doc = nlp(sentence)
    placeholder = 65
    entities = dict()
    for ent in doc.ents:
        entities[chr(placeholder)] = (ent.text, ent.kb_id_)
        placeholder += 1
    # return [(ent.text, ent.kb_id_, ent._.dbpedia_raw_result['@similarityScore']) for ent in doc.ents]
    return entities


def replace_entities(sentence, entities):
    for placeholder, (entity, _) in entities.items():
        if entity in sentence:
            sentence = sentence.replace(entity, placeholder)
    return sentence


def fix_start_end(sparql):
    sparql = sparql.replace('<start>', '')
    sparql = sparql.replace('<end>', '')
    return sparql


def restore_entity(sparql, entities):
    sparql = fix_start_end(sparql)
    for placeholder, (_, uri) in entities.items():
        if placeholder + ' ' in sparql or placeholder + '}' in sparql:
            sparql = sparql.replace(placeholder + ' ', '<' + uri + '> ')
            sparql = sparql.replace(placeholder + '}', '<' + uri + '>}')
    return sparql


def process_question(question):
    global max_length_targ, max_length_inp, encoder, decoder, inp_lang, units, targ_lang

    model_dir = os.path.dirname(__file__) + '../../../../../resources'
    input_dir = os.path.dirname(__file__) + '../../../../../resources'

    model_dir += '/training_checkpoints'
    pic_dir = input_dir + '/pickle_objects'

    embedding_dim = 256
    units = 1024

    with open(pic_dir + '/input_tensor.pickle', 'rb') as f:
        input_tensor = pickle.load(f)
    with open(pic_dir + '/target_tensor.pickle', 'rb') as f:
        target_tensor = pickle.load(f)
    with open(pic_dir + '/inp_lang.pickle', 'rb') as f:
        inp_lang = pickle.load(f)
    with open(pic_dir + '/targ_lang.pickle', 'rb') as f:
        targ_lang = pickle.load(f)
    with open(pic_dir + '/BATCH_SIZE.pickle', 'rb') as f:
        BATCH_SIZE = pickle.load(f)

    # Calculate max_length of the target tensors
    max_length_targ, max_length_inp = target_tensor.shape[1], input_tensor.shape[1]

    vocab_inp_size = len(inp_lang.word_index) + 1
    vocab_tar_size = len(targ_lang.word_index) + 1

    encoder = Encoder(vocab_inp_size, embedding_dim, units, BATCH_SIZE)
    decoder = Decoder(vocab_tar_size, embedding_dim, units, BATCH_SIZE)

    optimizer = tf.keras.optimizers.Adam()
    checkpoint = tf.train.Checkpoint(optimizer=optimizer,
                                     encoder=encoder,
                                     decoder=decoder)

    checkpoint.restore(tf.train.latest_checkpoint(model_dir))

    entities = find_entity(question)
    question_ph = replace_entities(question, entities)

    finaltrans = "input qurey: \n"
    finaltrans += question

    finaltrans += "\n\n\ninput query with placeholder:\n"
    finaltrans += question_ph

    finaltrans += "\n\n\nentities:\n"
    for placeholder, (entity, uri) in entities.items():
        finaltrans += "{},  {},  {}".format(placeholder, entity, uri)

    finaltrans += "\n\n\noutput qurey:\n"
    finaltranso = translate(question_ph)
    finaltrans += finaltranso

    finaltrans += '\n\n\noutput query with placeholder decoded:\n'
    finaltranso = decode(finaltranso)
    finaltranso = fix_URI(finaltranso)
    finaltrans += finaltranso

    finaltrans += '\n\n\noutput query with entities:\n'
    finaltranso = restore_entity(finaltranso, entities)
    finaltranso = finaltranso.replace("OFFSET", "")
    finaltranso = finaltranso.replace("LIMIT", "")
    finaltrans += finaltranso

    print(finaltrans)

    return finaltranso
