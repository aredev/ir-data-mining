import warnings

warnings.filterwarnings(action='ignore', category=UserWarning, module='gensim')

import gensim
from nltk.stem import WordNetLemmatizer
from indexer.database.db_handler import DbHandler


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
        self.docIds = []
        self.path = "data/lda"
        self.db_handler = DbHandler()
        self.corpus = gensim.corpora.MalletCorpus(self.path + '/nips.corpus')
        self.lda_model = gensim.models.LdaModel.load(self.path + '/nips.lda')
        self.lemmatizer = WordNetLemmatizer()

        # Get all of the doc id's
        count, corpus = self.db_handler.get_table_rows_and_count("papers")
        for doc in corpus:
            self.docIds.append(doc[0])

    def get_topics_for_document(self, docId, nr_topics=3, nr_topic_words=5):
        document_topics = self.lda_model.get_document_topics(self.corpus[self.get_index_for_docid(docId)])
        topics_by_id = sorted(document_topics, key=lambda tup: tup[1], reverse=True)
        topic_results = []

        # Show the the top <nr_topic_words> words of the best <nr_topics> topics.
        nr_topics = min([nr_topics, len(topics_by_id)])

        for (topic_id, _) in topics_by_id[:nr_topics]:
            top_words = self.lda_model.show_topic(topic_id)
            max_topics = min([nr_topic_words, len(top_words)])
            top_words = [self.lemmatizer.lemmatize(word) for (word, _) in top_words[:max_topics]]
            top_words = list(set(top_words))  # remove the duplicates within a topic
            topic_results.append(top_words)
        return topic_results

    def get_index_for_docid(self, docId):
        try:
            return self.docIds.index(int(docId))
        except Exception as e:
            return -1

    def build_lda_model(self, filename='nips.mallet'):
        corpus = gensim.corpora.MalletCorpus(filename)
        corpus.serialize('nips.corpus', corpus)

        dictionary = gensim.corpora.Dictionary.from_corpus(corpus)
        dictionary.save('nips.dict')

        dictionary.filter_extremes(no_below=25, no_above=0.7)
        # Build a model
        model = gensim.models.LdaModel(corpus, id2word=corpus.id2word, alpha='auto', num_topics=50, passes=15)
        model.save('nips.lda')