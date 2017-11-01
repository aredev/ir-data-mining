from whoosh.analysis import Filter
from util.spell import Spell
import enchant

class SpellCheckFilter(Filter):
    def __init__(self):
        """
        Following the approach which is described here:
        https://stackoverflow.com/questions/3449968/large-scale-spell-checking-in-python
        http://norvig.com/spell-correct.html
        """
        self.spell = Spell().get_instance()
        self.dic_us = enchant.Dict("en_US")
        self.dic_en = enchant.Dict("en_GB")

    def __call__(self, tokens):
        for t in tokens:
            if not self.dic_en.check(t.text) and not self.dic_us.check(t.text):
                uncorrected = t.text
                t.text = self.spell.correction(t.text)
                # print("Corrected '{}' to '{}'".format(uncorrected, t.text))
            yield t
