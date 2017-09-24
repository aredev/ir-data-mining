from nltk.stem import WordNetLemmatizer
from whoosh.analysis import Filter


class WordnetLemmatizerFilter(Filter):

    def __call__(self, tokens):
        for t in tokens:
            t.is_morph = True
            t.text = WordNetLemmatizer().lemmatize(t.text)
            yield t
