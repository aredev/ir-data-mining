import datetime
from django.http import HttpResponse
from django.shortcuts import render
import re

# Create your views here.
from indexer import Indexer
from ir_model import IRModel
from author_clustering import AuthorClustering


def index(request):
    m = IRModel.get_instance()
    print(m.dummy.get_random())
    # return HttpResponse(str(m.dummy.get_random()))
    return render(request, 'base.html')


def find_query_value(field, raw_title_query):
    return raw_title_query.split(field)[0]


def search(request):
    start_time = datetime.datetime.now()
    m = IRModel.get_instance()

    query = request.POST.get('q')
    pattern = re.compile("[y,t]:\"[a-zA-Z0-9 \.]+\"")
    params = pattern.findall(query)
    partial_results = []
    title_results = []  #list
    year_results = []   #nested list
    author_results = [] #nested list
    body_results = []
    for p in params:

        if p[0] == 't':
            title_query = "\'" + find_query_value('t:', p[3:-1]) + "\'"
            title_results.extend(m.indexer.search(title_query, 'title'))
        elif p[0] == 'y':
            year_query = find_query_value('y:', p[3:-1])
            year_results.append(m.indexer.search(year_query, 'year'))

    # intersect results from author and year
    print(title_results)
    print(year_results)

    body_query = pattern.sub('', query).strip()
    body_results = m.indexer.search(body_query)

    results = combine_title_body_results(title_results, body_results)
    intersect = None
    """"# Check if both tags are used.
    if len(year_results) > 0 and len(author_results) > 0:
        intersect = set(flatten(year_results)).intersection(flatten(author_results))
    elif len(year_results) > 0:
        intersect = set(flatten(year_results))
    elif len(author_results) > 0:
        intersect = set(flatten(author_results))
    """
    print("Before: " + str([body['score'] for body in body_results]))
    results = combine_title_body_results(body_results, body_results)
    print("Combined: " + str([body['score'] for body in results]))
    #results = set(partial_results[0])

    """if len(partial_results) > 0:
        results = set(partial_results[0])
    for param_result in partial_results[1:]:
        results = results.intersection(param_result)"""

    results = sorted(results, key=(lambda k: k['score']), reverse=True)

    print("The beste result: " + str(results[0]))
    for result in results:
        authors, suggested_authors = m.authors.find_authors_by_paper(result['docId'])
        result['suggested_authors'] = suggested_authors
        result['authors'] = authors
        # result['topics'] = m.lda.get_topics_for_document(result['docId'])

    end_time = datetime.datetime.now()
    computation_time = (end_time-start_time).microseconds

    return render(request, 'results.html', {'results': results, 'nr_of_results': len(results), 'time': computation_time})

# This help function performs a flatten operation on a double nested list.
def flatten(nestedlist):
    return [element for sublist in nestedlist for element in sublist]


# Might be faster if you keep a list of the matches and remove them from the second search.
def combine_title_body_results(title_results, body_results):
    combined_list = []
    for br in body_results:
        match = find_result_match(br['docId'], title_results)
        if match is not None:
            print("MATCH")
            br['score'] = float(br['score']) + float(match['score'])
        combined_list.append(br)

    for tr in title_results:
        match = find_result_match(tr['docId'], body_results)
        if match is None:
            combined_list.append(tr)
    return combined_list

# This function returns the result if it matches the paper_id, otherwise it returns None
def find_result_match(paper_id, result_list):
    for result in result_list:
        if result['docId'] == paper_id:
            return result
    return None
