import csv
import networkx as nx
import graph_cluster as gc


class AuthorClustering:

    def __init__(self, cache_enabled=False, label_cache_filename="label_cache.csv"):
        self.LABEL_CACHE = label_cache_filename

        # TESTING ENABLED
        self.author_dict, self.author_graph = self.load_csv()
        self.labels = []
        # self.author_graph = self.make_fake_graph()
        if cache_enabled:
            self.labels = self.load_label_cache()
        if not cache_enabled or not len(self.labels) == len(nx.nodes(self.author_graph)):
            self.labels = gc.GraphCluster(self.author_graph).cluster_dbscan()
            self.save_labels_csv(self.labels)
        print(str(len(self.labels)) + " labels: " + str(self.labels))
        print(str(len(nx.nodes(self.author_graph))) + " nodes: " + str(nx.nodes(self.author_graph)))
        gc.GraphCluster(self.author_graph).plot_graph("dummy", self.labels)

    # The load csv function reads all the authors and enters them sorted in the graph.
    # This function assumes that there are no edges with unknown nodes. This could cause the nodes to be unsorted.
    def load_csv(self):
        author_dict = {}
        author_graph = nx.Graph()
        with open('data/authors.csv', 'r', encoding="utf8") as csvfile:
            author_reader = csv.reader(csvfile, delimiter=',')
            author_list = []
            next(author_reader)
            for row in author_reader:
                author_dict[row[0]] = row[1]
                author_list.append(row[0])
            author_list = sorted(author_list, key=int)
            for author in author_list:
                author_graph.add_node(author)

        # Assumption: the list is ordered based on the paper id.
        with open('data/paper_authors.csv', 'r', encoding="utf8") as csvfile:
            graph_reader = csv.reader(csvfile, delimiter=',')
            coop_authors = []
            paper_id = -1
            for row in graph_reader:
                if paper_id == row[1]:
                    for author in coop_authors:
                        if author_graph.has_edge(author, row[2]):
                            weight = author_graph.get_edge_data(author, row[2])["weight"]

                            author_graph.add_edge(author, row[2],
                                                  weight=weight / 2)  # TODO: investigate effect of this weighting
                        else:
                            author_graph.add_edge(author, row[2], weight=1)

                else:
                    coop_authors = []
                    paper_id = row[1]
                coop_authors.append(row[2])

        return author_dict, author_graph

    # This function writes a list of labels to file.
    def save_labels_csv(self, labels):
        with open(self.LABEL_CACHE, 'w', encoding="utf8", newline='') as cache_file:
            wr = csv.writer(cache_file, delimiter=',')
            labels = [str(label) for label in labels]
            wr.writerow(labels)

    # This function loads labels as list of integers form the cache
    def load_label_cache(self):
        with open(self.LABEL_CACHE, 'r', encoding="utf8", newline='') as csvfile:
            label_reader = csv.reader(csvfile, delimiter=',')
            return [int(label) for label in next(label_reader)]

    # This function returns a list of nodes in the cluster of a given node (including the given node).
    # The label_list should be equally long as the node_list
    def find_cluster_of_node(self, node, node_list, label_list):
        node_index = node_list.index(node)
        match_label = label_list[node_index]
        return [node for node, label in zip(node_list, label_list) if label == match_label]

    # This function is for quick testing. It can be removed in the final version.
    def make_fake_graph(self):
        dummy_graph = nx.Graph()
        dummy_graph.add_nodes_from([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20])

        dummy_graph.add_edge(1, 2, weight=1)
        dummy_graph.add_edge(1, 3, weight=1)
        dummy_graph.add_edge(1, 4, weight=1)
        dummy_graph.add_edge(1, 5, weight=1)
        dummy_graph.add_edge(2, 3, weight=1)
        dummy_graph.add_edge(2, 4, weight=1)
        dummy_graph.add_edge(2, 5, weight=1)
        dummy_graph.add_edge(3, 4, weight=1)
        dummy_graph.add_edge(3, 5, weight=1)
        dummy_graph.add_edge(4, 5, weight=1)
        dummy_graph.add_edge(11, 12, weight=1)
        dummy_graph.add_edge(11, 13, weight=1)
        dummy_graph.add_edge(11, 14, weight=1)
        dummy_graph.add_edge(11, 15, weight=1)
        dummy_graph.add_edge(12, 13, weight=1)
        dummy_graph.add_edge(12, 14, weight=1)
        dummy_graph.add_edge(12, 15, weight=1)
        dummy_graph.add_edge(13, 14, weight=1)
        dummy_graph.add_edge(13, 15, weight=1)
        dummy_graph.add_edge(14, 15, weight=1)
        dummy_graph.add_edge(1, 11, weight=10)
        dummy_graph.add_edge(16, 17, weight=1)
        dummy_graph.add_edge(16, 18, weight=1)
        dummy_graph.add_edge(16, 19, weight=1)
        dummy_graph.add_edge(16, 20, weight=1)
        dummy_graph.add_edge(17, 18, weight=1)
        dummy_graph.add_edge(17, 19, weight=1)
        dummy_graph.add_edge(17, 20, weight=1)
        return dummy_graph

