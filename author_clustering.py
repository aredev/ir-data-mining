import csv
import networkx as nx
import pickle
import db_handler as db
import graph_cluster as gc
#from ir_model import IRModel

class AuthorClustering:

    def __init__(self, cache_enabled=True, label_cache_filename="data\label_cache.csv"):
        self.LABEL_CACHE = label_cache_filename
        self.author_dict, self.author_graph = self.load_csv()
        self.labels = []
        self.nodes = nx.nodes(self.author_graph)
        if cache_enabled:
            self.labels = self.load_label_cache()
            self.path_dict = self.load_obj("path_dict")

        if not cache_enabled or not len(self.labels) == len(self.nodes) or self.path_dict is None:
            print("Cache was not enabled or failed. Creating clusters ... This might take a while... (guessing 6min)")
            graph_cluster = gc.GraphCluster(self.author_graph)
            self.labels = graph_cluster.cluster_dbscan(epsilon=1.5, sample_min=10)
            #self.labels = graph_cluster.cluster_agglomerative()
            self.save_labels_csv()
            self.path_dict = graph_cluster.shortest_path_dict()
            self.save_obj(self.path_dict, "path_dict")
        self.cluster_stats()

    def cluster_stats(self):
        unique_clusters = gc.remove_all_from_list(set(self.labels), -1)
        number_of_clusters = len(unique_clusters)
        print("Number of clusters: " + str(number_of_clusters))
        print("Number of outliers: " + str(len(self.find_cluster_by_label(-1))))
        cluster_sizes = sorted([self.labels.count(cs) for cs in unique_clusters], reverse=True)
        if len(cluster_sizes) > 20:
            print("Average cluster size " + str(len(self.labels)/number_of_clusters) + " all sizes: " + str(cluster_sizes[0:20]))
        else:
            print("Average cluster size " + str(len(self.labels) / number_of_clusters) + " all sizes: " + str(
                cluster_sizes))
        dist_averages = []
        for label in unique_clusters:
            dist_averages.append(self.average_distance(self.find_cluster_by_label(label)))


        print("Average distances: " + str(dist_averages))

    def average_distance(self, nodes):
        size = len(nodes)
        if size > 1:
            i = 1
            total_dist = 0
            for node1 in nodes[:-1]:
                j = 0
                for node2 in nodes[i:]:
                    total_dist += 2 * float(self.path_dict[node1][node2])
                    j += 1
                i += 1
            return total_dist/(size*size)
        else:
            return 0

    # This function loads labels as list of integers form the cache
    def load_label_cache(self):
        try:
            with open(self.LABEL_CACHE, 'r', encoding="utf8", newline='') as csvfile:
                label_reader = csv.reader(csvfile, delimiter=',')
                return [int(label) for label in next(label_reader)]
        except EnvironmentError:
            print("ERROR: Cache could not be opened.")
            return []

    # This function returns a list of nodes in the cluster of a given node (excluding the given node).
    # The label_list should be equally long as the node_list
    def find_cluster_of_node(self, search_node):
        node_index = self.nodes.index(search_node)
        match_label = self.labels[node_index]
        return [node for node, label in zip(self.nodes, self.labels) if label == match_label and not node == search_node]

    def find_cluster_by_label(self, match_label):
        return [node for node, label in zip(self.nodes, self.labels) if label == match_label]

    # This function writes a list of labels to file.
    def save_labels_csv(self):
        try:
            with open(self.LABEL_CACHE, 'w', encoding="utf8", newline='') as cache_file:
                wr = csv.writer(cache_file, delimiter=',')
                labels = [str(label) for label in self.labels]
                wr.writerow(labels)
        except EnvironmentError:
            print("ERROR: saving labels to cache failed.")

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
                            #print(str(row[2]) + " -> " +str(author) + " prev weight: " + str(weight/2))
                        else:
                            author_graph.add_edge(author, row[2], weight=1)

                else:
                    coop_authors = []
                    paper_id = row[1]
                coop_authors.append(row[2])

        return author_dict, author_graph

    # This function finds the nearest neighbour of an node excluding a set of nodes.
    def find_nearest_neighbour(self, node, excluding):
        neighbour_dict = self.path_dict[node]
        closest = node
        neighbours = [n for n in neighbour_dict.keys() if n not in excluding]
        for neighbour in neighbours:
            if (neighbour_dict[closest] > neighbour_dict[neighbour] or closest == node) and not neighbour == node:
                closest = neighbour
        return closest

    def total_dist(self, nodes, node):
        dist = 0.0
        for neighbour in nodes:
            dist += self.path_dict[neighbour][node]
        return dist

    # This funtion returns a list with suggestions based on the labels (in order from low to high).
    # WARNING: This function might return None if none of the authors in the cluster has a successful pagerank.
    # TODO: Can't reach scoreFunction in model since author_clustering is in model. Make function static?
    """def precompute_all_cluster_suggestions(self):
    m = IRModel.get_instance() #Is this possible?
    print("precomputing cluster suggestions...")
    all_clusters = sorted(gc.remove_all_from_list(set(self.labels), -1))
    suggestion_list = []
    for cluster_label in all_clusters:
        suggestion_list.append(m.reputation_scores.get_author_with_highest_reputation_score(self.find_cluster_by_label(cluster_label)))
    print(suggestion_list)"""

    # This function finds the pairwise nearest neighbours for a group of authors (excluding already found authors in the
    # process. Pairwise nearest neighbour might return different results based on the order of the query authors.
    def find_authors_by_paper(self, paper_id):
        paper_authors = db.DbHandler().get_authors_by_paper_id(paper_id)
        result_authors = []
        for author in paper_authors:
            print(result_authors+paper_authors)
            closest = self.find_nearest_neighbour(author, result_authors+paper_authors)
            if not closest == author:
                result_authors.append(closest)
        return [db.DbHandler().get_author_by_id(pa) for pa in paper_authors], [db.DbHandler().get_author_by_id(ra) for ra in result_authors]

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

    def save_obj(self, obj, name):
        try:
            with open('data/'+ name + '.pkl', 'wb') as f:
                pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)
        except EnvironmentError:
            print("ERROR: Pickle could not be saved.")

    def load_obj(self, name):
        try:
            with open('data/' + name + '.pkl', 'rb') as f:
                return pickle.load(f)
        except EnvironmentError:
            print("ERROR: Pickle could not be opened.")
        return None
