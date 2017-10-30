import csv

from indexer.database import db_handler as db


class ReputationScores:
    def __init__(self):
        # Laad lijst van scores
        with open('data/scores.csv', 'r') as f:
            reader = csv.reader(f)
            self.lst = list(reader)
        self.author_list = [float(item[0]) for item in self.lst]
        self.score_list = [float(item[1]) for item in self.lst]
        self.mn = min(self.score_list)
        self.mx = max(self.score_list)
        self.score_list = [((item - self.mn) / (self.mx - self.mn)) for item in
                           self.score_list]

    def get_reputation_score_by_paper(self, docID):
        authors = db.DbHandler().get_authors_by_paper_id(docID)
        score = 0
        for author in authors:
            try:
                author = int(author)
                rs = self.get_score_from_list(author)
            except:
                rs = 0

            score = max(score, rs)

        return score

    def get_author_with_highest_reputation_score(self, authors):
        score = (0, authors[0])
        for author in authors:
            try:
                author = int(author)
                rs = self.get_score_from_list(author)
            except:
                rs = 0

            if rs > score[0]:
                score = (rs, author)
        return score[1]

    def get_score_from_list(self, author):
        index_number = self.author_list.index(author)
        score = self.score_list[index_number]
        return score

# voorbeeld gebruik.
# vb = ReputationScores()
# print(vb.get_reputation_score_from_authors(['test', ['1', 10, 'a', 1000, 1001]]))
