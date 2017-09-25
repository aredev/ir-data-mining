import numpy
import csv
import copy


def transformToMatrix(your_list):
    with open('authors.csv', 'r') as f:
        reader = csv.reader(f)
        next(reader)
        author_list = list(reader)

    lyl = len(your_list)
    lal = len(author_list)

    li = copy.deepcopy(author_list)

    for column in li:
        del column[1]

    li1 = []
    for li in li:
        for item in li:
            li1.append(item)

    for column in your_list:
        del column[0]

    matrix = numpy.zeros((lal, lal))
    for x in range(lyl):
        le = len(your_list[x])

        if le > 1:

            for y in range(le):

                for z in range(le):
                    if z is not y:
                        au1 = your_list[x][y]
                        au2 = your_list[x][z]

                        iau1 = li1.index(str(au1))
                        iau2 = li1.index(str(au2))

                        matrix[iau1][iau2] = matrix[iau1][iau2] + 1

    return matrix
