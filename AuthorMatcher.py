# -*- coding: utf-8 -*-
"""
Created on Mon Sep 25 08:39:51 2017

@author: frans
"""

from whoosh.matching import Matcher
from whoosh.qparser import QueryParser

class AuthorMatcher(object):
    def __init__(self, index):
        self.index = index
        self.parser = QueryParser("author_name", index.schema)
    
    def query(self, s):
        parsed = self.parser.parse(s)
        
        with self.index.searcher() as searcher:
            results = searcher.search(parsed)
            
            # TODO: Order by ranking
            for r in results:
                print(r)

        return s