import pickle
from atm_similarity import atm_similarity
import csv
import numpy as np
from indexer.database import db_handler as db
from sklearn import preprocessing
import matplotlib.pyplot as plt
from random import randint
from scipy.stats.stats import pearsonr

def create_paper2author_sug(filename="data_atm/paper_2_author_sug.csv", type="max", normalize=False):
    """This function creates author suggestions based on the authors of a paper."""
    paper_author_list = load_paper_authors()
    author_id_list = load_authors_id()
    authorsim = atm_similarity()
    result_list = []
    for paper in paper_author_list: #[p for p in paper_author_list if len(p) > 2]:
        author_sim_list = []
        authors_of_paper = [author_id_list.index(a) for a in paper[1:]]  #might throw an error

        if type == "pairwise":
            top_matches = compute_highest_pairwise_matches(authorsim, authors_of_paper)
        else:
            for author in authors_of_paper:
                author_sim_list.append(authorsim.get_list(author))
            average_vector = combine_vectors(author_sim_list, type=type, normalize=normalize)
            top_matches, _ = authorsim.get_top_authors_vector(average_vector)  # , exclude=authors_of_paper)

        top_matches = [paper[0]] + [author_id_list[author_index] for author_index in top_matches]
        #print(top_matches)
        result_list.append(top_matches)
    print(result_list)
    save_rows_to_csv(result_list, filename=filename)


def create_author_2_author_sug(top=10):
    author_id_list = load_authors_id()
    authorsim = atm_similarity(n_authors=top)
    suggestion_list = []
    for i, author in enumerate(author_id_list):
        top_matches, _ = authorsim.get_top_authors(i)
        top_matches = [author] + [author_id_list[author_index] for author_index in top_matches]
        suggestion_list.append(top_matches)
    print(suggestion_list)
    save_rows_to_csv(suggestion_list, filename="data_atm/author_2_author_sug_top" + str(top) + ".csv")


def compute_highest_pairwise_matches(authorsim, authors_of_paper):
    """Computes the top_matches based on the highest pairwise sum of similarity"""
    total_similarity = np.zeros(len(authorsim.author))
    for author in authors_of_paper:
        total_similarity += np.asarray(authorsim.get_all_similarities(author))
    #print(total_similarity)
    best = np.argsort(total_similarity)[::-1][:10]
    #print("Indices: "+str(best))
    #print("Values: "+str([total_similarity[b] for b in best]))
    return best


def load_paper_authors2():
    """This function loads all the papers with their authors to a list[paperd, [authorslist]]"""
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


def load_paper_authors():
    """This function loads all the papers with their authors to a list[paperd, authors_id1, authors_id2, ...]"""
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


def load_csv_rows(filename):
    """"Load csv rows"""
    row_list = []
    try:
        with open(filename, 'r', encoding="utf8") as csvfile:
            graph_reader = csv.reader(csvfile, delimiter=',')
            for row in graph_reader:
                row_list.append(row)
    except EnvironmentError:
        print("Failed to open "+filename)
    return row_list


def load_authors_id():
    """This function loads all the author id's to a list[author_id]. (an UNKOWN author is added at the end)"""
    author_id_list = []
    try:
        with open('data/authors.csv', 'r', encoding="utf8") as csvfile:
            graph_reader = csv.reader(csvfile, delimiter=',')
            next(graph_reader)
            for row in graph_reader:
                author_id_list.append(row[0])
    except EnvironmentError:
        print("Failed to open data/authors.csv")
    author_id_list.append("UNKOWN")
    return author_id_list


def load_obj(filename):
    """Load pickle"""
    try:
        with open(filename, 'rb') as f:
            return pickle.load(f)
    except EnvironmentError:
        print("ERROR: Pickle " + filename + " could not be opened.")
    return None


def combine_vectors(vector_list, type="max", normalize=False):
    """Combines the vectors using max or mean"""
    combined_vector = []
    if len(vector_list) > 0:
        v_length = len(vector_list[0])
        if normalize:
            vector_list = [(preprocessing.normalize(np.asarray(row).reshape(1, -1))*10000).flatten() for row in vector_list]
        for i in range(0, v_length):

            column = [row[i] for row in vector_list]
            if type is "max":
                combined_vector.append(max(column))
            if type is "mean":
                combined_vector.append(np.mean(column))
            if type is "add":
                combined_vector.append(sum(column))
    return combined_vector


def save_rows_to_csv(result_list, filename="data_atm/paper_2_author_sug_max_with_small.csv"):
    """This function saves the result to a csv file"""
    try:
        with open(filename, 'w', encoding="utf8", newline='') as csv_file:
            wr = csv.writer(csv_file, delimiter=',')
            wr.writerows(result_list)
    except EnvironmentError:
        print("ERROR: saving labels to cache failed.")


