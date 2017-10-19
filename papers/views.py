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
    return raw_title_query.split(field)


def search(request):
    start_time = datetime.datetime.now()
    m = IRModel.get_instance()

    query = request.POST.get('q')
    pattern = re.compile("[a,y,t]:\"\w+\"")
    params = pattern.findall(query)
    partial_results = []
    for p in params:
        if p[0] == 't':
            title_query = find_query_value('t:', p[3:-1])
            partial_results.append(m.indexer.search(title_query, 'title'))
        elif p[0] == 'y':
            year_query = find_query_value('y:', p[3:-1])
            partial_results.append(m.indexer.search(year_query, 'year'))
        else:
            author_query = find_query_value('a:', p[3:-1])
            partial_results.append(m.indexer.search(author_query, 'author'))

    if len(partial_results) > 0:
        results = set(partial_results[0])
    for param_result in partial_results[1:]:
        results = results.intersection(param_result)

    body_query = pattern.sub('', query).strip()
    print(m.dummy.get_random())

    results = m.indexer.search(body_query)

    results = sorted(results, key=lambda k: k['order'])

    print(str(results[0]))
    for result in results:
        authors, suggested_authors = m.authors.find_authors_by_paper(result['docId'])
        result['suggested_authors'] = suggested_authors
        result['authors'] = authors
        result['topics'] = m.lda.get_topics_for_document(result['docId'])

    end_time = datetime.datetime.now()
    computation_time = (end_time-start_time).microseconds

    return render(request, 'results.html', {'results': results, 'nr_of_results': len(results), 'time': computation_time})
