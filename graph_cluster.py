import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import sklearn.cluster as skcluster


class GraphCluster:

    def __init__(self, graph):
        self.graph = graph
        self.path_dict = dict()

    def shortest_path_dict(self):
        return nx.all_pairs_dijkstra_path_length(self.graph)

    # Colors nodes based on the labels. The order of the labels must match the order of the nodes
    def plot_graph(self, filename, labels="black", outlier_label=-1):
        if not outlier_label == -1 and not labels == "black":
            labels = [outlier_label if x == -1 else x for x in labels]
        plt.figure(num=None, figsize=(10, 10), dpi=1200)
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
        for key1 in keys[:-1]:
            j = i+1
            for key2 in keys[j:]:
                matrix[i][j] = path_dict[key1][key2]
                matrix[j][i] = matrix[i][j]
                j += 1
            i += 1
        if len(path_dict.keys()) < 100:
            print(np.matrix(matrix))
        return np.matrix(matrix)

    # LEGACY CODE: this could offer another solution for clustering disconnected graphs (DBSCAN)
    # The matrix conversion does not handle unconnected graphs.
    def path_dict_to_sparse_matrix(self, path_dict):
        print(path_dict)
        print("items: " + str(path_dict.items()))
        print("values: " + str(path_dict.values()))
        row_ind = []
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

    # dbscan clustering using computing all complete subgraphs separately.
    def cluster_dbscan(self, min_node_threshold=0, epsilon=1.0, sample_min=5):
        graph_list = nx.connected_component_subgraphs(self.graph)
        nr_of_graphs = nx.number_connected_components(self.graph)

        label_list = []
        index_list = []
        label_shifter = 0

        progress_counter = 1
        for subgraph in graph_list:
            print("Progress: " + str(progress_counter) + "/" + str(nr_of_graphs))
            progress_counter += 1
            if len(subgraph) > min_node_threshold:
                # path_dict = nx.all_pairs_shortest_path_length(subgraph)
                path_dict = nx.all_pairs_dijkstra_path_length(subgraph)
                dist_matrix = GraphCluster(self.graph).path_dict_to_matrix(path_dict)
                node_index = sorted(path_dict.keys(), key=int)
                index_list.extend(node_index)  # path_dict.keys()) #sort is not necessary
                db = skcluster.DBSCAN(eps=epsilon, metric="precomputed", min_samples=min([sample_min, len(node_index)])).fit(dist_matrix)
                for label in db.labels_:
                    if label == -1:
                        label_list.append(label)
                    else:
                        label_list.append(label+label_shifter)
                unique_labels = set(db.labels_)
                label_shifter += len(remove_all_from_list(unique_labels, -1))
                print("Ids: " + str(len(path_dict.keys())) + " : " + str(sorted(path_dict.keys(), key=int)))
                print("labels: " + str(len(db.labels_)) + " : " + str(db.labels_))
                #print("Label_shifter: " + str(label_shifter) + " Labels: " + str(self.remove_all_from_list(unique_labels, -1)) + "real: " + str(unique_labels))
            else:
                label_list.extend([label_shifter]*len(subgraph))
                index_list.extend(nx.nodes(subgraph))
                label_shifter += 1
        label_list = [x for _, x in sorted(zip(index_list, label_list), key=lambda x: int(x[0]))]
        return label_list

    # FIX: dissconnected graph and  k estimation
    def cluster_agglomerative(self):
        graph_list = sorted(nx.connected_component_subgraphs(self.graph), key=len, reverse=True)
        # NEED to fix disconnected graph
        shortest_path_dict = nx.all_pairs_shortest_path_length(graph_list[0])
        dist_matrix = GraphCluster(self.graph).path_dict_to_matrix(shortest_path_dict)
        db = skcluster.AgglomerativeClustering(n_clusters=2, affinity="precomputed", linkage="complete").fit(dist_matrix)
        return db.labels_

def remove_all_from_list(el_list, element):
    result = []
    for el in el_list:
        if not el == element:
            result.append(el)
    return result
