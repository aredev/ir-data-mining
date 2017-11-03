from whoosh.analysis import Filter


class StanfordLemmatizerFilter(Filter):
    def __call__(self, tokens):
        for t in tokens:
            t.text = t.lemma
            yield t
