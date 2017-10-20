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
        self.corpus = gensim.corpora.MalletCorpus('nips4topic.corpus')
        self.lda_model = gensim.models.LdaModel.load('nips.lda')

    # TODO: set bounds on nr_topics, nr_topic_words to prevent out of bound exceptions.
    # TODO: use lemmatization to remove duplicate words.
    def get_topics_for_document(self, docId, nr_topics=3, nr_topic_words=5):
        document_topics = self.lda_model.get_document_topics(self.corpus[int(docId)])
        topics_by_id = sorted(document_topics, key=lambda tup: tup[1], reverse=True)
        topic_results = []

        # Show the the top <nr_topic_words> words of the best <nr_topics> topics.
        nr_topics = min([nr_topics, len(topics_by_id)])

        for (topic_id, _) in topics_by_id[:nr_topics]:
            top_words = self.lda_model.show_topic(topic_id)
            max_topics = min([nr_topic_words, len(top_words)])
            top_words = [word for (word, _) in top_words[:max_topics]]
            topic_results.append(top_words)
        return topic_results
