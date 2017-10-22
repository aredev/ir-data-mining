import os
import os.path
import time
from shutil import rmtree

import psutil
from whoosh.analysis import LowercaseFilter
from whoosh.fields import Schema, TEXT, ID, STORED
from whoosh.index import create_in, exists_in, open_dir
from whoosh.qparser import QueryParser

from db_handler import DbHandler
from filters.wordnet_lemmatizer import WordnetLemmatizerFilter
from tokenizers.stanford import StanTokenizer
from util.utils import print_progress


class Indexer(object):
    def __init__(self):
        self.db_handler = DbHandler()
        self.index_path = "index"
        self.ix = None
        self.writer = None
        """
        By default, the StandardAnalyzer() is used. This analyzer is composed of a RegexTokenizer with a LowercaseFilter
        and an optional StopFilter (for removing stopwords)
        """
        self.analyzer = StanTokenizer() | LowercaseFilter() | WordnetLemmatizerFilter()  # | StopFilter()

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
        Create a new index. This takes about 15 minutes on an average machine assuming a low workload
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
        # use 40 percent of the available ram
        available_free_ram *= 0.4
        self.writer = self.ix.writer(procs=psutil.cpu_count(), limitmb=available_free_ram, multisegment=True)
        # self.writer = self.ix.writer()
        # To find out which terms are in the vocabulary, see
        # https://stackoverflow.com/questions/35565900/how-do-i-get-the-list-of-all-terms-in-a-whoosh-index
        # Read this: https://www.ocf.berkeley.edu/~tzhu/senate/Whoosh-2.4.1/docs/build/html/_sources/indexing.txt
        # Add documents to the index
        row_count, corpus = self.db_handler.get_table_rows_and_count("papers")
        start_time = time.time()
        print_progress(0, row_count, prefix="Docs being indexed:", suffix=" Complete")
        try:
            docs_indexed = 0
            for document in corpus:
                """
                A doc id is not the previous doc id incremented by one: for example, doc ID 57 is not being used,
                although doc ID 56 and 58 are.
                Therefore, we maintain our own counter to track the indexing progress
                """
                docId, year, title, _, pdf_name, abstract, paper_text = document
                # print(docId, year, title, pdf_name, abstract)
                self.writer.add_document(docId=str(docId), year=str(year), title=title, pdf_name=pdf_name,
                                         content=paper_text)
                print_progress(docs_indexed, row_count, prefix="Docs being indexed:", suffix=" Complete")
                docs_indexed += 1
            self.writer.commit()
            elapsed_time = time.time() - start_time
            print("\nIndexing took {} seconds".format(elapsed_time))
            all_terms = list(self.ix.reader().all_terms())
            print("Number of terms in the vocabulary: {}".format(len(all_terms)))
        except Exception as e:
            # Stop the writer and remove the index
            self.writer.cancel()
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
