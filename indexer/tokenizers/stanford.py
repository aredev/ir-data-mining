import logging

import regex
from nltk import internals
from nltk.parse.corenlp import GenericCoreNLPParser
from whoosh.analysis import Composable, Token
from whoosh.compat import text_type


class StanTokenizer(Composable):
    def __init__(self):
        self.server_url = "http://localhost:9000"
        # Annotator dependencies, see https://stanfordnlp.github.io/CoreNLP/dependencies.html
        self.additional_properties = {
            'tokenize.options': 'ptb3Escaping=false, unicodeQuotes=true, splitHyphenated=true, normalizeParentheses=false, normalizeOtherBrackets=false',
            'annotators': 'tokenize, ssplit, pos, lemma'
        }
        self.stanford_abstract_parser = GenericCoreNLPParser(self.server_url)
        self.stanford_abstract_parser.parser_annotator = 'depparse'
        # The '-xmx2G' changes the maximum allowable RAM to 2GB instead of the default 512MB.
        internals.config_java(options='-xmx4G')

    def __call__(self, value, positions=False, chars=False, keeporiginal=False,
                 removestops=True, start_pos=0, start_char=0, tokenize=True,
                 mode='', **kwargs):
        """
        :param value: The unicode string to tokenize.
        :param positions: Whether to record token positions in the token.
        :param chars: Whether to record character offsets in the token.
        :param start_pos: The position number of the first token. For example,
            if you set start_pos=2, the tokens will be numbered 2,3,4,...
            instead of 0,1,2,...
        :param start_char: The offset of the first character of the first
            token. For example, if you set start_char=2, the text "aaa bbb"
            will have chars (2,5),(6,9) instead (0,3),(4,7).
        :param tokenize: if True, the text should be tokenized.
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
            pos = start_pos
            try:
                json_result = self.stanford_abstract_parser.api_call(value, properties=self.additional_properties)
                for sentence in json_result['sentences']:
                    for token in sentence['tokens']:
                        if token:
                            t.text = token['word']
                            t.lemma = token['lemma']
                            t.pos = token['pos']
                            t.boost = 1.0
                            if keeporiginal:
                                t.original = token['originalText']
                            t.stopped = False
                            if positions:
                                t.pos = pos
                                pos += 1
                            if chars:
                                t.startchar = token['characterOffsetBegin']
                                t.endchar = token['characterOffsetEnd']
                            yield t
            except Exception as e:
                logging.critical(str(e))
                pass




