import csv
import pickle
import numpy as np
from math import log

import matplotlib.pyplot as plt

from similarity.wed import fast_wdist
from similarity.wpcc import wpearson
from similarity.cosine import get_cosine


class atm_similarity:
    def __init__(self, n_authors=10, n_topics=10, type='cosine'):
        # Laad lijst van scores

        with open('data/authors.csv', 'r') as f:
            reader = csv.reader(f)
            next(reader)
            self.author = list(reader)

        self.author.append(['N/A', 'N/A'])

        with open('data_atm/score_list.pkl', 'rb') as f:
            score_list = pickle.load(f)
        self.score_list = np.array(score_list)

        self.N = n_topics
        self.X = n_authors
        self.type = type

    def get_top_indexes(self, vector):

        sorted_list = list(np.argsort(vector)[::-1][:self.N])
        order = []
        for x in range(len(sorted_list)):
            if vector[sorted_list[x]] >= 1:
                order.append(sorted_list[x])

        return order

    def get_indexes_top_authors(self, sim_scores, amount):
        if self.type == 'pearson' or 'cosine':
            x = np.argsort(sim_scores)[::-1][:amount]
        else:
            x = np.argsort(sim_scores)[:amount]

        return x

    """Returns the author topic vector for given an author index. (author_id is not the same as author index)"""
    def get_list(self, auth_index):
        return self.score_list[auth_index]

    def get_weights(self, n):
        weights = []
        for x in range(n):
            weight = log(n + 1 - x, n + 1)
            weights.append(weight)
        return weights

    def get_similarity(self, auth_index1, auth_index2):
        vector1 = self.get_list(auth_index1)
        return self.get_similarity_vector_author(vector1, auth_index2)

    def get_similarity_vector_author(self, vector1, auth_index2):
        vector2 = self.get_list(auth_index2)

        order = self.get_top_indexes(vector1)

        vector1_adapted = []
        vector2_adapted = []

        for x in range(len(order)):
            vector1_adapted.append(vector1[order[x]])
            vector2_adapted.append(vector2[order[x]])

        weights = self.get_weights(len(order))

        try:
            if self.type == 'pearson':
                similarity = wpearson(vector1_adapted, vector2_adapted, weights, 8)
            elif self.type == 'euclid':
                similarity = fast_wdist(np.asarray(vector1_adapted), np.asarray(vector2_adapted), np.asarray(weights))
                similarity = sum(similarity)
            elif self.type == 'cosine':
                similarity = get_cosine(vector1_adapted, vector2_adapted, weights)
            else:
                print("NO VALID SIMILARITY MEASURE, USE PEARSON")
                similarity = wpearson(vector1_adapted, vector2_adapted, weights)
        except:
            similarity = 0

        return similarity

    """This function is finds all the similarities of a given author index.
        (can be reduced using get_all_similarities_vector)"""
    def get_all_similarities(self, auth_index1):
        sim_scores = []
        for auth_index2 in range(len(self.score_list)):
            if auth_index2 == 8653:
                sim_scores.append(0)
            else:
                sim_scores.append(self.get_similarity(auth_index1, auth_index2))
        return sim_scores

    """This function is finds all the similarities of a given vector"""
    def get_all_similarities_vector(self, sim_vector):
        sim_scores = []
        for auth_index2 in range(len(self.score_list)):
            if auth_index2 == 8653:
                sim_scores.append(0)
            else:
                sim_scores.append(self.get_similarity_vector_author(sim_vector, auth_index2))
        return sim_scores

    """This function is gives the top similarities and author indices(?) of a given author index.
    (can be reduced using get_all_similarities_vector)"""
    def get_top_authors(self, auth_index):
        sim_scores = self.get_all_similarities(auth_index)
        top_authors = list(self.get_indexes_top_authors(sim_scores, self.X + 1))
        top_scores = []
        for author in top_authors:
            top_scores.append(sim_scores[author])

        del top_scores[0], top_authors[0]

        return top_authors, top_scores

    """This function is gives the top similarities and author indices(?) of a given author top similarity"""
    def get_top_authors_vector(self, sim_vector, exclude=[]):
        sim_scores = self.get_all_similarities_vector(sim_vector)
        for author_index in exclude:
            sim_scores[author_index] = 0
        top_authors = list(self.get_indexes_top_authors(sim_scores, self.X))
        top_scores = []
        for author in top_authors:
            top_scores.append(sim_scores[author])

        return top_authors, top_scores

    def create_bar_plot(self, author_id, n_authors=2, show_plot=False):
        top_authors, top_scores = self.get_top_authors(author_id)
        top_topics = list(self.get_top_indexes(self.get_list(author_id)))
        score_list = self.score_list
        li = []
        row = []
        for topic_index in top_topics:
            row.append(score_list[author_id][topic_index])
        li.append(row)

        for n in range(n_authors):
            row = []
            for topic_index in top_topics:
                row.append(score_list[top_authors[n]][topic_index])
            li.append(row)

        li_n = []
        for n in range(n_authors + 1):
            if self.type == 'pearson' or self.type == 'cosine':
                su = sum(li[n])
            else:
                su = 1
            row = [x / su for x in li[n]]

            li_n.append(row)

        N = len(top_topics)
        ind = np.arange(N)  # the x locations for the groups
        width = 0.30 - n_authors * 0.03  # the width of the bars

        fig = plt.figure()

        ax = fig.add_subplot(111)

        fig.suptitle(self.author[author_id][1], fontsize=14, fontweight='bold')

        ax.set_title(str(n_authors) + " most similar authors using: " + self.type + " similarity")
        colour = ['b', 'g', 'r', 'c', 'm', 'y', 'k', 'w']
        rects = []
        authors_names = []
        authors_names.append(self.author[author_id][1])
        for x in range(n_authors):
            la = self.author[top_authors[x]][1] + ": " + str(round(top_scores[x], 3))
            authors_names.append(la)
        for n in range(n_authors + 1):
            row = ax.bar(ind + n * width, li_n[n], width, color=colour[n], label=authors_names[n])
            rects.append(row)

        ax.set_ylabel('Scores')
        ax.set_xlabel('Topic ID')
        ax.set_xticks(ind + width)
        ax.set_xticklabels(top_topics[0:N])

        legend = ax.legend(loc='upper right', shadow=True)

        # The frame is matplotlib.patches.Rectangle instance surrounding the legend.
        frame = legend.get_frame()
        frame.set_facecolor('0.90')

        # Set the fontsize
        for label in legend.get_texts():
            label.set_fontsize('small')

        for label in legend.get_lines():
            label.set_linewidth(1.5)

        if show_plot == True:
            plt.show()

        return fig