def get_author_by_paper(paper_authors, paper_id):
    """This function searches the paper-author relation from load_paper_authors() to find the author of one paper"""
    for paper in paper_authors:
        if paper[0] == paper_id:
            return paper[1:]
    return []


def p2a_suggestions_ratio(filename):
    """This function evaluates the suggestions csv"""
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


def did_authors_cooperate(author1, author2, author_to_paper):
    """This function tells if two authors worked together. (can also be done using the dist_dict[a1][a2] < 1)"""
    a2p_index = [x[0] for x in author_to_paper]
    papers_1 = author_to_paper[a2p_index.index(author1)]
    papers_2 = author_to_paper[a2p_index.index(author2)]
    return len(set(papers_1).intersection(papers_2)) > 0


def get_titles_of_authors(authors):
    """This function gives a 2D list of titles for each author. Input uses a list of author IDs"""
    author_to_paper = load_csv_rows("data_atm/papers_of_author.csv")
    result_list = []
    a2p_index = [x[0] for x in author_to_paper]  #Can also load this from authors
    papers_auth0 = (author_to_paper[a2p_index.index(authors[0])])[1:]
    for author in authors:
        print("Author id: " + author)
        title_list = [author]
        author_papers = (author_to_paper[a2p_index.index(author)])[1:]
        for paper in author_papers:
            title = str(get_title_of_paper(paper))
            title_list.append(title)
            if paper in papers_auth0 and author != authors[0]:
                print("  "+str(title)+" (COOPERATED)")
            else:
                print("  "+str(title))
    return result_list


def cooperation_ratio(authors, author_to_paper):
    """This function gives the part of authors that cooperated with author_1"""
    if len(authors) < 2:
        return -1
    cooperated = 0.0
    for author in authors[1:]:
        if did_authors_cooperate(authors[0], author, author_to_paper):
            cooperated += 1.0
    return cooperated/(len(authors)-1.0)


def give_overall_coop_ratio():
    """This gives the cooperation ratio for all the suggestions"""
    a2a_suggestions = load_csv_rows("data_atm/author_2_author_sug.csv")
    author_to_paper = load_csv_rows("data_atm/papers_of_author.csv")
    total = []

    for row in a2a_suggestions:
        coop_ratio = cooperation_ratio(row, author_to_paper)
        if not coop_ratio is -1:
            total.append(coop_ratio)
    print("Mean cooperation ratio: " + str(np.mean(total)))
    print("Median cooperation ratio: " + str(np.median(total)))


def give_complete_graph_coop_ratio():
    """This give the cooperation ratio for every author (not just suggestions, it takes a lot of time)"""
    authors = load_authors_id()[:-1]    # remove the UNKOWN author
    author_to_paper = load_csv_rows("data_atm/papers_of_author.csv")
    total = []
    authors_length = len(authors)
    for progress, author in enumerate(authors):
        temp = authors
        temp.remove(author)
        temp = [author] + temp
        coop_ratio = cooperation_ratio(temp, author_to_paper)
        if not coop_ratio is -1:                # -1 only happens if the list only contains 1 or no authors
            total.append(coop_ratio)
            print("Progress: " + str(progress) + " / " + str(authors_length))
    print("Mean cooperation ratio: " + str(np.mean(total)))
    print("Median cooperation ratio: " + str(np.median(total)))
    save_rows_to_csv(total, filename="data_atm/complete_graph_coop_ratio.csv")


def average_distance_author_to_sug(filename="data_atm/author_2_author_sug_top20.csv", limit=0):
    """Gives the average distance of an list of suggestions, limit restrains the number of suggestions limit 0 is all"""
    a2a_suggestions = load_csv_rows(filename)
    path_dict = load_obj("data/path_dict.pkl")
    all_sug_distances = []
    nr_unconnected = 0
    total_sug = 0
    for sugs in a2a_suggestions:
        if limit > 0:
            sugs = sugs[:limit+1]
        for sug in sugs[1:]:
            try:
                all_sug_distances.append(path_dict[sugs[0]][sug])
            except KeyError:
                nr_unconnected += 1
                #print(str(sugs[0]) + " and " + sug + " are not connected.")
            total_sug += 1
    disconnected_ratio = nr_unconnected/total_sug
    mean = np.mean(all_sug_distances)

    print("Ratio of disconnected suggestions: " + str(disconnected_ratio))
    print("Mean distance: " + str(mean))
    print("Median distance: " + str(np.median(all_sug_distances)))
    return disconnected_ratio, mean


