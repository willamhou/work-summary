[TOC]



# 网络编程模型

  前述对I/O模型及I/O复用进行了简要介绍, 而这个网络编程模型都是在I/O模型上进行发展. 本部分主要介绍常见的网络编程模型.

​	服务器并发模型设计有两个点:

	*	服务器如何管理连接
	*	服务器如何处理请求

## PPC

**说明**:

​		PPC是 Process Per Connection, 意味着每次有一个新的连接, 就新建一个进程去专门处理这个连接的请求. 这是传统的UNIX网络服务器所采用的模型.

![img](https://static001.geekbang.org/resource/image/89/99/8941e9ef9286493d67e9da277b9ee799.png)

**优点**:

* 实现方式简单

**缺点**:

* fork代价高, 从操作系统的角度而言:创建一个进程的代价很高, 需要分配很多内核资源,需要将内存映像从父进程复制到子进程

* 父子进程通信复杂, 父子进程通信需要采用IPC之类的进程通信方案

* 进程数量增大以后对操作系统压力较大:如果每个连接的存活时间都较长,会导致系统资源长时间得不到释放;同时又有新的连接进来,进一步抢占系统资源. 一般情况下, 该模式支持的最大并发数量就是几百

* 每次连接进来时才会fork子进程, 由于fork代价较高, 导致客户觉得访问较慢.

  

## Prefork

**说明**:

​	顾名思义, Perfork就是提前创建进程.系统在启动的时候预先创建好进程,然后才开始接受用户的请求. 当有新的连接进来的时候, 就可以省去fork的操作, 让用户访问更快、更好.

​	![img](https://static001.geekbang.org/resource/image/d0/2e/d0f1df9716145a6bd02bb4a83b1fd62e.jpg)

**优点**:

* 实现方式简单
* 提前创建进程避免了客户访问较慢的体验

**缺点**:

* 同PPC模型
* 由于多个进程同时accpet一个socket可能会引入惊群问题(可以由操作系统解决这个问题, Linux 2.6内核以后已解决了该问题)



## TPC

**说明**:

​	Thread per Connection, 指每次有新的连接就新建一个线程去专门处理这个连接的请求。与进程相比，线程更轻量级，创建线程的消耗比进程要少得多；同时多线程是共享进程内存空间的，线程通信相比进程通信更简单。

![img](https://static001.geekbang.org/resource/image/26/42/263798db70ca2509d6ecf95604fe8842.png)

**优点**:

* 子线程共享主进程空间, 同fork相比减少了系统开销
* 无须进程间通信

**缺点**:

* 高并发情况下, 仍旧存在性能问题. 线程创建仍旧消耗系统资源
* 线程间的互斥和共享引入了新的问题, 可能会导致死锁
* 多线程相互影响, 如果一个线程异常可能会导致整个进程退出



## PreThread

**说明**:

​	顾名思义, 提前创建线程, 减少当连接进来的时候才创建线程的操作, 让用户体验更好. 常见的实现方式有以下两种:

	*	主进程accept, 然后将连接交给某个线程处理
	*	子线程都尝试去accept, 最终只有一个线程accept成功, 方案示意图如下:

![img](https://static001.geekbang.org/resource/image/54/df/548d9b2ece16bebba532b996a88bbadf.jpg)

**优点**:

* 提前创建线程,减少了有新的连接过来时才创建线程的消耗
* 同TPC

**缺点**:

* ### 同TPC

  

## Reactor

**说明**:

在前述模型中, 存在两个问题:

 *	存在进程的创建与销毁, 没做到资源复用造成了极大浪费
 *	连接建立后，如果当前进程/线程暂时没有数据可读，则进程/线程就阻塞在read操作上，造成进程/线程资源浪费

 针对上面两个问题有以下解决方案:

* 基于线程池复用资源. 不再为每个连接创建线程,  而是将连接分配给线程, 一个线程可以处理多个业务
* 基于I/O复用. 当多条连接共用一个阻塞对象后，进程只需要在一个阻塞对象上等待，而无须再轮询所有连接.当某条连接有新的数据可以处理时，操作系统会通知进程，进程从阻塞状态返回，开始进行业务处理



I/O复用+线程池就是Reactor模式(Dispatch模式)的基本设计思想,本质上事件驱动的.即 I/O 多路复用统一监听事件，收到事件后分配（Dispatch）给某个线程.

### Reactor的关键组成

* Reactor:负责监听和分配事件
* 处理资源池: 负责处理事件

### Reactor的典型实现方案

* 单Reactor单进程/线程

  ![img](https://static001.geekbang.org/resource/image/21/b1/214701713f4cd942295f423ba158f6b1.png)

  * 方案说明
    * Reactor 对象通过 select 监控连接事件，收到事件后通过 dispatch 进行分发
    * 如果是连接建立的事件，则由 Acceptor 处理，Acceptor 通过 accept 接受连接，并创建一个 Handler 来处理连接后续的各种事件
    * 如果不是连接建立事件，则 Reactor 会调用连接对应的 Handler（第 2 步中创建的 Handler）来进行响应。Handler 会完成 read-> 业务处理 ->send 的完整业务流程
  * 方案优点
    * 没有多进程程通信问题, 没有数据竞争, 全部都在一个进程内完成
  * 方案缺点
    * 只有一个进程没有办法发挥多核的优点, 无法发挥多核性能
    * Handler在处理某个连接上的任务时, 整个进程无法处理其他连接事件, 容易导致性能瓶颈
  * 补充
    * 适用于业务处理非常快速的场景, 比如:Redis
    * C/CPP中一般是单进程, Java中一般是单线程

* 单Reactor多进线程

  ![img](https://static001.geekbang.org/resource/image/7c/43/7c299316e48b0531328ba39261d1d443.png)

  

  * 方案说明

    * 主线程中，Reactor 对象通过 select 监控连接事件，收到事件后通过 dispatch 进行分发
    * 如果是连接建立的事件，则由 Acceptor 处理，Acceptor 通过 accept 接受连接，并创建一个 Handler 来处理连接后续的各种事件
    * 如果不是连接建立事件，则 Reactor 会调用连接对应的 Handler（第 2 步中创建的 Handler）来进行响应
    * Handler 只负责响应事件，不进行业务处理；Handler 通过 read 读取到数据后，会发给 Processor 进行业务处理
    * Processor 会在独立的子线程中完成真正的业务处理，然后将响应结果发给主进程的 Handler 处理
    * Handler 收到响应后通过 send 将响应结果返回给 client

  * 方案优点

    * 充分利用CPU多核能力

  * 方案缺点

    * 多线程数据共享和访问比较复杂
    * Reactor负责承担所有事件的监听和响应, 只在主线程中运行,瞬间高并发会成为性能瓶颈.

    

  

* 主从Reactor多线程

![img](https://static001.geekbang.org/resource/image/47/84/47918f1429370664d7eb6d0c741f4784.png)

* 方案说明
  * 父进程中 mainReactor 对象通过 select 监控连接建立事件，收到事件后通过 Acceptor 接收，将新的连接分配给某个子进程
  * 子进程的 subReactor 将 mainReactor 分配的连接加入连接队列进行监听，并创建一个 Handler 用于处理连接的各种事件
  * 当有新的事件发生时，subReactor 会调用连接对应的 Handler（即第 2 步中创建的 Handler）来进行响应
  * Handler 完成 read→业务处理→send 的完整业务流程
* 方案优点
  * 父进程和子进程职责明确, 父进程只负责连接的建立, 子进程负责完成后续的业务处理
  * 父进程和子进程的交互简单, 父进程只需要把新连接传给子进程, 子进程无须返回数据
  * 子进程之间是互相独立的，无须同步共享之类的处理（这里仅限于网络模型相关的 select、read、send 等无须同步共享，“业务处理”还是有可能需要同步共享的
* 补充
  * Memcache 和Netty:主从多线程
  * Nginx: 主从多进程



## Proactor

Reactor是非阻塞同步模型,  这里的同步实际上是指的I/O操作都是同步的. 如果能将I/O改成异步处理, 则能够进一步提升性能, 这就是异步网络模型Proactor.



![img](https://static001.geekbang.org/resource/image/9d/4f/9d41c2e6ae712a6b815a8021b47a624f.png)

* 方案说明
  * Proactor Initiator 负责创建 Proactor 和 Handler, 并将 Proactor 和 Handler 都通过 Asynchronous Operation Processor 注册到内核
  * Asynchronous Operation Processor 负责处理注册请求, 并完成 I/O 操作
  * Asynchronous Operation Processor 完成 I/O 操作后通知 Proactor
  * Proactor 根据不同的事件类型回调不同的 Handler 进行业务处理
  * Handler 完成业务处理, Handler 也可以注册新的 Handler 到内核进程
* 方案缺点
  * Linux目前没有真正的异步I/O模型
  * 当前所有的Linux下的Proactor模型都是用同步I/O模拟出来的, 比如:Boost.Asio

## 参考书目

* 从零开始学架构
* UNIX网络编程 卷1:套接字联网API
* [极客时间:网络编程实战](https://time.geekbang.org/column/article/111267)
* Linux多线程服务端编程