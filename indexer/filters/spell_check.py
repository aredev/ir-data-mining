from nltk.stem import WordNetLemmatizer
from whoosh.analysis import Filter
from util.spell import Spell


class SpellCheckFilter(Filter):
    def __init__(self):
        """
        Following the approach which is described here:
        https://stackoverflow.com/questions/3449968/large-scale-spell-checking-in-python
        http://norvig.com/spell-correct.html
        """
        self.spell = Spell().get_instance()

    def __call__(self, tokens):
        for t in tokens:
            t.is_morph = True
            org_text = t.text
            t.text = self.spell.correction(t.text)
            yield t
