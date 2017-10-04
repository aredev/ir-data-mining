# whoosh imports
###############################################
from whoosh.fields import Schema, TEXT, ID, STORED
from whoosh.index import create_in, exists_in, open_dir
from whoosh.qparser import QueryParser
from whoosh.scoring import WeightingModel
from whoosh.searching import Searcher
import gensim

import re
from math import sqrt
from math import log
#import matplotlib

import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
indexdir = 'index'

index = open_dir(indexdir)
reader = index.reader()

tfidf = gensim.models.TfidfModel.load('nips.tfidf_model')

print(tfidf.__getitem__(bow))

# corpus = gensim.corpora.MalletCorpus('nips.mallet')
#
# tfidf = gensim.models.TfidfModel(corpus)
# #print(tfidf[0])
# tfidf.save('nips.tfidf_model')

class Cosine(WeightingModel):
    """A cosine vector-space scoring algorithm, translated into Python
    from Terrier's Java implementation.
    """

    def score(self, searcher, fieldnum, text, docnum, weight, QTF=1):
        doc_tfidf_vector = self.get_doc_tfidf(docnum)#searcher.idf(fieldnum, text)
        query_tfidf_vector = self.get_query_tfidf(text)

        # DTW = (1.0 + log(weight)) * idf
        # QMF = 1.0  # TODO: Fix this
        # QTW = ((0.5 + (0.5 * QTF / QMF))) * idf
        return self.cosine(doc_tfidf_vector, query_tfidf_vector)

    def get_term_freq_query(query):
        terms = re.split("\s", query)
        term_freq = {}
        for t in terms:
            if t in term_freq:
                term_freq[t] += 1
            else:
                term_freq[t] = 1
        return term_freq

    def get_query_tfidf(self, query):
        term_freqs = self.get_term_freq_query(query)
        tfidf_dict = {}
        for t in term_freqs:
            tfidf_dict[t.key] = t.value * index.searcher.idf(t.key)
        return tfidf_dict

    # def get_term_freq_doc(docid):
    #     docnum = index.searcher.document_number(id=docid)  # searcher.document_number
    #     freq_generator = index.searcher.vector_as("frequency", docnum, "content")
    #     term_freq = {}
    #     for t in freq_generator:
    #         term_freq[t[0]] = t[1]
    #     return term_freq

    def get_doc_tfidf(docnum):
        bow = reader.vector_as('frequency', docnum, 'content')
        tfidf_vector = tfidf[bow]

        tfidf_dict = {}
        for word, score in tfidf_vector:
            tfidf_dict[word] = score
        return tfidf_dict

    def cosine(x, y):
        # always compare the longest document against the shortest
        if len(x) < len(y):
            a = x
            x = y
            y = a
            del a
        xsum = sum([k * k for k in x.values()])
        ysum = sum([k * k for k in y.values()])
        score = 0
        for word in x.iterkeys():
            if word not in y:
                continue
            score += x[word] * y[word]
        score = score / sqrt(xsum * ysum)
        print("cosine similarity: %.2f" % score)
        return score







