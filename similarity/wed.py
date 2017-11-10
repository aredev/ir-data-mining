import numpy as np

def fast_wdist(A, B, W):
    """
    Compute the weighted euclidean distance between two arrays of points:

    D{i,j} =
    sqrt( ((A{0,i}-B{0,j})/W{0,i})^2 + ... + ((A{k,i}-B{k,j})/W{k,i})^2 )

    inputs:
        A is an (k, m) array of coordinates
        B is an (k, n) array of coordinates
        W is an (k, m) array of weights

    returns:
        D is an (m, n) array of weighted euclidean distances
    """

    # compute the differences and apply the weights in one go using
    # broadcasting jujitsu. the result is (n, k, m)
    wdiff = (A[np.newaxis,...] - B[np.newaxis,...].T) / W[np.newaxis,...]

    # square and sum over the second axis, take the sqrt and transpose. the
    # result is an (m, n) array of weighted euclidean distances
    D = np.sqrt((wdiff*wdiff).sum(1)).T

    return D