#  向量检索

###  Approximate Nearest Neighbor Search (ANNS)

为什么要有向量检索?

* 在各个AI的技术领域中,  都在尝试利用实数向量来表示内容本身
* 在利用实数向量表示的内容来说,具备两个特点
  * 实数向量维度高
  * 数据内容的集合规模大 

​    假设向量维度为d, 数据集合规模为N. 如果我们采用brute force的线性搜索方式去精确查找, 整体的时间复杂度是O(Nd). 而向量维度和数据集合规模的增大必然导致时间消耗的增加. 而向量检索可以在牺牲一定精度的情况下, 获得时间和空间上的消耗减少.

向量检索应该具备一些特点:

* 查的足够快(实时性高), 能够支撑海量数据规模的查询
* 查的足够准(同brute force而言, topK有较好的召回率)
* 存储空间消耗小

 从向量检索的本质来说:

* brute force 是不对空间进行划分, 从全空间进行搜索, 所以精度准, 但是速度慢
* 向量检索的相关算法都是对全空间划分, 将Points集合进行全空间划分, 将其划分为若干个很小的子空间. 在搜索的时候, 通过某个方式, 将待查询的实数向量映射到在一个或者多个这样的子空间, 然后在子空间进行遍历.
* 空间上的划分和待查询子向量的映射都是导致精度损失的原因

 从当前向量检索的方法来看, 主要有以下几类:

* 基于树的方法
* 基于哈希的方法
* 基于矢量量化的方法
* 基于图的方法



## 基于树的方法

未完待续

## 基于哈希的方法

* 无监督哈希
* 有监督哈希
* 半监督哈希

关于上述三种的相关论文可以参考[Hash Learning]( https://github.com/czxxjtu/Hash-Learning.github.io ), 这个网址里面有很多相关论文介绍. 在工业场景中一般情况下使用的局部敏感哈希(Locality Sensitive Hashing).

### what is Locality Sensitive Hashing?

局部敏感哈希具备<u>**距离相近的点比距离相远的点更容易发生碰撞**</u>的特征.



###  哈希是如何加速查找的?

对于一个待查询向量而言,  整个查询由两部分组成

* 确认待查询向量落在哪个桶内 (缩小空间)
* 遍历当前桶内的向量 (数据集合规模变小)

### 单表哈希与多表哈希

在[FALCONN]( https://github.com/FALCONN-LIB/FALCONN ) 中支持了hyperplane hash function 和 cross-polytope hash function. 假设我们现在使用了hyperplane lsh, 那这个时候我们可以选择超平面的个数是K.. 

在单表哈希的情况下,

* 如果K太小, 则每个cell的数据规模仍旧较大, 查询时间仍旧很高.
* 如果K太大, 则查询向量和其最近邻向量落入到一个cell里面的概率就会很小.(每个哈希函数都有一定的概率将相近的点映射到不同的cell里面)

针对单表哈希的这个情况,  可以利用多表哈希来解决. (这个解法类似于Annoy中的构建多个树)

* 构建过程
  * 针对单表哈希的过程,  重复L次. 相当于构建了K * L个哈希函数
* 查询过程
  * 针对待查询向量可以获得L个cell, 在这L个个cell中查询



## 多表哈希下K与L的选取

K的选取面临的问题同单表哈希中一样. 对L的选取仍旧存在问题

* L过大, 需要更多的存储空间和增加相应的查询时间

通过合理的选取K和L,  我们仍旧能够获得极大的性能提升.

### MultiProbe LSH

为了能获得较好的查询准确率, L的一般取值范围设置成100~1000, 此时空间上的消耗就会变大. 在大数据集上这更是一个不可忽视的问题.

MultiProbe(多探针)能够显著的减少哈希表的数量的一种策略. MultiProbe是指在每个哈希表中, 不仅仅对待查询向量所在的cell中遍历, 同时也在其临近的T个cell中遍历. 临近指的是包含最近邻的可能性最高, 可以利用汉明距离来求T个cell.

MultiProbe可以提高在一个哈希表中找到最近邻的概率, 从而使得我们可以减少构建哈希表的数量.



### 参数选择

* K (每个哈希表的哈希函数数目)

* L (哈希表的数目)

* T (每个哈希表中最邻近的cell的数量)

* 选取过程

  * 根据可使用内存的大小选择L

  * 然后再K和T之间做折中. 一般而言K越大, 相应的T应该也越大; K减少, T也应该减少

    K和T选取的最佳实践:

    * 试着增加K的数量. 在固定的K下, 如果当前的样本集合查询准确率满足我们的需求, 则这个T是合理的
    * 改变参数T的时候, 不需要重建哈希表(但是K和L相反)
    * 可以通过二分查找的方式确定合理的T



## 基于矢量量化的方法

未完待续

## 参考书目

*  [LSH:primer](https://github.com/FALCONN-LIB/FALCONN/wiki/LSH-Primer) 
*  https://github.com/FALCONN-LIB/FALCONN/wiki/LSH-Families 
*  [Similarity Search in High Dimensions via Hashing]( https://www.cs.princeton.edu/courses/archive/spring13/cos598C/Gionis.pdf )
*  [图像检索:向量索引]( http://yongyuan.name/blog/vector-ann-search.html )
*  https://milvus.io/cn/docs/v0.8.0/about_milvus/index_method.md
* [Hash Learning]( https://github.com/czxxjtu/Hash-Learning.github.io )

