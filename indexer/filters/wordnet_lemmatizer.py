from nltk.stem import WordNetLemmatizer
from whoosh.analysis import Filter
from nltk.corpus import wordnet as wn


class WordnetLemmatizerFilter(Filter):
    def __call__(self, tokens):
        for t in tokens:
            transformed_tag = self._penn2morphy(t.pos)
            if transformed_tag:
                t.text = WordNetLemmatizer().lemmatize(t.text, transformed_tag)
            else:
                t.text = WordNetLemmatizer().lemmatize(t.text)
            yield t

    def _penn2morphy(self, penntag, return_none=False):
        """
        Tagging is done using the Stanford POS tagger.
        This function maps these pos tags so that they are recognised in WordNet.
        If no map was not found, the empty string will be returned.
        Taken from https://stackoverflow.com/questions/35458896/python-map-nltk-stanford-pos-tags-to-wordnet-pos-tags
        :param return_none:
        :return:
        """
        morphy_tag = {'NN': wn.NOUN, 'JJ': wn.ADJ,
                      'VB': wn.VERB, 'RB': wn.ADV}
        try:
            return morphy_tag[penntag[:2]]
        except:
            return None if return_none else ''
