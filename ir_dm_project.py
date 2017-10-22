from indexer import Indexer
#from lda import LDA
from author_clustering import AuthorClustering
from graph_cluster import GraphCluster
import networkx as nx
import datetime
from ir_model import IRModel
import nltk
import re


def main():

    a = AuthorClustering(cache_enabled=True)
    print(len(a.nodes))
    #l1 = ["5", "1", "10", "2", "6"]
    #l2 = [1,2,3,4,5]
    #print(sorted(zip(l1,l2), key=lambda x: int(x[0])))
    #for l in set(a.labels):
    #    print("label: " + str(l) + " count: " + str(a.labels.count(l)))
    GraphCluster(a.author_graph).plot_graph("final3", labels=a.labels, outlier_label=125)
    #print("lab: " + str([n for (n,l) in zip(a.nodes, a.labels) if l == 0]))
    #print(len([n for (n,l) in zip(a.nodes, a.labels) if l == 0]))
    #big_g = sorted(nx.connected_component_subgraphs(a.author_graph), key=len, reverse=True)[0]
    #print("Big: " + str(len(big_g)) + ":" + str(sorted(nx.nodes(big_g),key=int)))
    #print("all: " + str(len(nx.nodes(a.author_graph))) + str(nx.nodes(a.author_graph)))
    #print("all: " + str(len(a.nodes)) + str(a.nodes))


    #print(a.find_authors_by_paper("3"))

    #query = "a:\"John de Beer\""
    #pattern = re.compile("[a,y,t]:\"[a-zA-Z ]+\"")
    #params = pattern.findall(query)
    #print(params)



    # m = IRModel.get_instance()
    # body_results = m.indexer.search("neural")
    # title_results = m.indexer.search("Constrained Differential Optimization", 'title')


    #print(m.authors.find_authors_by_paper(results[1]['docId']))

    # topics = m.lda.get_topics_for_document(results[0]['docId'])
    #print("doc_id: " + results[1]['docId'])
    # for result in results:
    #     print("Doc: " +str(result['docId'])+"Score: "+ str(result['score']))

def remove_all_form_list(el_list, element):
    result = []
    for el in el_list:
        if not el == element:
            result.append(el)
    return result

if __name__ == "__main__":
    main()