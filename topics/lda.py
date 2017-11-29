import warnings
warnings.filterwarnings(action='ignore', category=UserWarning, module='gensim')

import gensim
from gensim import utils
from indexer.indexer import Indexer
import json
import logging

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)


class LDA(object):

    def prepDataAndRun(self):
        indexer = Indexer()
        voca = indexer.get_voca()
        id2word = {}
        word2id = {}
        l = []
        for x in range(len(voca)):
            voca[x] = list(voca[x])
            if voca[x][0] == "content":
                term = voca[x][1].decode("utf-8")
                word2id[term] = x
                id2word[x] = term
                l.append(term)
        voca = l

        fp = open('bowcorpus.json', 'r')
        corpus = json.load(fp)
        bows = [bow for (id, bow) in corpus]
        idbows = []

        for bow in bows:
            idbow = [(word2id[word], freq) for word, freq in bow]
            idbows.append(idbow)
        LDA.build_lda_model(idbows, id2word)

    def build_lda_model(corpus, id2word):
        # gensim.corpora.Dictionary.from_corpus(corpus)
        gensim.corpora.MmCorpus.serialize('nips.mm', corpus, id2word=id2word)
        corpus = gensim.corpora.MmCorpus('nips.mm')


        dictionary = gensim.corpora.Dictionary.from_corpus(corpus, id2word)
        dictionary.save('nips.dict')

        filterdict = gensim.corpora.Dictionary.load('nips.dict')
        filterdict.filter_extremes(10, 0.5)
        filterdict.save('nipsFilter10.dict')
        old2new = {dictionary.token2id[token]: new_id for new_id, token in filterdict.iteritems()}
        vt = gensim.models.VocabTransform(old2new)
        gensim.corpora.MmCorpus.serialize('filtered_nips.mm', vt[corpus], id2word=filterdict)
        filtercorpus = gensim.corpora.MmCorpus('filtered_nips.mm')

        model = gensim.models.LdaModel(filtercorpus, id2word=filterdict, alpha='auto', num_topics=20, passes=10)
        model.save('ldaFilter10.lda')

        filterdict2 = gensim.corpora.Dictionary.load('nips.dict')
        filterdict2.filter_extremes(50, 0.5)
        filterdict.save('nipsFilter50.dict')
        old2new = {dictionary.token2id[token]: new_id for new_id, token in filterdict2.iteritems()}
        vt = gensim.models.VocabTransform(old2new)
        gensim.corpora.MmCorpus.serialize('filtered_nips2.mm', vt[corpus], id2word=filterdict)
        filtercorpus2 = gensim.corpora.MmCorpus('filtered_nips2.mm')

        model = gensim.models.LdaModel(filtercorpus2, id2word=filterdict2, alpha='auto', num_topics=20, passes=10)
        model.save('ldaFilter50.lda')


    def build_dtm_model(self):
        """
        Method using DtmModel in gensim
        :return:
        """

        corpus = gensim.corpora.MalletCorpus('nips.mallet')

        time_slices = [90, 93, 101, 127, 140, 143, 144, 150, 150, 151, 152, 152, 152, 158, 197, 198, 204, 207, 207, 207,
                       217, 250, 262, 292, 306, 360, 368, 403, 411, 567]

        ldaseq = gensim.models.LdaSeqModel(corpus=corpus, time_slice=time_slices, num_topics=15)
        ldaseq.save('nips.dtm')


    def generate_dtm(self):
        """
        Method for DTM using the C++ wrapper
        :return:
        """
        corpus = gensim.corpora.MalletCorpus('nips.mallet')

        # This .exe file contains a memory leak, try the one in libs/no-leak, only runnable on linux
        time_slices = [90, 93, 101, 127, 140, 143, 144, 150, 150, 151, 152, 152, 152, 158, 197, 198, 204, 207, 207, 207,
                       217, 250, 262, 292, 306, 360, 368, 403, 411, 567]

        model = gensim.models.wrappers.DtmModel('libs/dtm-win64.exe', corpus, time_slices=time_slices,
                                                num_topics=15, initialize_lda=True, id2word=corpus.id2word)
        topics = model.show_topics(num_topics=3, times=1, formatted=True)
        print(topics)
        model.save('nips.dtm')
