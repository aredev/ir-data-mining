import datatransform
import matrixtransform
import pagerank
import csv

with open('authors.csv', 'r') as f:
    reader = csv.reader(f)
    next(reader)
    author_list = list(reader)

dataList = datatransform.transformToList('paper_authors.csv')

matrix = matrixtransform.transformToMatrix(dataList)

scoreList = pagerank.powerIteration(matrix, rsp=0.15, epsilon=0.00001, maxIterations=1000)

result = []

for x in range(len(author_list)):
    result.append([int(author_list[x][0]), scoreList[x]])

with open('result.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerows(result)

print('test')
