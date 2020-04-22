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



## 参考书目

*  https://github.com/FALCONN-LIB/FALCONN/wiki/LSH-Primer 
*  https://github.com/FALCONN-LIB/FALCONN/wiki/LSH-Families 
*  [Similarity Search in High Dimensions via Hashing]( https://www.cs.princeton.edu/courses/archive/spring13/cos598C/Gionis.pdf )
*  [图像检索:向量索引]( http://yongyuan.name/blog/vector-ann-search.html )
*  https://milvus.io/cn/docs/v0.8.0/about_milvus/index_method.md
* 