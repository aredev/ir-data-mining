import os
import os.path
import re
import time
from datetime import datetime
from shutil import rmtree

import psutil
from tqdm import tqdm
from whoosh.analysis import LowercaseFilter, StopFilter
from whoosh.fields import Schema, TEXT, ID, STORED, DATETIME
from whoosh.index import create_in, exists_in, open_dir
from whoosh.qparser import QueryParser, MultifieldParser

from indexer.database.db_handler import DbHandler
from indexer.filters.punctuation import PunctuationFilter
from indexer.filters.stanford_lemmatizer import StanfordLemmatizerFilter
from indexer.tokenizers.stanford import StanTokenizer
from util import utils
from util.spell import Spell


class Indexer(object):
    def __init__(self, mode="normal"):
        self.db_handler = DbHandler()
        self.index_path = "index"
        self.ix = None
        self.writer = None
        self.spell = Spell.get_instance()
        """
        By default, the StandardAnalyzer() is used. This analyzer is composed of a RegexTokenizer with a LowercaseFilter
        and an optional StopFilter (for removing stopwords)
        """
        self.analyzer = self.__determine_analyzer(mode)
        """
        The whoosh.fields.TEXT indexes the text and stores the term positions to allow phrase searching
        TEXT fields use StandardAnalyzer by default. 
        To specify a different analyzer, use the analyzer keyword argument to the constructor, 
        e.g. TEXT(analyzer=analysis.StemmingAnalyzer())
        """
        # Read the Vectors section in http://whoosh.readthedocs.io/en/latest/schema.html
        self.schema = Schema(
            doc_id=ID(stored=True),
            title=TEXT(stored=True),
            authors=TEXT(stored=True),
            pub_date=DATETIME(stored=True),
            abstract=TEXT(stored=True),
            content=TEXT(vector=True, analyzer=self.analyzer),
            pdf_name=STORED,
        )
        """
        To test whether a directory currently contains a valid index, use index.exists_in:
        """
        exists = exists_in(self.index_path)
        if exists:
            print("Index already exists")
            # A valid index exists, reload the index
            self.__reload_index()
        else:
            print("Index does not yet exist")
            # No valid index found, remove and recreate index
            rmtree(self.index_path, ignore_errors=True)
            self.__create_index()

    def __determine_analyzer(self, mode):
        tokenizer = StanTokenizer()
        return {
            'normal': tokenizer | PunctuationFilter() | StanfordLemmatizerFilter() | LowercaseFilter(),
            'author topic modelling': tokenizer | PunctuationFilter() | StanfordLemmatizerFilter() | LowercaseFilter() | StopFilter(),
        }[mode]

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
        # To find out which terms are in the vocabulary, see
        # https://stackoverflow.com/questions/35565900/how-do-i-get-the-list-of-all-terms-in-a-whoosh-index
        # Add documents to the index
        row_count, corpus = DbHandler().get_table_rows_and_count("papers")
        start_time = time.time()
        try:
            docs_indexed = 0
            for document in tqdm(corpus):
                doc_id, year, title, _, pdf_name, abstract, paper_text = document
                if self.is_valid_document(paper_text, title):
                    # TODO remove this comment to fetch abstract from online
                    # abstract = self.determine_abstract(abstract, title, str(year))
                    author_names = utils.get_authors_for_doc_id(doc_id)
                    pub_date = datetime(year=year, month=1, day=1)
                    self.writer.add_document(doc_id=str(doc_id), pub_date=pub_date, title=title, pdf_name=pdf_name,
                                             content=paper_text, authors=author_names, abstract=abstract)
                    docs_indexed += 1
            self.writer.commit()
            elapsed_time = time.time() - start_time
            print("\nIndexing took {} seconds".format(elapsed_time))
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

    def from_hit_to_dict(self, hit, score):
        return {
            'docId': hit['doc_id'],
            'title': hit['title'],
            'year': hit['pub_date'],
            'score': score
        }

    def multifield_search(self, query_dict):
        """
        :param query_dict: a dict with keys for fields, values for sub queries
        :return:
        """
        field_weights = {
            'title': 10,
            'authors': 5,
            'pub_date': 2,
            'content': 1
        }
        with self.ix.searcher() as searcher:
            parser = MultifieldParser(field_weights.keys(), self.ix.schema, field_weights)
            sep = ''
            query = ''
            for key, val in query_dict.items():
                if val != '':
                    if key == 'content_title':
                        query += sep + "(title:({}) OR content:({}))".format(val, val)
                    elif key == 'authors':
                        query += sep + "(authors:({})".format(val)
                    elif key == 'pub_date':
                        query += sep + "(pub_date:({})".format(val)
                    sep = ' AND '

            parsed_query = parser.parse(query)
            corrected = searcher.correct_query(parsed_query, query)
            if corrected.query != parsed_query:
                print("Did you mean: " + str(corrected.string) + " ?")

            results = searcher.search(parsed_query)
            results_in_dict = []
            if len(results) > 0:
                for idx, r in enumerate(results):
                    results_in_dict.append(self.from_hit_to_dict(r, results.score(idx)))
            return results_in_dict

    def get_abstract_for_paper(self, title, year):
        """
        This method retrieves the abstract from a given paper text.
        This is done by getting the partial abstract from Google Scholar
        :param title: The title of the publication
        :param year: The year of the publication
        :return: A snippet of the abstract for the given publication taken from Google Scholar.
        """
        # search_query = scholarly.search_pubs_query(title + " " + year)
        # result = next(search_query)
        # abstract = result.bib['abstract']
        # return abstract

    def is_valid_document(self, paper_text, title):
        """
        This function determines whether the document is 'valid' or not.
        This is done by checking all of the wo
        :param paper_text:
        :return:
        """
        try:
            paper_text = utils.remove_punctuation.sub(u" ", paper_text)
            for stopword in utils.stops:
                # Check if any of the stopwords is present as a substring in the paper text (ignoring case)
                if re.search(stopword, paper_text, re.IGNORECASE):
                    return True
            return False
        except Exception as e:
            print(e)
            print("\nThis occurred for the document with the following title: '{}'".format(title))

    def is_valid_abstract(self, abstract):
        return abstract.lower() != "abstract missing"

    def determine_abstract(self, abstract, title, year):
        if self.is_valid_abstract(abstract):
            return abstract
        return self.get_abstract_for_paper(title, year)

    def get_index_information(self):
        all_doc_ids_iter = self.ix.reader().all_doc_ids()
        v_list = []
        a = 0
        for doc_num in all_doc_ids_iter:
            """
            ix.reader().vector returns a whoosh.matching.Matcher.
            See http://whoosh.readthedocs.io/en/latest/api/matching.html
            """
            a += 1
            print(a)
            doc_id = str(self.get_docId(doc_num))
            try:
                v = self.ix.reader().vector(doc_num, "content")
                # Convert to a list of (word, frequency) tuples
                v_items = tuple(v.items_as("frequency"))
            except:
                v_items = []
                print("NO VECTOR")

            v_list.append((doc_id, v_items))
            i = 0
        return v_list

    def get_voca(self):
        voca = list(self.ix.reader().all_terms())

        return voca

    def get_docId(self, doc_num):

        fields = self.ix.reader().stored_fields(doc_num)

        docId = fields["doc_id"]

        return docId
