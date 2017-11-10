import math


def get_cosine(v1, v2, weights):
    sumxx, sumxy, sumyy = 0, 0, 0
    for i in range(len(v1)):
        x = v1[i]
        y = v2[i]
        z = weights[i]
        sumxx += x * x * z
        sumyy += y * y * z
        sumxy += x * y * z
    return sumxy / math.sqrt(sumxx * sumyy)
