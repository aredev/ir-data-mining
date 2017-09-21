import os.path
import sqlite3

from whoosh.fields import Schema, TEXT, ID
from whoosh.index import create_in, open_dir
from whoosh.qparser import QueryParser

from Tokenizer import Tokenizer


class Indexer(object):
    def __init__(self, path="data/", filename="database.sqlite"):
        self.data_path = path
        self.db_name = filename
        self.conn = sqlite3.connect(self.data_path + self.db_name)
        self.cursor = self.conn.cursor()
        self.index = {}
        self.tokenizer = Tokenizer()

    def db_info(self):
        for name in self.get_table_names():
            print(name, "\t", len(self.conn.execute("SELECT * FROM " + name).fetchall()))

    def get_table_row_count(self, table):
        results = self.conn.execute("SELECT * FROM " + table).fetchall()
        return len(results)

    def get_table_rows_and_count(self, table):
        results = self.conn.execute("SELECT * FROM " + table).fetchall()
        return len(results), results

    def get_table_names(self):
        results = self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
        return [name[0] for name in results]

    def tokenize(self):
        row_count, results = self.get_table_rows_and_count("papers")
        self.tokenizer.tokenize(results)

    def index(self):
        # TODO Abdullah, I just copied your code here. We should integrate next time
        # Reverse index (http://whoosh.readthedocs.io/en/latest/glossary.html)
        # Create fake data

        schema = Schema(
            docId=ID(stored=True),
            content=TEXT,
        )

        # Create inde

        if not os.path.exists("index"):
            os.mkdir("index")
        ix = create_in("index", schema)

        ix = open_dir("index")

        writer = ix.writer()
        writer.add_document(docId=u"8", content=u"This is my document")
        writer.add_document(docId=u"9", content=u"This is my plop")
        writer.add_document(docId=u"10", content=u"Life like this")
        writer.add_document(docId=u"11", content=u"document document document")

        writer.commit()

        # Find te


        with ix.searcher() as searcher:
            parser = QueryParser("content", ix.schema)
            myquery = parser.parse(u"This document")
            print(myquery)
            results = searcher.search(myquery)
            print(len(results))
            if len(results) > 0:
                for r in results:
                    print(r)
