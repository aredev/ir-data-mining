from indexer import Indexer
#from lda import LDA
from author_clustering import AuthorClustering
import datetime
from ir_model import IRModel
import nltk
import re

def main():
    #a = AuthorClustering(cache_enabled=True)
    #print(a.find_authors_by_paper("3"))

    # query = "a:\"John de Beer\""
    # pattern = re.compile("[a,y,t]:\"[a-zA-Z ]+\"")
    # params = pattern.findall(query)
    # print(params)


    m = IRModel.get_instance()
    # body_results = m.indexer.search("neural")
    # title_results = m.indexer.search("Constrained Differential Optimization", 'title')


    #print(m.authors.find_authors_by_paper(results[1]['docId']))

    # topics = m.lda.get_topics_for_document(results[0]['docId'])
    #print("doc_id: " + results[1]['docId'])
    # for result in results:
    #     print("Doc: " +str(result['docId'])+"Score: "+ str(result['score']))

if __name__ == "__main__":
    main()