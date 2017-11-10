import pickle
import csv

with open('data_atm/v_list.pkl', 'rb') as f:
    v_list = pickle.load(f)

with open('data_atm/voca.pkl', 'rb') as f:
    voca = pickle.load(f)

with open('data/output.csv', 'r') as f:
    reader = csv.reader(f)

    paperId_author = list(reader)

with open('data/authors.csv', 'r') as f:
    reader = csv.reader(f)
    next(reader)
    author_data = list(reader)

a = 0
l = []

for x in range(len(voca)):
    voca[x] = list(voca[x])
    if voca[x][0] == "content":
        term = voca[x][1].decode("utf-8")
        l.append(term)
voca = l


cnt = []
count = 0
print(len(v_list))
# for x in range(len(v_list)):
#     count += 1
#     print("Process 1", count)
#     term_list = []
#     for y in range(len(v_list[x][1])):
#         v_list[x][1][y] = list(v_list[x][1][y])
#         word = v_list[x][1][y][0]
#         index = voca.index(word)
#         term = [index, v_list[x][1][y][1]]
#         term_list.append(term)
#
#     doc_id = v_list[x][0]
#     cnt.append([doc_id, term_list])
# corpus = []
# count = 0
# for x in range(len(cnt)):
#     count += 1
#     print("Process 2", count)
#     corpus_row = []
#     for y in range(len(cnt[x][1])):
#         word_id = cnt[x][1][y][0]
#         word_count = cnt[x][1][y][1]
#         for z in range(word_count):
#             corpus_row.append(word_id)
#     corpus.append(corpus_row)
#
# with open('data_atm/corpus.pkl', 'wb') as f:
#     pickle.dump(corpus, f)

id_list = []
author_list = []
for x in range(len(paperId_author)):
    id_list.append(paperId_author[x][0])
    del paperId_author[x][0]
    author_list.append(paperId_author[x])

doc_author = []
count = 0
error = 0
for x in range(len(v_list)):
    count += 1
    try:
        doc_id = v_list[x][0]
        ind = id_list.index(doc_id)
        authors = author_list[ind]
    except:
        authors = []
        error += 1

    doc_author.append(authors)



author_id_list = []
for x in range(len(author_data)):
    author_id = author_data[x][0]
    author_id_list.append(author_id)

doc_author_indexed = []
for doc in range(len(doc_author)):
    row = []
    for aut in range(len(doc_author[doc])):
        author_index = author_id_list.index(doc_author[doc][aut])
        row.append(author_index)
    doc_author_indexed.append(row)




with open('data_atm/voca_atm.pkl', 'wb') as f:
    pickle.dump(voca, f)

with open('data_atm/doc_author.pkl', 'wb') as f:
    pickle.dump(doc_author_indexed, f)
