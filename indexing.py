from whoosh.fields import Schema, TEXT, ID
from whoosh.index import create_in, open_dir
import os.path
from whoosh.query import *
from whoosh.analysis import StemmingAnalyzer
from whoosh.qparser import QueryParser

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
