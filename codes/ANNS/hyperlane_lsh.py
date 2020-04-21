import numpy as np
from distance import cosine_dist, euclidean_dist, euclidean_center, euclidean_square, l1norm_dist


class LSH(object):

    def __init__(self, hash_size, input_dims, hashtable_nums = 1):

        self.hash_tables = [dict() for i in range(hashtable_nums)]
        self.dims = input_dims
        self.hash_size = hash_size
        self.uniform_hyperplanes = [np.random.randn(hash_size, self.dims) for i in range(hashtable_nums)]


    def _hash(self, hyperplane, input_point):

        if isinstance(input_point, list):
            input_point = np.array(input_point)

        hash_key = np.dot(hyperplane, input_point)

        return "".join(['1' if i > 0 else '0' for i in hash_key])

    def build_index(self, input_lists:list, extra_lists:list = None):


        for i, hash_table in enumerate(self.hash_tables):
            for item in input_lists:
                hash_key = self._hash(self.uniform_hyperplanes[i], item)
                hash_table.setdefault(hash_key, []).append(tuple(item))

        print(self.hash_tables)

    def search(self, query, topk = 10, distance = cosine_dist):

        candidates = set()

        for i, hash_table in enumerate(self.hash_tables):
            hash_key = self._hash(self.uniform_hyperplanes[i], query)
            candidates.update(hash_table.get(hash_key, []))

        candidates = [(ix, distance(np.array(query), np.array(ix))) for ix in candidates]
        candidates.sort(key = lambda x:x[1])

        # print(candidates)
        return candidates[:topk] if topk > len(candidates) else candidates


mini_lsh = LSH(5, 8)
mini_lsh.build_index([[1,2,3,4,5,6,7,8], [2,2,3,4,5,6,7,9], [10,12,99,1,5,31,2,3], [12,15,99,1,5,31,2,3]])
res = mini_lsh.search([1,2,3,4,5,6,7,7], distance = cosine_dist)
print(res)
