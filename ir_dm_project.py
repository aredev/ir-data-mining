import os
import sys
sys.path.append(os.getcwd())

from Indexer import Indexer
from AuthorMatcher import AuthorMatcher


def main():
    index = Indexer()
    matcher = AuthorMatcher(index.ix)
    r = matcher.query("Maxwell")
    print("Result: {}".format(r))

if __name__ == "__main__":
    main()