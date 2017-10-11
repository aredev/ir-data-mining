import warnings
warnings.filterwarnings(action='ignore', category=UserWarning, module='gensim')

import gensim
import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)


class LDA(object):

    def build_lda_model(self):
        corpus = gensim.corpora.MalletCorpus('nips.mallet')

        dictionary = gensim.corpora.Dictionary.from_corpus(corpus, corpus.id2word)
        dictionary.filter_n_most_frequent(10)

        #Build a model
        model = gensim.models.LdaModel(corpus, id2word=corpus.id2word, alpha='auto', num_topics=13)
        model.save('nips.lda')

        model = gensim.models.LdaModel.load('nips.lda')
        print(model.show_topics())

    def generate_dtm(self):
        corpus = gensim.corpora.MalletCorpus('nips.mallet')

        model = gensim.models.wrappers.DtmModel('libs/dtm-win64.exe', corpus, [5, 8], num_topics=5, initialize_lda=True, id2word=corpus.id2word)
        topics = model.show_topics(num_topics=3, times=1, formatted=True)
        print(topics)