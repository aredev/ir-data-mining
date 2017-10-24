import datetime

from ScoreFunction import ReputationScores
from author_clustering import AuthorClustering
from indexer import Indexer


# Singleton class that holds the instantiations that are needed during execution of the queries.
from lda import LDA


class IRModel:
    __instance = None

    @staticmethod
    def get_instance():
        if IRModel.__instance is None:
            IRModel()
        return IRModel.__instance

    def __init__(self):
        if IRModel.__instance is not None:
            raise Exception("Singleton bla")
        else:
            start_time = datetime.datetime.now()
            print("Starting initialization of IR Model! at " + str(start_time))
            self.indexer = Indexer()
            self.reputation_scores = ReputationScores()
            self.authors = AuthorClustering(cache_enabled=True)
            self.lda = LDA()
            IRModel.__instance = self
            end_time = datetime.datetime.now()
            print(
                "Finished initialization of IR Model! at " + str(end_time) + "\nIt took: " + str(end_time - start_time))
