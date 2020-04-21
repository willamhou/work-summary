import numpy as np


def euclidean_dist(x, y):
    """ This is a hot function, hence some optimizations are made. """
    diff = np.array(x) - y
    return np.sqrt(np.dot(diff, diff))

def euclidean_square(x, y):
    """ This is a hot function, hence some optimizations are made. """
    diff = np.array(x) - y
    return np.dot(diff, diff)

def euclidean_center(x, y):
    """ This is a hot function, hence some optimizations are made. """
    diff = np.mean(x) - np.mean(y)
    return np.dot(diff, diff)

def l1norm_dist(x, y):
    return sum(abs(x - y))

def cosine_dist(x, y):
    return 1 - np.dot(x, y) / ((np.dot(x, x) * np.dot(y, y)) ** 0.5)


