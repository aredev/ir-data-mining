
from whoosh.scoring import WeightingModel, BaseScorer

class IDF(WeightingModel):
    def scorer(self, searcher, fieldname, text, qf=1):
        # IDF is a global statistic, so get it from the top-level searcher
        parent = searcher.get_parent()  # Returns self if no parent
        idf = parent.idf(fieldname, text)
        return IDFScorer(idf)


class IDFScorer(BaseScorer):
    def __init__(self, idf):
        self.idf = idf

    def supports_block_quality(self):
        return False

    def score(self, matcher):
        return self.idf
