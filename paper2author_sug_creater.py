import pickle
from atm_similarity import atm_similarity
import csv
import numpy as np

"""This function creates author suggestions based on the authors of a paper."""
def create_paper2author_sug():
    paper_author_list = load_paper_authors()
    author_id_list = load_authors_id()
    authorsim = atm_similarity()
    result_list = []
    for paper in [p for p in paper_author_list if len(p) > 2]:
        author_sim_list = []
        authors_of_paper = [author_id_list.index(a) for a in paper[1:]]
        for author in authors_of_paper:
            try:
                author_sim_list.append(authorsim.get_list(author))
            except ValueError:
                print("Author id: " + str(author) + " is missing")
        average_vector = combine_vectors(author_sim_list)
        top_matches, _ = authorsim.get_top_authors_vector(average_vector) #, exclude=authors_of_paper)
        top_matches = [paper[0]] + [author_id_list[author_index] for author_index in top_matches]
        result_list.append(top_matches)
    print(result_list)
    save_paper_2_author_sug(result_list)


"""This function loads all the papers with their authors to a list[paperd, [authorslist]]"""
def load_paper_authors2():
    paper_author_list = []
    try:
        with open('data/paper_authors.csv', 'r', encoding="utf8") as csvfile:
            graph_reader = csv.reader(csvfile, delimiter=',')
            next(graph_reader)
            for row in graph_reader:
                paper_author_list.append(row[1:])
    except EnvironmentError:
        print("Failed to open data/paper_authors.csv")
    return paper_author_list


"""This function loads all the papers with their authors to a list[paperd, authors_id1, authors_id2, ...]"""
def load_paper_authors():
    paper_author_list = []
    with open('data/paper_authors.csv', 'r', encoding="utf8") as csvfile:
        graph_reader = csv.reader(csvfile, delimiter=',')
        next(graph_reader)
        paper_id = -1
        for row in graph_reader:
            if paper_id == row[1]:
                interList = paper_author_list.pop()
                interList.append(row[2])
                paper_author_list.append(interList)
            else:
                paper_id = row[1]
                paper_author_list.append([row[1], row[2]])   # set paper name
    return paper_author_list


"""This function loads all the author id's to a list[author_id]"""
def load_authors_id():
    author_id_list = []
    try:
        with open('data/authors.csv', 'r', encoding="utf8") as csvfile:
            graph_reader = csv.reader(csvfile, delimiter=',')
            next(graph_reader)
            for row in graph_reader:
                author_id_list.append(row[0])
    except EnvironmentError:
        print("Failed to open data/authors.csv")
    return author_id_list


"""This function combines a list of vectors using the average. (Vectors must be the same size, and must contain at least
    1 row) similar to numpy matrix.mean(0)"""
def combine_vectors_average(vector_list):
    average_vector = []
    if len(vector_list) > 0:
        v_length = len(vector_list[0])
        for i in range(0, v_length):
            average_vector.append(np.mean([row[i] for row in vector_list]))
    return average_vector


"""Combines the vectors using max or mean"""
def combine_vectors(vector_list, type="max"):
    combined_vector = []
    if len(vector_list) > 0:
        v_length = len(vector_list[0])
        for i in range(0, v_length):
            if type is "max":
                combined_vector.append(max([row[i] for row in vector_list]))
            if type is "mean":
                combined_vector.append(np.mean([row[i] for row in vector_list]))
    return combined_vector


""""This function saves the result to a csv file"""
def save_paper_2_author_sug(result_list, filename="data_atm/paper_2_author_sug_max_with_small.csv"):
    try:
        with open(filename, 'w', encoding="utf8", newline='') as csv_file:
            wr = csv.writer(csv_file, delimiter=',')
            wr.writerows(result_list)
    except EnvironmentError:
        print("ERROR: saving labels to cache failed.")


"""This function searches the paper-author relation from load_paper_authors() to find the author of one paper"""
def get_author_by_paper(paper_authors, paper_id):
    for paper in paper_authors:
        if paper[0] == paper_id:
            return paper[1:]
    return []


"""This function evaluates the suggestions csv"""
def evaluate_suggestions(filename):
    papers = load_paper_authors()
    ratio = []
    try:
        with open(filename, 'r', encoding="utf8") as csvfile:
            graph_reader = csv.reader(csvfile, delimiter=',')
            for row in graph_reader:
                authors = get_author_by_paper(papers, row[0])
                ratio.append(len(set(authors).intersection(row[1:])) / len(authors))

    except EnvironmentError:
        print("Failed to open data/authors.csv")
    print("Median ratio of author found as suggestion: " + str(np.median(ratio)) + " Avg: " + str(np.mean(ratio)))
    return ratio


if __name__ == "__main__":
    evaluate_suggestions("data_atm/paper_2_author_sug_max_with_small.csv")
    #create_paper2author_sug()