#with open('data_atm/score_list.pkl', 'rb') as f:
#    score_list = pickle.load(f)
#for x in range(10):
#    print(score_list[x])


# with open('data_atm/csvdata.csv', 'r') as f:
#     reader = csv.reader(f)
#     data = list(reader)
#
# id_list = []
# p_list = []
# h_list = []
# for x in range(len(data)):
#     id_list.append(data[x][0])
#     h_list.append(data[x][1])
#     p_list.append(data[x][2])
#
#
# sim1 = atm_similarity(10, 10, 'cosine')
#
# sim_list = []
# all_data = []
# for x in range(8000, len(id_list)):
#     if x % 100 == 0:
#         print(x)
#     id_indexes, scores = sim1.get_top_authors(x)
#     ids = []
#     for index in id_indexes:
#         ids.append(int(id_list[index]))
#
#     row = []
#     for y in range(len(id_indexes)):
#         row.append([ids[y], scores[y]])
#     sim_list.append(row)
#
#     all_data.append([id_list[x], p_list[x], h_list[x], row])
#     if x % 1000 == 0:
#         with open('data_atm/bart_data.csv', 'w', newline='') as csvfile:
#             writer = csv.writer(csvfile)
#             writer.writerows(all_data)
#
#
# with open('data_atm/bart_data.csv', 'w', newline='') as csvfile:
#     writer = csv.writer(csvfile)
#     writer.writerows(all_data)
#

# sim_list = []
    # # rand = random.sample(range(0, len(sim1.author)), 3)
# for x in range(100, 150):
#     ids, scores = sim1.get_top_authors(x)
#
#     sim_list.append([ids, scores])
#
#     if x % 20 == 0:
#         print(x)
#
#     if x % 10 == 0:
#         filename = "C:/Users/Bart/Desktop/Figures/figure_" + sim1.type + str(x)
#         fig = sim1.create_bar_plot(x, 5)
#         fig.savefig(filename)
