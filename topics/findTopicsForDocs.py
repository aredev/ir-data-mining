import gensim
from indexer.indexer import Indexer
from db_handler import DbHandler
import json
import csv

# indexer = Indexer()
fp = open('data/lda/bowcorpus.json', 'r')
corpusWithIds = json.load(fp)
corpusWithoutIds = [bow for (id, bow) in corpusWithIds]
ids = [id for (id, bow) in corpusWithIds]
print(ids)

dictionary = gensim.corpora.Dictionary.load('data/lda/nipsFilter50.dict')
corpus = gensim.corpora.MmCorpus('data/lda/filtered_nips2.mm')

model = gensim.models.LdaModel.load('data/lda/ldaFilter50.lda')

with open('docsTopTopic.csv', 'w') as csvfile:
    writer = csv.writer(csvfile, delimiter=',')
    topics = [sorted(model.get_document_topics(doc,minimum_probability=0.01), key=lambda x: x[1], reverse=True) for doc in corpus]
    topicsWithIds = list(zip(ids, topics))
    writer.writerow(['id', 'topicid'])
    for id, topics in topicsWithIds:
        t = [topic for topic, _ in topics]
        writer.writerow([id, t[0]])