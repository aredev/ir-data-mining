# whoosh imports
###############################################
import re
from math import sqrt

import gensim
from whoosh.scoring import WeightingModel, BaseScorer


#import matplotlib


# corpus = gensim.corpora.MalletCorpus('nips.mallet')
#
# tfidf = gensim.models.TfidfModel(corpus)
# #print(tfidf[0])
# tfidf.save('nips.tfidf_model')

class CosineWeighter(WeightingModel):
    """A cosine vector-space scoring algorithm, translated into Python
    from Terrier's Java implementation.
    """

    def scorer(self, searcher, fieldname, text, qf=1):
        pass


class CosineScorer(BaseScorer):

    def score(self, matcher):
        return _score(searcher, fieldname, text, docnum)

    def _score(self, searcher, fieldname, text, docnum): #docnum
        print("Computing score with " + self.query)
        doc_tfidf_vector = self.get_doc_tfidf(docnum, searcher)  # searcher.idf(fieldnum, text)
        query_tfidf_vector = self.get_query_tfidf(text)
        score = self.cosine(doc_tfidf_vector, query_tfidf_vector)
        print("score " + str(score))
        return score

    def __init__(self, query):
        self.query = query
        print(query)

    def __index__(self):
        self.tfidf = gensim.models.TfidfModel.load('nips.tfidf_model')

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

    def get_doc_tfidf(self, docnum, searcher):
        bow = searcher.vector_as('frequency', docnum, 'content')
        tfidf_vector = self.tfidf[bow]
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







