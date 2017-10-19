from indexer import Indexer
from author_clustering import AuthorClustering

def main():
    # index = Indexer()
    author_clusters = AuthorClustering(cache_enabled=True)
    #print(author_clusters.find_authors_by_paper("3206"))
    print("suggestions:" + author_clusters.find_authors_by_paper("3719")) #paper 3719 auth 3758


if __name__ == "__main__":
    main()