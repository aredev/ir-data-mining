import os

from nltk.tokenize import StanfordTokenizer
from nltk.stem import WordNetLemmatizer


class Tokenizer(object):
    def __init__(self):
        self.lib_dir = "libs/"
        self.stanford_path = os.path.abspath(self.lib_dir + "stanford-postagger.jar")
        self.stanford_tokenizer = StanfordTokenizer
        self.lemmatizer = WordNetLemmatizer
        self.tokens = {}

    def tokenize(self, docs):
        for doc in docs:
            # print(doc)
            id, year, title, _, pdf_name, abstract, paper_text = doc
            # Pre processing (e.g. spell checking)
            tokens = self.stanford_tokenizer(path_to_jar=self.stanford_path).tokenize(paper_text)
            # Post processing (e.g. lemmatization)
            map(self.lemmatizer.lemmatize, tokens)
            # Store results
            self.tokens[id] = tokens
