import datetime

from Dummy import Dummy
from indexer import Indexer
from author_clustering import AuthorClustering
from ScoreFunction import ReputationScores
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
            self.dummy = Dummy()
            self.reputation_scores = ReputationScores()
            self.authors = AuthorClustering(cache_enabled=True)
            # self.lda = LDA()
            IRModel.__instance = self
            end_time = datetime.datetime.now()
            print("Finished initialization of IR Model! at " + str(end_time) + "\nIt took: " + str(end_time - start_time))




