import time
import os
from nltk.tokenize import StanfordTokenizer, sent_tokenize
from nltk.tag import StanfordPOSTagger
from whoosh.analysis import Composable, Token
from whoosh.compat import text_type
from nltk.corpus import wordnet as wn
from nltk import internals
import regex


class StanTokenizer(Composable):
    def __init__(self):
        self.lib_dir = "libs/"
        self.stanford_path = os.path.abspath(self.lib_dir + "stanford-postagger.jar")
        self.model_path = os.path.abspath(self.lib_dir + "models")
        self.stanford_tokenizer = StanfordTokenizer(path_to_jar=self.stanford_path)
        self.stanford_tagger = StanfordPOSTagger(self.model_path + '/english-bidirectional-distsim.tagger',
                                                 path_to_jar=self.stanford_path, java_options="-mx4500m")
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
            start_time = time.time()
            prevend = 0
            pos = start_pos
            """
            To prevent out of memory errors, we first tokenize the text into sentences.
            We then tokenize each of the sentences and then apply postagging.
            """
            sentences = sent_tokenize(value)
            """
            Tagging and tokenization is very slow.
            We can start the pos-tagger as a server, which makes it faster.
            See
            http://nlp.stanford.edu/software/pos-tagger-faq.shtml#d
            and
            https://stackoverflow.com/questions/23322674/how-to-improve-speed-with-stanford-nlp-tagger-and-nltk
            """
            print(len(sentences))
            tokenized_sentences = self.stanford_tokenizer.tokenize_sents(sentences)
            tagged_tokenized_sentences = self.stanford_tagger.tag_sents(tokenized_sentences)
            elapsed_time = time.time() - start_time
            print("Elapsed time: {}s".format(elapsed_time))
            """
            For each sentence, we loop through the words in this sentence.
            For each word, we apply the regex to remove punctuation.
            This leads to the empty string if the word only consisted of punctuation.
            """
            tagged_tokenized_sentences = map(
                lambda sent: map(lambda word: (self.remove.sub(u" ", word[0]).strip(), word[1]), sent),
                tagged_tokenized_sentences)

            lenght = 0
            for sentence in tagged_tokenized_sentences:
                # We only consider words that have all values in the tuple set
                for (word, pos_tag) in filter(lambda x: all(x), sentence):
                    lenght += 1
                    # print("word:{}, pos-tag:{}".format(word, pos_tag))
                    start = prevend
                    end = start + len(word)
                    if word:
                        t.text = word
                        # Transform the postags.
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
            print("Number of tokens in doc: {}".format(lenght))


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
