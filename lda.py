import warnings

import datetime

warnings.filterwarnings(action='ignore', category=UserWarning, module='gensim')

import gensim


class LDA(object):
    # corpus = gensim.corpora.MalletCorpus('nips.mallet')
    # print ('corpus done')
    # #Build a model
    # model = gensim.models.LdaModel(corpus, id2word=corpus.id2word, alpha='auto', num_topics=25)
    # model.save('nips.lda')
    #
    # model = gensim.models.LdaModel.load('nips.lda')
    # print(model.show_topics())

    def __init__(self) -> None:
        self.corpus = gensim.corpora.MalletCorpus('nips.corpus')
        self.lda_model = gensim.models.LdaModel.load('nips.lda')

    def get_topics_for_document(self, docId):
        doc_as_bow = self.corpus[int(docId)]
        document_topics = self.lda_model.get_document_topics(doc_as_bow)
        topics_by_id = sorted(document_topics, key=lambda tup: tup[1], reverse=True)

        topic_results = []

        for (topic_id, _) in topics_by_id:
            topic_name = self.lda_model.show_topic(topic_id)
            if topic_name not in topic_results:
                topic_results.append(topic_name)

        return topic_results
