import os

from nltk.tokenize import StanfordTokenizer
from whoosh.analysis import Composable, Token
from whoosh.compat import text_type


class StanTokenizer(Composable):
    def __init__(self):
        self.lib_dir = "libs/"
        self.stanford_path = os.path.abspath(self.lib_dir + "stanford-postagger.jar")
        self.stanford_tokenizer = StanfordTokenizer

    def __call__(self, value, positions=False, chars=False, keeporiginal=False,
                 removestops=True, start_pos=0, start_char=0, tokenize=True,
                 mode='', **kwargs):
        """
        Because object instantiation in Python is slow, tokenizers should create ONE SINGLE Token object
        and YIELD IT OVER AND OVER, changing the attributes each time.
        :param string: A unicode string
        :return: A token iterator
        """
        assert isinstance(value, text_type), "%s is not unicode" % repr(value)

        t = Token(positions, chars, removestops=removestops, mode=mode,
                  **kwargs)
        if not tokenize:
            t.original = t.text = value
            t.boost = 1.0
            if positions:
                t.pos = start_pos
            if chars:
                t.startchar = start_char
                t.endchar = start_char + len(value)
            yield t

        else:
            prevend = 0
            pos = start_pos
            text = self.stanford_tokenizer(path_to_jar=self.stanford_path).tokenize(value)
            for word in text:
                start = prevend
                end = start + len(word)
                if word:
                    t.text = word
                    t.boost = 1.0
                    if keeporiginal:
                        t.original = t.text
                    t.stopped = False
                    if positions:
                        t.pos = pos
                        pos += 1
                    if chars:
                        t.startchar = start_char + start
                        t.endchar = start_char + end
                    prevend = start + len(word)
                    yield t
