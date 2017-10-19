import os
import os.path
import sys
from shutil import rmtree

from whoosh.analysis import LowercaseFilter, StopFilter
from whoosh.fields import Schema, TEXT, ID, STORED, DATETIME
from whoosh.index import create_in, exists_in, open_dir
from whoosh.qparser import QueryParser, syntax
from nltk.tokenize import StanfordTokenizer

from db_handler import DbHandler
from filters.wordnet_lemmatizer import WordnetLemmatizerFilter
from tokenizers.stanford import StanTokenizer
from cosine import CosineSim

class Indexer(object):
    def __init__(self):
        self.db_handler = DbHandler()
        self.stanford_path = os.path.abspath("libs/stanford-postagger.jar")
        self.stanford_tokenizer = StanfordTokenizer
        self.index_path = "index"
        self.ix = None
        self.writer = None
        """
        By default, the StandardAnalyzer() is used. This analzer is composed of a RegexTokenizer with a LowercaseFilter
        and an optional StopFilter (for removing stopwords)
        """
        self.analyzer = StanTokenizer() | LowercaseFilter() | WordnetLemmatizerFilter()
        """
        The whoosh.fields.TEXT indexes the text and stores the term positions to allow phrase searching
        TEXT fields use StandardAnalyzer by default. 
        To specify a different analyzer, use the analyzer keyword argument to the constructor, 
        e.g. TEXT(analyzer=analysis.StemmingAnalyzer())
        """
        self.schema = Schema(
            docId=ID(stored=True),
            content=TEXT(analyzer=self.analyzer),
            year=STORED,
            title=TEXT,
            pdf_name=STORED,
        )
        """
        To test whether a directory currently contains a valid index, use index.exists_in:
        """
        exists = exists_in(self.index_path)
        if exists:
            # A valid index exists, reload the index
            self.__reload_index()
        else:
            print("Not")
            # No valid index found, remove and recreate index
            rmtree(self.index_path, ignore_errors=True)
            self.__create_index()

    def __reload_index(self):
        """
        Reload the index
        :return:
        """
        self.ix = open_dir(u"index")
        self.writer = self.ix.writer()

    def __create_index(self):
        """
        Create a new index
        :return:
        """
        os.mkdir(self.index_path)
        self.ix = create_in(self.index_path, self.schema)
        self.writer = self.ix.writer()
        # Add documents to the index
        row_count, corpus = self.db_handler.get_table_rows_and_count("papers")
        try:
            for document in range(0, 20):
                docId, year, title, _, pdf_name, abstract, paper_text = corpus[document]
                # print(docId, year, title, pdf_name, abstract)
                text = self.stanford_tokenizer(path_to_jar=self.stanford_path).tokenize(paper_text)
                text = [x.lower() for x in text]
                self.writer.add_document(docId = str(docId), content = text, year = year, title = title, pdf_name = pdf_name)
                #if docId%200 == 0:
                print(str(docId) + " en " + str(" ".join(text)))
            # Commit changes
            self.writer.commit()
        except Exception as e:
            # Formatted printing exception
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            # In addition, we also print the normal exception
            print(e)
            # Remove the index
            rmtree(self.index_path, ignore_errors=True)

    def search(self, query):
        """
        Search using a given query
        :param query: a query
        :return:
        """
        with self.ix.searcher() as searcher:
            parser = QueryParser("content", self.ix.schema, group=syntax.OrGroup)
            query = parser.parse(query)
            print(query)
            similarityScorer = CosineSim(searcher, query)
            results = searcher.search(query, limit=None, scored=False, sortedby=False, terms=True)
            print(len(results))
            scoredResults ={}
            if len(results) > 0:
                for r in results:
                    print(r.docnum)
                    scoredResults[r.docnum] = similarityScorer.similarity(r.docnum+1)
