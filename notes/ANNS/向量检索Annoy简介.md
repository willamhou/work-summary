# 向量检索:Annoy简介

## 哈希方法简介

在向量检索的哈希方法中，主要就是通过某些方法将一些连续的实值转化成为0或1的散列值.在对向量实值散列化的过程中，对哈希函数有一些要求.根据不同的策略, 哈希方法可以分为:

* 有监督哈希
* 无监督哈希
* 半监督哈希

## Local Sensitive Hashing

局部敏感哈希(Local Sensitive Hashing)本质上是一种无监督哈希方法.

### 什么是局部敏感？

哈希函数族具备:**<u>距离较近的样本点比距离较远的样本点更容易发生碰撞</u>**的特点时，就可以被称为局部敏感

### 哈希方法如何加速？

对于精确查找而言，本质上是在整个数据空间内进行遍历比较. 而对于哈希方法而言，

1. 首先利用哈希函数确定查询样本落入的Bucket
2. 然后在这个Bucket中进行遍历查找，得到查询样本的最近邻

从上述描述来看，LSH也符合ANNS算法的特点

1. 利用某种方式对全空间进行切分
2. 利用某种方式对子空间搜索

## 多表哈希

当我们使用LSH的时候，第一个想法就是使用一个区分性足够的好的哈希函数，将数据空间切分为两部分，然后进行搜索.  从前述描述可以看出，一个区分性足够好的函数可以将数据空间一分为二。但是在搜索的时候，整个搜索空间只下降了一半，当我们要搜索的数据空间无比巨大的时候，这个搜索时延是我们不能接受的.

单哈希函数有前述的问题，那么自然而然我们可以想到利用一组(**<u>K个</u>**)哈希函数做数据空间的划分. 由于每个哈希函数都可以划分为2个空间，那么K个哈希函数就可以将数据空间划分为2^K个子空间(Bucket). 那么对于每个查询样本而言，我们可能只会近似搜索比较1/2^K的数据点. 通过对K的良好选择，我们就会获得一个良好的查询时间



在多哈希函数中, 问题的关键点在于K的选择.  如果我们选择的K太小, 查询时间会下降. 如果我们选择K太大， 则由于LSH的特性查询样本和近邻样本落入同一个Bucket的概率会降低.

针对K的问题, 我们可以考虑通过重复这个过程L次增加整体的召回率. 那么重复L次这个过程分为两步

1. 构建哈希表的时候, 重复L次. 可以得到L个哈希表
2. 给定插叙样本的时候, 重复L次, 可以得到L个Bucket. 我们在这L个Bucket中做遍历查询得到最近邻

前述过程相当于构建了K*L个哈希函数.

#### 多表哈希的关键点

多表哈希最关键的两个参数是K(哈希函数个数)和L(哈希表个数). 

参数K的问题

1. K太小，每个哈希桶中容纳的数据量太大，增加响应时间
2. K太大，每个哈希桶中容纳的数据小，降低了近邻召回率. 这点可以通过L个哈希表来解决

参数L的问题

	1. L太小，K太大的问题没有解决
	2. L太大，内存空间的过多消耗和响应时间的增加

从上述两个参数问题来看，这点很难解决. 但实际上看, 在K过大或K过小之间一定有一个合理的值. 通过合理的选择K和L, 同线性扫描而言，我们还是可以得到极大的速度提升

#### 什么是多探针哈希

在多表哈希的时间过程中，L的大小一般设置为100~1000. 但是如果我们有一个极大的数据集, 那么多表哈希消耗的内存空间极大. 为了平衡内存空间消耗和近邻召回率,  我们可以采用多探针哈希的方式

在多表哈希中, 查询样本最终与L个哈希桶内的数据点进行遍历. 而多探针哈希, 我们将在T个哈希桶中进行遍历(T > L). 这意味着两点:

1. 在查询样本落入的哈希桶中遍历
2. 除了查询样本落入的哈希桶, 还要和查询样本落入的哈希桶的近邻哈希桶中遍历

怎么定义近邻哈希桶?

这里的近邻哈希桶指的是汉明距离下的相近.

#### 多探针哈希的关键点

通过前述说明, 一共有三个关键点

