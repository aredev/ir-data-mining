import warnings
warnings.filterwarnings(action='ignore', category=UserWarning, module='gensim')

import gensim


class LDA(object):
    corpus = gensim.corpora.MalletCorpus('nips.mallet')
    print ('corpus done')
    #Build a model
    model = gensim.models.LdaModel(corpus, id2word=corpus.id2word, alpha='auto', num_topics=25)
    model.save('nips.lda')

    model = gensim.models.LdaModel.load('nips.lda')
    print(model.show_topics())
