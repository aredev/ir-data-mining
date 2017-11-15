import pickle
from ptm import AuthorTopicModel
import csv
import logging
import random

import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from ptm.utils import get_top_words

with open('data_atm/corpus.pkl', 'rb') as f:
    corpus = pickle.load(f)

"""doc_author.pkl is not a 2D list[papers][authors]?  (1240 did not work with 1241)"""
with open('data_atm/doc_author.pkl', 'rb') as f:
    doc_author = pickle.load(f)

"""voca is a list of words"""
with open('data_atm/voca_atm.pkl', 'rb') as f:
    voca = pickle.load(f)
    print(voca)


with open('data/authors.csv', 'r') as f:
    reader = csv.reader(f)
    next(reader)
    author = list(reader)

author.append(['N/A', 'N/A'])

for doc in range(len(doc_author)):
    if doc_author[doc] == []:
        doc_author[doc] = [len(author) - 1]

n_doc = len(corpus)
n_voca = len(voca)
# n_topic = 30
n_author = len(author)
max_iter = 30

print("data preparation completed")
subset = 2000
n_topics = [20, 25, 30, 35, 40, 45, 50]
eval_list = []



"""
for n_topic in n_topics:
    try:
        with open('data_atm/finalized_model.sav', 'rb') as f:
            model = pickle.load(open("data_atm/finalized_model.sav", 'rb'))
        print("MODEL ALREADY PRESENT")
    except:
        print("CREATE MODEL")
        model = AuthorTopicModel(subset, n_voca, n_topic, n_author)
        print("FIT MODEL")
        model.fit(corpus[0:subset], doc_author, max_iter=max_iter)
        # print("SAVE MODEL")

        # filename = 'data_atm/finalized_model.sav'
        # pickle.dump(model, open(filename, 'wb'))
        eval_list.append([n_topic, model.log_likelihood()])
        print(eval_list)
        with open('data_atm/eval_list.pkl', 'wb') as f:
            pickle.dump(eval_list, f)


        #
        # try:
        #     with open('data_atm/score_list.pkl', 'rb') as f:
        #         score_list = pickle.load(f)
        #     print("SCORE_LIST ALREADY PRESENT")
        # except:
        #     score_list = []
        #
        #     for x in range(n_author):
        #         score_list.append(list(model.AT[x]))
        #
        #     with open('data_atm/score_list.pkl', 'wb') as f:
        #         pickle.dump(score_list, f)
        #
        #
        # for k in range(n_topic):
        #     top_words = get_top_words(model.TW, voca, k, 30)
        #     print('topic ', k , ','.join(top_words))
"""
