import pickle
from atm_similarity import atm_similarity
import csv
import numpy as np
from indexer.database import db_handler as db

"""This function creates author suggestions based on the authors of a paper."""
def create_paper2author_sug():
    paper_author_list = load_paper_authors()
    author_id_list = load_authors_id()
    authorsim = atm_similarity()
    result_list = []
    for paper in [p for p in paper_author_list if len(p) > 2]:
        author_sim_list = []
        authors_of_paper = [author_id_list.index(a) for a in paper[1:]]  #might throw an error
        for author in authors_of_paper:
                author_sim_list.append(authorsim.get_list(author))
        average_vector = combine_vectors(author_sim_list)
        top_matches, _ = authorsim.get_top_authors_vector(average_vector) #, exclude=authors_of_paper)
        top_matches = [paper[0]] + [author_id_list[author_index] for author_index in top_matches]
        result_list.append(top_matches)
    print(result_list)
    save_rows_to_csv(result_list)


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
                inter_list = paper_author_list.pop()
                inter_list.append(row[2])
                paper_author_list.append(inter_list)
            else:
                paper_id = row[1]
                paper_author_list.append([row[1], row[2]])   # set paper name
    return paper_author_list


""""Load csv rows"""
def load_csv_rows(filename):
    row_list = []
    try:
        with open(filename, 'r', encoding="utf8") as csvfile:
            graph_reader = csv.reader(csvfile, delimiter=',')
            for row in graph_reader:
                row_list.append(row)
    except EnvironmentError:
        print("Failed to open "+filename)
    return row_list


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


"""Load pickle"""
def load_obj(filename):
    try:
        with open(filename, 'rb') as f:
            return pickle.load(f)
    except EnvironmentError:
        print("ERROR: Pickle " + filename + " could not be opened.")
    return None

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
            column = [row[i] for row in vector_list]
            if type is "max":
                combined_vector.append(max(column))
            if type is "mean":
                combined_vector.append(np.mean(column))
    return combined_vector


""""This function saves the result to a csv file"""
def save_rows_to_csv(result_list, filename="data_atm/paper_2_author_sug_max_with_small.csv"):
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
def p2a_suggestions_ratio(filename):
    papers = load_paper_authors()
    save_rows_to_csv(papers, filename="test_output.csv")
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

def create_suggested_author_2_author():
    author_id_list = load_authors_id()
    authorsim = atm_similarity()
    suggestion_list = []
    for i, author in enumerate(author_id_list):
        top_matches, _ = authorsim.get_top_authors(i)
        top_matches = [author] + [author_id_list[author_index] for author_index in top_matches]
        suggestion_list.append(top_matches)
    print(suggestion_list)
    save_rows_to_csv(suggestion_list, filename="data_atm/author_2_author_sug.csv")

def create_author_to_paper_csv():
    author_id_list = load_authors_id()
    papers = load_paper_authors()
    result_list = []
    for author in author_id_list:
        author_papers = [author]
        for paper in papers:
            if author in paper[1:]:
                author_papers.append(paper[0])
        result_list.append(author_papers)
    print(result_list)
    save_rows_to_csv(result_list, filename="data_atm/papers_of_author.csv")


def get_title_of_paper(paper_id):
    return db.DbHandler().get_title_by_paper_id(paper_id)


"""This function tells if two authors worked together. (can also be done using the dist_dict[a1][a2] < 1)"""
def did_authors_cooperate(author1, author2, author_to_paper):
    a2p_index = [x[0] for x in author_to_paper]
    papers_1 = author_to_paper[a2p_index.index(author1)]
    papers_2 = author_to_paper[a2p_index.index(author2)]
    return len(set(papers_1).intersection(papers_2)) > 0


"""This function gives a list of titles for each author."""
def get_titles_of_authors(authors):
    author_to_paper = load_csv_rows("data_atm/papers_of_author.csv")
    result_list = []
    a2p_index = [x[0] for x in author_to_paper]  #Can also load this from authors
    for author in authors:
        print("Author: " + author)
        title_list = [author]
        author_papers = (author_to_paper[a2p_index.index(author)])[1:]
        for paper in author_papers:
            title = str(get_title_of_paper(paper))
            title_list.append(title)
            print("  "+str(title))
    return result_list

""""This function gives the part of authors that cooperated with author_1"""
def cooperation_ratio(authors):
    if len(authors) < 2:
        return -1
    author_to_paper = load_csv_rows("data_atm/papers_of_author.csv")
    cooperated = 0.0
    for author in authors[1:]:
        if did_authors_cooperate(authors[0], author, author_to_paper):
            cooperated += 1.0
    return cooperated/(len(authors)-1.0)

def give_overall_coop_ratio():
    a2a_suggestions = load_csv_rows("data_atm/author_2_author_sug.csv")
    total = []
    for row in a2a_suggestions:
        coop_ratio = cooperation_ratio(row)
        if not coop_ratio is -1:
            total.append(coop_ratio)
    print("Mean cooperation ratio: " + str(np.mean(total)))
    print("Median cooperation ratio: " + str(np.median(total)))

def average_distance_author_to_sug():
    a2a_suggestions = load_csv_rows("data_atm/author_2_author_sug.csv")
    path_dict = load_obj("data/path_dict.pkl")
    all_sug_distances = []
    nr_unconnected = 0
    total_sug = 0
    for sugs in a2a_suggestions:
        for sug in sugs[1:]:
            try:
                all_sug_distances.append(path_dict[sugs[0]][sug])
            except KeyError:
                nr_unconnected += 1
                print(str(sugs[0]) + " and " + sug + " are not connected.")
            total_sug += 1

    print("Ratio of disconnected suggestions: " + str(nr_unconnected/total_sug))
    print("Mean distance: " + str(np.mean(all_sug_distances)))
    print("Median distance: " + str(np.median(all_sug_distances)))


if __name__ == "__main__":
    #get_titles_of_authors(["1"])
    #print(cooperation_ratio(["1", "971", "1730", "168", "901", "308"]))
    #give_overall_coop_ratio()
    #get_titles_of_authors(["1", "971", "1730", "168", "901", "308"])
    average_distance_author_to_sug()
    # get_title_of_paper("63")
    # create_author_to_paper_csv()
    # create_suggested_author_2_author()
    # p2a_suggestions_ratio("data_atm/paper_2_author_sug_max_with_small.csv")
    # p2a_suggestions_ratio("data_atm/paper_2_author_sug_max.csv")
    #p2a_suggestions_ratio("data_atm/paper_2_author_sug_avg.csv")
    # create_paper2author_sug()