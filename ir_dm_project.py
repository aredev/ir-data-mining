from indexer import Indexer
#from lda import LDA
from author_clustering import AuthorClustering
from ir_model import IRModel


def main():
    # a = AuthorClustering(cache_enabled=True)

    m = IRModel.get_instance()
    results = m.indexer.search("neural")
    print(m.authors.find_authors_by_paper(results[0]['docId']))

    print(m.lda.get_topics_for_document(results[0]['docId']))


if __name__ == "__main__":
    main()