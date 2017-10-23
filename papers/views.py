import datetime
import re

from django.shortcuts import render

# Create your views here.
from ir_model import IRModel
from idfweighting import IDF


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
    pattern = re.compile("[a,y,t]:\"[a-zA-Z0-9 \.]+\"")
    params = pattern.findall(query)
    title_results = []  #list
    year_results = []   #nested list
    author_results = [] #nested_list

    for p in params:
        if p[0] == 't':
            title_query = "\'" + find_query_value('t:', p[3:-1]) + "\'"
            title_results.extend(m.indexer.search(title_query, 'title', IDF))
        elif p[0] == 'y':
            year_query = find_query_value('y:', p[3:-1])
            year_results.append(m.indexer.search(year_query, 'year'))
        elif p[0] == 'a':
            author_query = "\'*" + find_query_value('a:', p[3:-1]) + "*\'"
            author_results.append(m.indexer.search(author_query, 'authors'))

    need_to_intersect_year_author = len(year_results) > 0 and len(author_results) > 0
    year_author_results = []
    if need_to_intersect_year_author:
        year_author_results = combine_author_year_results(author_results[0], year_results[0])
    elif len(year_results) > 0:
        year_author_results = year_results[0]
    elif len(author_results) > 0:
        year_author_results = author_results[0]

    body_query = pattern.sub('', query).strip()
    if len(title_results) != 0:
        title_results = m.indexer.search(body_query, 'title', IDF)
    body_results = m.indexer.search(body_query)

    results = combine_title_body_results(title_results, body_results)

    #intersect with year results if it contains hits
    if len(results) > 0 and len(year_author_results) > 0:
        results = combine_with_year_results(results, year_author_results)
    elif len(year_author_results) > 0:
        results = year_author_results

    results = assign_pagerank(results, m)

    results = sorted(results, key=(lambda k: k['score']), reverse=True)

    # print("The beste result: " + str(results[0]))
    for result in results:
        authors, suggested_authors = m.authors.find_authors_by_paper(result['docId'])
        result['suggested_authors'] = suggested_authors
        result['authors'] = authors
        result['topics'] = m.lda.get_topics_for_document(result['docId'])

    end_time = datetime.datetime.now()
    computation_time = (end_time-start_time).microseconds

    return render(request, 'results.html', {'results': results, 'nr_of_results': len(results), 'time': computation_time})


# This function assigns the pagerank of a paper.
def assign_pagerank(result_list, irm_model, y=1.0):
    for i, result in enumerate(result_list):
        result_list[i]['score'] = result['score'] + y * irm_model.reputation_scores.get_reputation_score_by_paper(result['docId'])
    return result_list


def combine_with_year_results(combined_title_body_results, year_results):
    combined_list = []
    for yr in year_results:
        match = find_result_match(yr['docId'], combined_title_body_results)
        if match is not None:
            combined_list.append(yr)

    return combined_list


# Might be faster if you keep a list of the matches and remove them from the second search.
def combine_title_body_results(title_results, body_results, t=1.0, b=1.0):
    combined_list = []
    for br in body_results:
        match = find_result_match(br['docId'], title_results)
        if match is not None:
            print("MATCH")
            br['score'] = b * float(br['score']) + t * float(match['score'])
        else:
            br['score'] = b * float(br['score'])
        combined_list.append(br)

    for tr in title_results:
        match = find_result_match(tr['docId'], body_results)
        if match is None:
            tr['score'] = t * float(tr['score'])
            combined_list.append(tr)
    return combined_list

def combine_author_year_results(author_results, year_results):
    combined_list = []

    for ar in author_results:
        match = find_result_match(ar['docId'], year_results)
        if match is not None:
            combined_list.append(ar)

    return combined_list


# This function returns the result if it matches the paper_id, otherwise it returns None
def find_result_match(paper_id, result_list):
    for result in result_list:
        if result['docId'] == paper_id:
            return result
    return None
