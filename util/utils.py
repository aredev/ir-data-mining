import sys
import unicodedata

import regex
from nltk.corpus import stopwords

from indexer.database.db_handler import DbHandler

# Taken from https://stackoverflow.com/questions/265960/best-way-to-strip-punctuation-from-a-string-in-python
remove_punctuation = regex.compile(r'[\p{C}|\p{M}|\p{P}|\p{S}|\p{Z}]+', regex.UNICODE)
stops = set(stopwords.words('english'))
punctuation_tags = {"#", "$", '"', ",", ".", ":", "``", "-LRB-", "-RRB-", "-RCB-", "-LCB-", "CD", "LS",
                    "SYM"}


# Print iterations progress
def print_progress(iteration, total, prefix='', suffix='', decimals=1, bar_length=50):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        bar_length  - Optional  : character length of bar (Int)
    """
    str_format = "{0:." + str(decimals) + "f}"
    percents = str_format.format(100 * (iteration / float(total)))
    filled_length = int(round(bar_length * iteration / float(total)))
    bar = '█' * filled_length + '-' * (bar_length - filled_length)

    sys.stdout.write('\r%s |%s| %s%s %s' % (prefix, bar, percents, '%', suffix)),

    if iteration == total:
        sys.stdout.write('\n')
    sys.stdout.flush()


def get_authors_for_doc_id(doc_id):
    author_ids = DbHandler().get_authors_by_paper_id(doc_id)
    author_names = ""
    for author_id in author_ids:
        author_names += DbHandler().get_author_by_id(author_id) + " "
    return author_names


def normalize_caseless(text):
    return unicodedata.normalize("NFKD", text.casefold())


def caseless_equal(left, right):
    return normalize_caseless(left) == normalize_caseless(right)


def parse(text, additional_properties):
    from nltk.parse import CoreNLPParser
    parser = CoreNLPParser()
    json_result = parser.api_call(text, properties=additional_properties)
    return json_result
