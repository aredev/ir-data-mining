from indexer import Indexer
from author_clustering import AuthorClustering

def main():
    # index = Indexer()
    author_clusters = AuthorClustering(cache_enabled=True)


if __name__ == "__main__":
    main()