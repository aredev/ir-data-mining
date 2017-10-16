import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import sklearn.cluster as skcluster


class GraphCluster:
    i = 10

    def __init__(self, graph):
        self.graph = graph

    # This function should be extended
    def cluster_graph(self):
        return self.graph

    # Colors nodes based on the labels. The order of the labels must match the order of the nodes
    def plot_graph(self, filename, labels="black"):
        pos = nx.spring_layout(self.graph)
        nx.draw_networkx_nodes(self.graph, pos, width=30, node_color=labels, node_size=5, alpha=1)
        nx.draw_networkx_edges(self.graph, pos, width=2, edge_color='r', alpha=1)
        plt.savefig(filename)
        plt.clf()

    # The matrix conversion does not handle unconnected graphs.
    def path_dict_to_matrix(self, path_dict):
        keys = sorted(path_dict.keys(), key=int)
        matrix = np.zeros((len(keys), len(keys)))
        i = 0
        for key1 in keys:
            j = 0
            for key2 in keys:
                matrix[i][j] = path_dict[key1][key2]
                j += 1
            i += 1
        return np.matrix(matrix)

    # LEGACY CODE: this could offer another solution for clustering disconnected graphs (DBSCAN)
    # The matrix conversion does not handle unconnected graphs.
    def path_dict_to_sparse_matrix(self, path_dict):
        print(path_dict)
        print("items: " + str(path_dict.items()))
        print("values: " + str(path_dict.values()))
        row_ind =[]
        col_ind = []
        data = []

        A = nx.adjacency_matrix(self.graph)
        print(A.todense())

        for key1, v in path_dict.items():
            print("v: " + str(v))
            print("key1: " + str(key1))

        """
        row_ind.append(key1)
        col_ind.append(key2)
        data.append(val)
        x = sp.csr_matrix(([1] * len(row_ind), (row_ind, col_ind)))
        """

        #row_ind2 = [k for k, v in path_dict.items() for _ in range(len(v))]
        #col_ind2 = [i for ids in path_dict.values() for i in ids]
        #print("row_ind: " + str(row_ind))
        #print("col_ind: " + str(col_ind))
        #x = sp.csr_matrix(([1] * len(row_ind2), (row_ind2, col_ind2)))
        #print(x)
        #return x

    # DBSCAN with sparce matrix problem with missing indexes (e.g 0)
    def cluster_dbscan2(self):
        path_dict = nx.all_pairs_shortest_path_length(self.graph)
        db = skcluster.DBSCAN(eps=1, metric="precomputed", algorithm="ball trees").fit(self.path_dict_to_sparse_matrix(path_dict))
        return db.labels_

    # dbscan clustering but only for the biggest sub graph.
    # need to fix division of subgraphs.
    # need to fix addition of subgraphs and rearranging the labels.
    def cluster_dbscan(self, min_node_threshold=0):
        graph_list = nx.connected_component_subgraphs(self.graph)
        nr_of_graphs = nx.number_connected_components(self.graph)

        label_list = []
        index_list = []
        label_shifter = 0

        progress_counter = 1
        for subgraph in graph_list:
            print("Progress: " + str(progress_counter) +"/"+ str(nr_of_graphs))
            progress_counter += 1
            if len(subgraph) > min_node_threshold:
                # path_dict = nx.all_pairs_shortest_path_length(subgraph)
                path_dict = nx.all_pairs_dijkstra_path_length(subgraph)
                dist_matrix = GraphCluster(self.graph).path_dict_to_matrix(path_dict)
                db = skcluster.DBSCAN(eps=1, metric="precomputed").fit(dist_matrix)
                index_list.extend(path_dict.keys())
                for label in db.labels_:
                    if label == -1:
                        label_list.append(label)
                    else:
                        label_list.append(label+label_shifter)
                label_shifter += len(np.unique(db.labels_))
            else:
                label_list.extend([label_shifter]*len(subgraph))
                index_list.extend(nx.nodes(subgraph))
                label_shifter += 1
        label_list = [x for _, x in sorted(zip(index_list, label_list))]
        return label_list

    # FIX: dissconnected graph and  k estimation
    def cluster_agglomerative(self):
        graph_list = sorted(nx.connected_component_subgraphs(self.graph), key=len, reverse=True)
        # NEED to fix disconnected graph
        shortest_path_dict = nx.all_pairs_shortest_path_length(graph_list[0])
        dist_matrix = GraphCluster(self.graph).path_dict_to_matrix(shortest_path_dict)
        db = skcluster.AgglomerativeClustering(n_clusters=2, affinity="precomputed", linkage="complete").fit(dist_matrix)
        return db.labels_



