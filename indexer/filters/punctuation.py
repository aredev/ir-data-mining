import regex
from whoosh.analysis import Filter


class PunctuationFilter(Filter):
    def __init__(self):
        # Taken from https://stackoverflow.com/questions/265960/best-way-to-strip-punctuation-from-a-string-in-python
        self.remove = regex.compile(r'[\p{C}|\p{M}|\p{P}|\p{S}|\p{Z}]+', regex.UNICODE)
        self.punctuation_tags = {"#", "$", '"', ",", ".", ":", "``", "-LRB-", "-RRB-", "-RCB-", "-LCB-", "CD", "LS",
                                 "SYM"}

    def __call__(self, tokens):
        tokens = self._remove_punctuation(tokens)
        tokens = self._remove_empty_tokens(tokens)
        for t in tokens:
            if t:
                yield t

    def _remove_punctuation(self, tokens):
        """
        Given a list of (token, tag) tuples, removes the punctuation in the token
        :param tagged_tokens: A list of (token, tag) tuples
        :return: A list of (token, tag) tuples, where any punctuation in the tokens has been removed.
        """
        for token in tokens:
            token.text = self.remove.sub(u" ", token.text).strip()
            yield token

    def _remove_punctuation_using_tags(self, tokens):
        """
        The Stanford POS Tagger uses tags based on the Penn Treebank Project:
        https://stackoverflow.com/questions/1833252/java-stanford-nlp-part-of-speech-labels
        In addition to these tags, the Stanford POS Tagger has additional punctuation tags (9 in total):
        https://www.eecis.udel.edu/~vijay/cis889/ie/pos-set.pdf
        This function removes the punctuation  based on these punctuation tags and other tags.
        :param tagged_tokens: A list of (token, tag) tuples
        :return: A list of (token, tag) tuples, where any token with a punctuation tag has been removed
        """
        for token in tokens:
            if token.pos not in self.punctuation_tags:
                yield token

    def _remove_empty_tokens(self, tokens):
        """
        Given a list of (token, tag) tuples, removes the tuples that an empty token (i.e. "")
        :param tagged_tokens: A list of (token, tag) tuples
        :return: A list of (token, tag) tuples, where tuples that had an empty token have ben removed
        """
        for token in tokens:
            if token.text:
                yield token
