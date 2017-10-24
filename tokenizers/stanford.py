import regex
from nltk import internals
from nltk.corpus import wordnet as wn
from nltk.tag.stanford import CoreNLPPOSTagger
from nltk.tokenize.stanford import CoreNLPTokenizer
from whoosh.analysis import Composable, Token
from whoosh.compat import text_type


class StanTokenizer(Composable):
    def __init__(self):
        self.server_url = "http://localhost:9000"
        self.stanford_tokenizer = CoreNLPTokenizer(self.server_url)
        self.stanford_tagger = CoreNLPPOSTagger(self.server_url)
        # Taken from https://stackoverflow.com/questions/265960/best-way-to-strip-punctuation-from-a-string-in-python
        self.remove = regex.compile(r'[\p{C}|\p{M}|\p{P}|\p{S}|\p{Z}]+', regex.UNICODE)
        """
        See https://stackoverflow.com/questions/27116495/java-command-fails-in-nltk-stanford-pos-tagger
        This will increase the maximum RAM size that java allows Stanford POS Tagger to use. 
        The '-xmx2G' changes the maximum allowable RAM to 2GB instead of the default 512MB.
        """
        internals.config_java(options='-xmx4G')

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
            try:
                # Tokenize
                tokens = self.stanford_tokenizer.tokenize(value)
                # Tag the tokens
                tagged_tokens = self.stanford_tagger.tag(tokens)
                # Remove punctuation and finally remove empty tokens
                tagged_tokens = self._remove_punctuation_using_tags(tagged_tokens)
                tagged_tokens = self._remove_empty_tokens(tagged_tokens)
                # print("Tagged and tokenized doc {} in: {}s".format(value[0:4], elapsed_time))
                for (token, pos_tag) in tagged_tokens:
                    start = prevend
                    end = start + len(token)
                    if token:
                        t.text = token
                        # Transform the pos-tags.
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
                        prevend = start + len(token)
                        yield t
            except Exception as e:
                """
                Documents with doc id "6398" and "6421" (having index 6355 and 6378 receptively)
                throw an exception when being tokenized. 
                """
                pass

    def _remove_punctuation(self, tagged_tokens):
        """
        Given a list of (token, tag) tuples, removes the punctuation in the token
        :param tagged_tokens: A list of (token, tag) tuples
        :return: A list of (token, tag) tuples, where any punctuation in the tokens has been removed.
        """
        return [(self.remove.sub(u" ", t[0]).strip(), t[1]) for t in tagged_tokens]

    def _remove_punctuation_using_tags(self, tagged_tokens):
        """
        The Stanford POS Tagger uses tags based on the Penn Treebank Project:
        https://stackoverflow.com/questions/1833252/java-stanford-nlp-part-of-speech-labels
        In addition to these tags, the Stanford POS Tagger has additional punctuation tags (9 in total):
        https://www.eecis.udel.edu/~vijay/cis889/ie/pos-set.pdf
        This function removes the punctuation  based on these punctuation tags and other tags.
        :param tagged_tokens: A list of (token, tag) tuples
        :return: A list of (token, tag) tuples, where any token with a punctuation tag has been removed
        """
        return [(t[0].strip(), t[1]) for t in tagged_tokens if
                t[1] not in ["#", "$", '"', ",", ".", ":", "``", "-LRB-", "-RRB-", "-RCB-", "-LCB-", "CD", "LS", "SYM"]
                and all(t)
                ]

    def _remove_empty_tokens(self, tagged_tokens):
        """
        Given a list of (token, tag) tuples, removes the tuples that an empty token (i.e. "")
        :param tagged_tokens: A list of (token, tag) tuples
        :return: A list of (token, tag) tuples, where tuples that had an empty token have ben removed
        """
        return [t for t in tagged_tokens if all(t)]

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
