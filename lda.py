import warnings
warnings.filterwarnings(action='ignore', category=UserWarning, module='gensim')

import gensim
import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)


class LDA(object):

    def build_lda_model(self):
        corpus = gensim.corpora.MalletCorpus('nips.mallet')

        dictionary = gensim.corpora.Dictionary.from_corpus(corpus, corpus.id2word)

        #Build a model
        model = gensim.models.LdaModel(corpus, id2word=corpus.id2word, alpha='auto', num_topics=13)
        model.save('nips.lda')

        model = gensim.models.LdaModel.load('nips.lda')
        print(model.show_topics())


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
