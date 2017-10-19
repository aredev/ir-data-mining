
from whoosh.query import Query
from whoosh.searching import Searcher
from gensim import utils
from gensim.corpora.dictionary import Dictionary
import gensim




import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

class CosineSim():
    def __init__(self, searcher, q):
        self.query = q
        self.searcher = searcher
        # self.corpus = gensim.corpora.MalletCorpus('nips.corpus')
        self.corpus = gensim.corpora.malletcorpus.MalletCorpus('nips.mallet')
        gensim.corpora.MalletCorpus.serialize(fname='nips.corpus', corpus=self.corpus )
        # corpus.save('nips.malletcorpus')
        self.dict = Dictionary.load('nips.dict')
        print('corpus done')
        # self.tfidf = gensim.models.TfidfModel.load('nips.tfidf_model')

        # print(tfidf[[('the',1)]])

        self.tfidf = gensim.models.TfidfModel(self.corpus, id2word=self.corpus.id2word, dictionary=self.dict)
        # tfidf.save('nips.tfidf_model')

        print("test tfidf ", self.tfidf[[('the',1)]])
        self.query_tfidf_vector = self.get_query_tfidf(self.query)
        print("bla")

    def get_query_tfidf(self, query):
        term_freq = {}
        for token in query.all_tokens():
            t = token.text
            if t in term_freq:
                term_freq[t] += 1
            else:
                term_freq[t] = 1
        print(term_freq)
        for t in term_freq:
            print(t)
        array = []
        for t in term_freq:
            term = self.corpus.word2id[t]
            array.append((term, term_freq[t]))
        tfidf = self.tfidf[array]
        print('query tfidf:\n', tfidf)
        return tfidf

    def get_doc_tfidf(self, docnum, searcher):
        doc = self.corpus.docbyoffset(docnum)
        print (docnum, doc)
        #bow = Dictionary.doc2bow(doc)
        tfidf_vector = self.tfidf[doc]
        # tfidf_dict = {}
        # for word, score in tfidf_vector:
        #     tfidf_dict[word] = score
        # return tfidf_dict
        return tfidf_vector

    def similarity(self, docid):
        print("Computing score with " + str(self.query))

        doc_tfidf_vector = self.get_doc_tfidf(docid, self.searcher)  # searcher.idf(fieldnum, text)
        score = gensim.matutils.cossim(doc_tfidf_vector, self.query_tfidf_vector)
        #score = self.cosine(doc_tfidf_vector, self.query_tfidf_vector)
        print("score " + str(score))
        return score


    # def cosine(self, x, y):
    #     # always compare the longest document against the shortest
    #     if len(x) < len(y):
    #         a = x
    #         x = y
    #         y = a
    #         del a
    #     xsum = sum([k * k for k in x.values()])
    #     ysum = sum([k * k for k in y.values()])
    #     score = 0
    #     for word in x.iterkeys():
    #         if word not in y:
    #             continue
    #         score += x[word] * y[word]
    #     score = score / sqrt(xsum * ysum)
    #     print("cosine similarity: %.2f" % score)
    #     return score