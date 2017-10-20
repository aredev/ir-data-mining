from indexer import Indexer
#from lda import LDA
from author_clustering import AuthorClustering
from ir_model import IRModel
import nltk

def main():
    #a = AuthorClustering(cache_enabled=True)
    #print(a.find_authors_by_paper("3"))

    m = IRModel.get_instance()
    results = m.indexer.search("neural")
    print(m.authors.find_authors_by_paper(results[1]['docId']))

    topics = m.lda.get_topics_for_document(results[0]['docId'])
    #print("doc_id: " + results[1]['docId'])
    for result in results:
        print("Score: " + str(result['score']))


if __name__ == "__main__":
    main()