import os
import os.path
import sys
from shutil import rmtree

from whoosh.analysis import LowercaseFilter, StopFilter
from whoosh.fields import Schema, TEXT, ID, STORED
from whoosh.index import create_in, exists_in, open_dir
from whoosh.qparser import QueryParser

from db_handler import DbHandler
from filters.wordnet_lemmatizer import WordnetLemmatizerFilter
from tokenizers.stanford import StanTokenizer

import psutil


class Indexer(object):
    def __init__(self):
        self.db_handler = DbHandler()
        self.index_path = "index"
        self.ix = None
        self.writer = None
        """
        By default, the StandardAnalyzer() is used. This analzer is composed of a RegexTokenizer with a LowercaseFilter
        and an optional StopFilter (for removing stopwords)
        """
        self.analyzer = StanTokenizer() | LowercaseFilter() | WordnetLemmatizerFilter() | StopFilter()
        """
        The whoosh.fields.TEXT indexes the text and stores the term positions to allow phrase searching
        TEXT fields use StandardAnalyzer by default. 
        To specify a different analyzer, use the analyzer keyword argument to the constructor, 
        e.g. TEXT(analyzer=analysis.StemmingAnalyzer())
        """
        self.schema = Schema(
            docId=ID(stored=True),
            content=TEXT(analyzer=self.analyzer),
            year=TEXT(stored=True),
            title=TEXT(stored=True),
            pdf_name=STORED,
        )
        """
        To test whether a directory currently contains a valid index, use index.exists_in:
        """
        # TODO remove "and False" cuz this is a debug statement
        exists = exists_in(self.index_path)
        if exists and False:
            # A valid index exists, reload the index
            self.__reload_index()
        else:
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
        """
        Optimization, we automatically determine the number of processors to use.
        We also determine the amount of RAM that is available and set that as a threshold.
        """
        values = psutil.virtual_memory()
        # to display in MB format, bitshift right with 20. For GB format, shift with 30.
        available_free_ram = values.available >> 20
        # use 80 percent of the available ram
        available_free_ram *= 0.4
        self.writer = self.ix.writer(procs=psutil.cpu_count(), limitmb=available_free_ram, multisegment=True)
        # self.writer = self.ix.writer()
        # To find out which terms are in the vocabulary, see
        # https://stackoverflow.com/questions/35565900/how-do-i-get-the-list-of-all-terms-in-a-whoosh-index
        # Read this: https://www.ocf.berkeley.edu/~tzhu/senate/Whoosh-2.4.1/docs/build/html/_sources/indexing.txt
        # Add documents to the index
        row_count, corpus = self.db_handler.get_table_rows_and_count("papers")
        try:
            for document in corpus[:2]:
                docId, year, title, _, pdf_name, abstract, paper_text = document
                print(docId, year, title, pdf_name, abstract)
                self.writer.add_document(docId=str(docId), year=str(year), title=title, pdf_name=pdf_name,
                                         content=paper_text)
            # Commit changes. NOTE this is a very slow operation, not sure how this can be fixed
            self.writer.commit()
        except Exception as e:
            # Formatted printing exception
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            # In addition, we also print the normal exception
            print(e)
            self.writer.cancel()
            # Remove the index
            rmtree(self.index_path, ignore_errors=True)

        """
        So, while multisegment=True is much faster than a normal writer, you should only use it for 
        large batch indexing jobs (or perhaps only for indexing from scratch). 
        It should not be the only method you use for indexing, 
        because otherwise the number of segments will tend to increase forever!
        """
        self.writer = self.ix.writer()

    def search(self, query):
        """
        Search using a given query
        :param query: a query
        :return:
        """
        with self.ix.searcher() as searcher:
            parser = QueryParser("content", self.ix.schema)
            query = parser.parse(query)
            results = searcher.search(query)
            print(len(results))
            if len(results) > 0:
                for r in results:
                    print(r)