def average_distance_author_to_all():
    """Copy pasta this function calculates average distance between every author"""
    path_dict = load_obj("data/path_dict.pkl")
    authors = load_authors_id()[:-2]  # remove the UNKOWN author?
    all_sug_distances = []
    nr_unconnected = 0
    total_sug = 0
    for author in authors:
        others = authors[:]
        others.remove(author)
        for sug in others:
            try:
                all_sug_distances.append(path_dict[author][sug])
            except KeyError:
                nr_unconnected += 1
                #print(str(author) + " and " + sug + " are not connected.")
            total_sug += 1
    print("Ratio of disconnected authors: " + str(nr_unconnected / total_sug))
    print("Mean distance between all authors: " + str(np.mean(all_sug_distances)))
    print("Median distance between all authors: " + str(np.median(all_sug_distances)))


def distance_similarity_correlation():
    """This function computes the correlation between distance and similarity"""
    path_dict = load_obj("data/path_dict.pkl")
    authors = load_authors_id()[:-1]  # remove the UNKOWN author?
    authorsim = atm_similarity()
    all_distances = []
    all_similarities = []
    nr_unconnected = 0
    total_sug = 0
    for index1, author in enumerate(authors):
        for index2, sug in enumerate(authors):
            if sug != author:
                all_similarities.append(authorsim.get_similarity(index1, index2))
                try:
                    all_distances.append(path_dict[author][sug])
                except KeyError:
                    all_distances.append(100)
                    nr_unconnected += 1
                total_sug += 1
    print("Ratio of disconnected authors: " + str(nr_unconnected / total_sug))
    print("Mean distance between all authors: " + str(np.mean(all_distances)))
    print("Median distance between all authors: " + str(np.median(all_distances)))

    plt.scatter(all_similarities, all_distances)
    plt.ylabel('Distance')
    plt.xlabel('Similarity')
    plt.show()
    plt.clf()
    save_rows_to_csv(zip(all_similarities, all_distances), filename="/data_atm/dist_sim_correlation2.csv")
    print("Correlation: " + str(np.corrcoef(all_similarities, all_distances)[0, 1]))
    print("Pearson correlation: " + str(pearsonr(all_similarities, all_distances)))

def histogram_of_top_suggested_distance(nr_sug=10):
    average_list = []
    discon_ratio_list = []
    for i in range(1, nr_sug+1):
        discon_ratio, mean = average_distance_author_to_sug(limit=i)
        discon_ratio_list.append(discon_ratio)
        average_list.append(mean)
    print(average_list)
    plt.plot(range(1, len(average_list)+1), average_list, 'ro', color="red")

    plt.ylabel('Distance')
    plt.xlabel('Nr top suggestion')
    plt.show()
    plt.clf()

    plt.plot(range(1, len(discon_ratio_list) + 1), discon_ratio_list, 'ro', color="blue")
    plt.ylabel('Disconnected ratio')
    plt.xlabel('Nr top suggestion')
    plt.show()
    plt.clf()


def random_test_sample(a2a_sug_file="data_atm/author_2_author_sug_top10.csv"):
    """This function gives a random test sample"""
    authors = load_authors_id()[:-1]
    a2a_sug = load_csv_rows(filename=a2a_sug_file)

    random_author_index = randint(0, len(a2a_sug)-1)    # Author index instead of id to ensure missing id's
    random_author_id = authors[random_author_index]

    print("SAMPLED AUTHOR: " + str(random_author_id))
    get_titles_of_authors(a2a_sug[random_author_id])

    print("-"*20)

if __name__ == "__main__":


    #get_titles_of_authors(["1"])
    #print(cooperation_ratio(["1", "971", "1730", "168", "901", "308"]))

    #get_titles_of_authors(["1", "971", "1730", "168", "901", "308"])
    #average_distance_author_to_sug()
    #create_author_to_paper_csv()

    #create_author_2_author_sug(top=10)

    #p2a_suggestions_ratio("data_atm/paper_2_author_sug_max_with_small.csv")
    #create_paper2author_sug(filename="data_atm/paper_2_author_sug_add4.csv", type="add")
    #create_paper2author_sug(filename="data_atm/paper_2_author_sug_add_normal5.csv", type="add", normalize=True)

    #distance_similarity_correlation()

    #histogram_of_top_suggested_distance(nr_sug=20)
    #average_distance_author_to_all()
    #give_complete_graph_coop_ratio()

    #create_paper2author_sug(filename="data_atm/paper_2_author_sug_mean.csv", type="mean", normalize=False)
    #create_paper2author_sug(filename="data_atm/paper_2_author_sug_add.csv", type="add", normalize=False)
    #create_paper2author_sug(filename="data_atm/paper_2_author_sug_pairwise.csv", type="pairwise", normalize=False)

    """Evaluation functions"""
    # random_test_sample()
    # give_overall_coop_ratio()
    distance_similarity_correlation()

