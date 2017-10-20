from indexer import Indexer
#from lda import LDA
from author_clustering import AuthorClustering
import datetime
from ir_model import IRModel
import nltk

def main():
    #a = AuthorClustering(cache_enabled=True)
    #print(a.find_authors_by_paper("3"))

    test()

    """m = IRModel.get_instance()
    results = m.indexer.search("neural")
    print(m.authors.find_authors_by_paper(results[0]['docId']))

    topics = m.lda.get_topics_for_document(results[0]['docId'])
    print("doc_id: " + results[0]['docId'])
    for result in results:
        print("Doc: " +str(result['docId'])+"Score: "+ str(type(result['score'])))"""


def test():
    body_results = [{'docId': '1', 'score': 1.0}, {'docId': '2', 'score': 2.0}, {'docId': '3', 'score': 3.0}]
    title_results = [{'docId': '4', 'score': 1.0}, {'docId': '2', 'score': 2.0}, {'docId': '8', 'score': 3.0}]
    combo = combine_title_body_results(title_results, body_results)

    for r in combo:
        print("doc_Id: " + r['docId'] + "Score: " + str(r['score']))


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

if __name__ == "__main__":
    main()