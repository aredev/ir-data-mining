import datetime
import re

from django.shortcuts import render

# Create your views here.
from group10_webinterface.papers.models import Paper, Author, Topic
from ir_model import IRModel


def index(request):

    m = IRModel.get_instance()
    return render(request, 'base.html', {
        'query': ""
    })


def find_query_value(field, raw_title_query):
    return raw_title_query.split(field)[0]


def search(request):
    start_time = datetime.datetime.now()
    m = IRModel.get_instance()

    query = request.POST.get('q')
    author = request.POST.get('author')
    years = request.POST.get('year')

    search_dict = {}
    if query is not None:
        search_dict['content_title'] = query
    if author is not None:
        search_dict['authors'] = author
    if years is not None:
        year_from = years.split(',')[0]
        year_to = years.split(',')[1]
        search_dict['pub_date'] = "[" + year_from + " TO " + year_to + "]"
    print(search_dict)

    results = m.indexer.multifield_search(search_dict)
    results = assign_pagerank(results, m)
    results = sorted(results, key=(lambda k: k['score']), reverse=True)[:10]

    end_time = datetime.datetime.now()
    computation_time = (end_time - start_time).seconds

    papers = []
    for result in results:
        papers.append(Paper.objects.get(id=result['docId']))

    previous_query = {
        'q': query,
        'author': author,
        'years': years
    }

    return render(request, 'results.html', {
        'results': papers,
        'query': previous_query,
        'nr_of_results': len(papers),
        'time': computation_time
    })


# This function assigns the pagerank of a paper.
def assign_pagerank(result_list, irm_model, y=1.0):
    return result_list
    # for i, result in enumerate(result_list):
        # result_list[i]['score'] = result['score'] + y * irm_model.reputation_scores.get_reputation_score_by_paper(
        #     result['docId'])
    # return result_list


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



""""
CRUDS PER MODEL
"""


def getAuthorById(request, author_id):
    author = Author.objects.get(id=author_id)
    return render(request, 'author.html', {'author': author})


def getTopicById(request, topic_id):
    topic = Topic.objects.get(id=topic_id)
    return render(request, 'topic.html', {'topic': topic})

def getPaperById(request, paper_id):
    paper = Paper.objects.get(id=paper_id)
    return render(request, 'paper.html', {'paper': paper})
