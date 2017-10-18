import os
from nltk.tokenize import StanfordTokenizer
from nltk.tag import StanfordPOSTagger
from whoosh.analysis import Composable, Token
from whoosh.compat import text_type
from nltk.corpus import wordnet as wn
import regex


class StanTokenizer(Composable):
    def __init__(self):
        self.lib_dir = "libs/"
        self.stanford_path = os.path.abspath(self.lib_dir + "stanford-postagger.jar")
        self.model_path = os.path.abspath(self.lib_dir + "models")
        self.stanford_tokenizer = StanfordTokenizer(path_to_jar=self.stanford_path)
        self.stanford_tagger = StanfordPOSTagger(self.model_path + '/english-bidirectional-distsim.tagger',
                                                 path_to_jar=self.stanford_path)
        # Taken from https://stackoverflow.com/questions/265960/best-way-to-strip-punctuation-from-a-string-in-python
        self.remove = regex.compile(r'[\p{C}|\p{M}|\p{P}|\p{S}|\p{Z}]+', regex.UNICODE)

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
            tokenized_text = self.stanford_tokenizer.tokenize(value)
            tagged_tokenized_text = self.stanford_tagger.tag(tokenized_text)
            # TODO the regex also removes things like '-' in the word 'self-organizing'. Find out if this is a problem
            # apply the regex to remove punctuation and also remove spaces as words
            tagged_tokenized_text = [(self.remove.sub(u" ", word[0]).strip(), word[1]) for word in
                                     tagged_tokenized_text]
            """
            As we removed the tokens that were punctuation, we have to remove the tokens that don't have an empty first element.
            This can be done using the "all()" function, which returns False only if all values in t1 are non-empty/nonzero.
            See https://stackoverflow.com/questions/31154372/what-is-the-best-way-to-check-if-a-tuple-has-any-empty-none-values-in-python
            """
            tagged_tokenized_text = list(filter(lambda x: all(x), tagged_tokenized_text))
            for (word, pos_tag) in tagged_tokenized_text:
                start = prevend
                end = start + len(word)
                if word:
                    t.text = word
                    t.pos_tag = self._penn2morphy(pos_tag)
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

    def _penn2morphy(self, penntag, return_none=False):
        """
        Tagging is done using the Stanford POS tagger.
        This function maps these pos tags so that they are recognised in WordNet.
        If no map was not found, the empty string will be returned.
        Taken from https://stackoverflow.com/questions/35458896/python-map-nltk-stanford-pos-tags-to-wordnet-pos-tags
        :param returnNone:
        :return:
        """
        morphy_tag = {'NN': wn.NOUN, 'JJ': wn.ADJ,
                      'VB': wn.VERB, 'RB': wn.ADV}
        try:
            return morphy_tag[penntag[:2]]
        except:
            return None if return_none else ''
