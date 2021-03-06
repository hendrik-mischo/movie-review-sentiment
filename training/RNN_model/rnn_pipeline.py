import numpy as np
import pandas as pd
import string
from bs4 import BeautifulSoup

from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer

import tensorflow as tf
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import load_model

import pickle
from joblib import dump, load

from models.RNN.transformers import TextToSequence, RemoveHTML


#if __name__ == '__main__':

with open('../../models/RNN/tokenizer.pickle', 'rb') as handle:
    tokenizer = pickle.load(handle)

print('Building pipeline ...')

# Preprocessing Functions

def RemoveHTML(text):
    text = BeautifulSoup(text, "html.parser").get_text()
    return text

def TextToSequence(text):
    # loading
    text = pd.Series(text)
    text = pad_sequences(tokenizer.texts_to_sequences((pd.Series(text))),maxlen=500)
    return text


# Creating Transformation Functions

remove_html = FunctionTransformer(RemoveHTML, validate=False)
text_to_seq = FunctionTransformer(TextToSequence, validate=False)


# Pipeline

text_transformer = Pipeline(
    [
        ('remove_html', remove_html),
        ('text_to_seq', text_to_seq)
    ], verbose=True)

# save transformer
dump(text_transformer, filename="../../models/RNN/text_transformer.joblib")

print('text_transformer saved ...')


# demo
print('run demo ...')

# load model
model = load_model("rnn_model.h5")

# load text_transformer
#text_transformer = load("text_transformer.joblib")

text = 'awesome movie, but somehwere I got lost'

sequence = text_transformer.transform(text)

pred = model.predict(sequence)

print(pred)