* K, 每个哈希表的哈希函数数量. 哈希函数主要用于空间划分(the number of hash functions)
* L, 哈希表的数量. 每个哈希表有K个哈希函数(the number of hash tables)
* T, 探针哈希桶的数量 (the number of probes)



在上述参数选择的时候, 根据内存情况确认L的大小, 然后在K和T中做权衡.

* K越大则T应该设置的越大
* 对于固定的K, 如果在查询样本中已经达到了我们的目标准确率，则该T是合理值
* 对于T调参的时候, 不需要重建哈希表, 同时可以通过二分搜索来加速参数选取过程.

## 开源实现

### LSHash

[LSHash](https://github.com/kayzhu/LSHash/tree/master/lshash)适合对于LSH代码原理的学习.

整个LSHash包含

* lshash.py 单表哈希的实际实现

* storage.py 索引存储的实现

  

hash_size就是哈希函数的数量, input_dim是输入样本的维度.

```python
 def _generate_uniform_planes(self):
        """ Generate uniformly distributed hyperplanes and return it as a 2D
        numpy array.
        """

        return np.random.randn(self.hash_size, self.input_dim)
```



query_point就是查询样本点, num_results就是近邻的TopK, distance_func是哪种距离衡量近邻

```python
    def query(self, query_point, num_results=None, distance_func=None):
        """ Takes `query_point` which is either a tuple or a list of numbers,
        returns `num_results` of results as a list of tuples that are ranked
        based on the supplied metric function `distance_func`.
        :param query_point:
            A list, or tuple, or numpy ndarray that only contains numbers.
            The dimension needs to be 1 * `input_dim`.
            Used by :meth:`._hash`.
        :param num_results:
            (optional) Integer, specifies the max amount of results to be
            returned. If not specified all candidates will be returned as a
            list in ranked order.
        :param distance_func:
            (optional) The distance function to be used. Currently it needs to
            be one of ("hamming", "euclidean", "true_euclidean",
            "centred_euclidean", "cosine", "l1norm"). By default "euclidean"
            will used.
        """

        candidates = set()
        if not distance_func:
            distance_func = "euclidean"

        if distance_func == "hamming":
            if not bitarray:
                raise ImportError(" Bitarray is required for hamming distance")

            for i, table in enumerate(self.hash_tables):
                binary_hash = self._hash(self.uniform_planes[i], query_point)
                for key in table.keys():
                    distance = LSHash.hamming_dist(key, binary_hash)
                    if distance < 2:
                        candidates.update(table.get_list(key))

            d_func = LSHash.euclidean_dist_square

        else:

            if distance_func == "euclidean":
                d_func = LSHash.euclidean_dist_square
            elif distance_func == "true_euclidean":
                d_func = LSHash.euclidean_dist
            elif distance_func == "centred_euclidean":
                d_func = LSHash.euclidean_dist_centred
            elif distance_func == "cosine":
                d_func = LSHash.cosine_dist
            elif distance_func == "l1norm":
                d_func = LSHash.l1norm_dist
            else:
                raise ValueError("The distance function name is invalid.")

            for i, table in enumerate(self.hash_tables):
                binary_hash = self._hash(self.uniform_planes[i], query_point)
                candidates.update(table.get_list(binary_hash))

        # rank candidates by distance function
        candidates = [(ix, d_func(query_point, self._as_np_array(ix)))
                      for ix in candidates]
        candidates.sort(key=lambda x: x[1])

        return candidates[:num_results] if num_results else candidates
```



### FALCONN

[FALCONN](https://github.com/FALCONN-LIB/FALCONN/wiki/LSH-Families )适合在实践中使用, 具体使用方法可以参考其官方文档, 不再赘述.

## 参考书目

[LSHash](https://github.com/kayzhu/LSHash/tree/master/lshash)

[FALCONN](https://github.com/FALCONN-LIB/FALCONN/wiki/LSH-Families )

[HASHING](https://github.com/ZJULearning/MatlabFunc/tree/master/ANNS/Hashing)

[LSH:primer](https://github.com/FALCONN-LIB/FALCONN/wiki/LSH-Primer) 

[Hash Learning]( https://github.com/czxxjtu/Hash-Learning.github.io )

