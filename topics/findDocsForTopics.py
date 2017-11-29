import gensim
from indexer.indexer import Indexer
from db_handler import DbHandler
import json
import csv

indexer = Indexer()
corpusWithIds = indexer.get_index_information()
fp = open('indexAsBow.json', 'w')
json.dump(corpusWithIds, fp)
corpusWithoutIds = [bow for (id, bow) in corpusWithIds]
ids = [id for (id, bow) in corpusWithIds]
print(ids)

dictionary = gensim.corpora.Dictionary.load('nipsFilter50.dict')
corpus = gensim.corpora.MmCorpus('filtered_nips2.mm')

model = gensim.models.LdaModel.load('ldaFilter50.lda')

with open('topDocsForTopics.csv', 'w') as csvfile:
    writer = csv.writer(csvfile, delimiter=',')
    for topicnr in range(model.num_topics):
        docs = sorted(zip(ids, model[corpus]), reverse=True, key=lambda x: abs(dict(x[1]).get(topicnr, 0.0)))
        for (docid, topics) in docs[:10]:
            for (topicid, prob) in topics:
                if topicid == topicnr:
                    writer.writerow([topicnr, docid, prob])
                    break
            print(docid, topics)
        #     print(indexer.db_handler.get_title_by_paper_id(id))
            # print(topicnr, ": ", [id for id, _ in docs[:10]])