import argparse
import tensorflow as tf
import numpy as np
import os
import pickle
import time
from nmt import Encoder,Decoder,loss_function,BahdanauAttention
from sklearn.model_selection import train_test_split
from prepare_dataset import load_dataset,merging_datafile




@tf.function
def train_step(inp, targ, enc_hidden):
  loss = 0

  with tf.GradientTape() as tape:
    enc_output, enc_hidden = encoder(inp, enc_hidden)

    dec_hidden = enc_hidden

    dec_input = tf.expand_dims([model_spql.wv.vocab['<start>'].index] * BATCH_SIZE, 1)

    # Teacher forcing - feeding the target as the next input
    for t in range(1, targ.shape[1]):
      # passing enc_output to the decoder
      predictions, dec_hidden, _ = decoder(dec_input, dec_hidden, enc_output)

      loss += loss_function(targ[:, t], predictions)

      # using teacher forcing
      dec_input = tf.expand_dims(targ[:, t], 1)

  batch_loss = (loss / int(targ.shape[1]))

  variables = encoder.trainable_variables + decoder.trainable_variables

  gradients = tape.gradient(loss, variables)

  optimizer.apply_gradients(zip(gradients, variables))

  return batch_loss

def train(epochs,dir):
    model_dir = dir
    given_dir = model_dir+'/training_log.txt'
    model_dir+='/training_checkpoints'

    checkpoint_prefix = os.path.join(model_dir, "ckpt")
    EPOCHS = epochs
    train_l=[]


    for epoch in range(EPOCHS):
        empty_s=" "
        start = time.time()

        enc_hidden = encoder.initialize_hidden_state()
        total_loss = 0

        for (batch, (inp, targ)) in enumerate(dataset.take(steps_per_epoch)):
            batch_loss = train_step(inp, targ, enc_hidden)
            total_loss += batch_loss

            if batch % 100 == 0:
                print('Epoch {} Batch {} Loss {:.4f}'.format(epoch + 1,
                                                            batch,
                                                            batch_loss.numpy()))
        # saving (checkpoint) the model every 2 epochs
        if (epoch + 1) % 2 == 0:
            checkpoint.save(file_prefix = checkpoint_prefix)

        print('Epoch {} Loss {:.4f} \n'.format(epoch + 1,
                                            total_loss / steps_per_epoch))
        empty_s='Epoch {} Loss {:.4f} \n'.format(epoch + 1,
                                            total_loss / steps_per_epoch)
        print('Time taken for 1 epoch {} sec\n'.format(time.time() - start))
        empty_s+='Time taken for 1 epoch {} sec\n'.format(time.time() - start)
        train_l.append(empty_s)
    filelog = open(given_dir,'w',encoding="utf8")
    filelog.writelines(train_l)
    filelog.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    # requiredNamed = parser.add_argument_group('required named arguments')
    # requiredNamed.add_argument(
    #     '--input', dest='input', metavar='inputDirectory', help='dataset directory', required=False)
    # requiredNamed.add_argument(
    #     '--output', dest='output', metavar='outputDirectory', help='dataset directory', required=False)
    # requiredNamed.add_argument(
    #         '--batch-size', dest='BatchSize', help='Input Batch Size for dataset according to data size', required=False)
    # requiredNamed.add_argument(
    #         '--epochs', dest='Epochs', help='Input string for translation', required=False)
    args = parser.parse_args()
    args.input = 'data/qald8'
    args.output = 'data/qald8'
    args.BatchSize = 5
    args.Epochs = 5
    input_dir = args.input
    output_dir = args.output
    BATCH_SIZE = int(args.BatchSize)
    Epoc=int(args.Epochs)
    output_direc = merging_datafile(input_dir,output_dir)
    pic_dir=input_dir+'/pickle_objects'
    os.mkdir(pic_dir)

    num_examples = None
    input_tensor, target_tensor, model_nl, model_spql = load_dataset(output_direc, num_examples)
    max_length_targ, max_length_inp = target_tensor.shape[1], input_tensor.shape[1]
    input_tensor_train, input_tensor_val, target_tensor_train, target_tensor_val = train_test_split(input_tensor, target_tensor, test_size=0.2)

    BUFFER_SIZE = len(input_tensor_train)
    steps_per_epoch = len(input_tensor_train)//BATCH_SIZE
    embedding_dim = 300
    units = 1024
    vocab_inp_size = len(model_nl.wv.vocab)+1
    vocab_tar_size = len(model_spql.wv.vocab)+1

    dataset = tf.data.Dataset.from_tensor_slices((input_tensor_train, target_tensor_train)).shuffle(BUFFER_SIZE)
    dataset = dataset.batch(BATCH_SIZE, drop_remainder=True)
    example_input_batch, example_target_batch = next(iter(dataset))

    embedding_matrix = np.zeros((vocab_inp_size, 300))
    for word, i in model_nl.wv.vocab.items():
        embedding_matrix[model_nl.wv.vocab[word].index] = model_nl.wv.get_vector(word)

    embedding_matrix_spql = np.zeros((vocab_tar_size, 300))
    for word, i in model_spql.wv.vocab.items():
        embedding_matrix_spql[model_spql.wv.vocab[word].index] = model_spql.wv.get_vector(word)

    with open(pic_dir+'/embedding_matrix.pickle', 'wb') as f:
        pickle.dump(embedding_matrix, f)
    with open(pic_dir+'/embedding_matrix_spql.pickle', 'wb') as f:
        pickle.dump(embedding_matrix_spql, f)
    with open(pic_dir+'/model_nl.pickle', 'wb') as f:
        pickle.dump(model_nl, f)
    with open(pic_dir+'/model_spql.pickle', 'wb') as f:
        pickle.dump(model_spql, f)
    with open(pic_dir+'/input_tensor.pickle', 'wb') as f:
        pickle.dump(input_tensor, f)
    with open(pic_dir+'/target_tensor.pickle', 'wb') as f:
        pickle.dump(target_tensor, f)
    with open(pic_dir+'/BATCH_SIZE.pickle', 'wb') as f:
        pickle.dump(BATCH_SIZE, f)

    encoder = Encoder(vocab_inp_size, embedding_dim, units, BATCH_SIZE,embedding_matrix)
    decoder = Decoder(vocab_tar_size, embedding_dim, units, BATCH_SIZE,embedding_matrix_spql)
    attention_layer = BahdanauAttention(10)
    sample_hidden = encoder.initialize_hidden_state()
    sample_output, sample_hidden = encoder(example_input_batch, sample_hidden)
    attention_result, attention_weights = attention_layer(sample_hidden, sample_output)

    optimizer = tf.keras.optimizers.Adam()
    checkpoint = tf.train.Checkpoint(optimizer=optimizer,
                                 encoder=encoder,
                                 decoder=decoder)


    train(Epoc,input_dir)