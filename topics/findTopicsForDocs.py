import gensim
from indexer.indexer import Indexer
from db_handler import DbHandler
import json
import csv

indexer = Indexer()
fp = open('bowcorpus.json', 'r')
corpusWithIds = json.load(fp)
corpusWithoutIds = [bow for (id, bow) in corpusWithIds]
ids = [id for (id, bow) in corpusWithIds]
print(ids)

dictionary = gensim.corpora.Dictionary.load('nipsFilter50.dict')
corpus = gensim.corpora.MmCorpus('filtered_nips2.mm')

model = gensim.models.LdaModel.load('ldaFilter50.lda')

with open('topTopicsForDocs.csv', 'w') as csvfile:
    writer = csv.writer(csvfile, delimiter=',')
    topics = [sorted(model.get_document_topics(doc,minimum_probability=0.01), key=lambda x: x[1], reverse=True) for doc in corpus]
    topicsWithIds = list(zip(ids, topics))
    print(topicsWithIds[110:115])
    for id, topics in topicsWithIds:
        for topic, prob in topics:
            writer.writerow([id, topic, prob])