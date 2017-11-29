
import gensim
from random import randint

topicpath = ''
dictionary = gensim.corpora.Dictionary.load('nipsFilter50.dict')
model = gensim.models.LdaModel.load('ldaFilter50.lda')

# randomWord = dict.items()[randint(0,len(dict.items())-1)][1]


top_words = [[word for word, _ in model.show_topic(topicno, topn=10)] for topicno in range(model.num_topics)]

i = 0
for topic in top_words:
    print (str(i), ": %s" % (' '.join(topic)))
    i += 1