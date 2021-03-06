### I/O模型

* 阻塞I/O (bloking I/O)
* 非阻塞I/O (nonblocking I/O)
* I/O复用 (I/O multiplexing)
* 信号驱动I/O （singal-drive I/O）
* 异步I/O (asynchronous I/O)


一个输入操作通常包含两个不同的阶段:
* 等待数据准备好
* 从内核向进程复制数据

对于一个套接字而言, 第一步通常涉及等待数据从网络中到达. 当所等待数据分组到达时, 它被复制到内核中的某个缓冲区. 第二步就是将数据从内核缓冲区复制到应用进程缓冲区.


#### 阻塞I/O

![img](https://camo.githubusercontent.com/5ebdb46341969caa39d2037f9061d966dbfd9961/68747470733a2f2f63732d6e6f7465732d313235363130393739362e636f732e61702d6775616e677a686f752e6d7971636c6f75642e636f6d2f313439323932383431363831325f342e706e67)

**说明**:
在此模型下应用进程被阻塞, 直到数据报到到达且被复制到应用进程缓冲区或者发生错误才返回.

**优点**:
程序实现简单, 进程或线程在阻塞等待数据期间挂起, 基本不占用CPU资源.

**缺点**：
每个连接需要独立的进程/线程单独处理，当并发请求量大时为了维护程序，内存、线程切换开销较大.

#### 非阻塞I/O
![img](https://camo.githubusercontent.com/d0fbceea06e5674972700d461ca62d6f1b715f0b/68747470733a2f2f63732d6e6f7465732d313235363130393739362e636f732e61702d6775616e677a686f752e6d7971636c6f75642e636f6d2f313439323932393030303336315f352e706e67)

**说明**:
在此模型下, 应用进程把一个套接字设置成非阻塞是告诉内核:当所请求的I/O操作非得把本进程投入睡眠才能完成时,不要把本进程投入睡眠, 而是返回一个错误.

轮询:当一个进程需要不断的执行系统调用来知晓I/O是否完成.


**优点**:
进程不会阻塞在等待数据的过程, 每次的I/O请求都可以立即返回, 实时性较好.

**缺点**：
进程持续轮询内核,来查看某个操作是否就绪.这么做往往消耗大量CPU时间,使得CPU利用率较低.


#### I/O 复用
![img](https://camo.githubusercontent.com/c31f8db408e14826915b8d7b70724e5095298ee0/68747470733a2f2f63732d6e6f7465732d313235363130393739362e636f732e61702d6775616e677a686f752e6d7971636c6f75642e636f6d2f313439323932393434343831385f362e706e67)

**说明**:
在此模型中可以使用select/poll/epoll(2.6以后的内核支持). 我们阻塞于select调用上,等待数据报套接字可读.当select返回套接字可读时, 我们调用recvfrom把所读数据复制到应用进程缓冲区. 同阻塞I/O不同的地方在于, I/O复用可以等待多个描述符就绪.


**优点**:
基于一个阻塞对象, 等待多个描述符就绪. 而不需要使用多个进程或者线程来等待多个描述符就绪,大大减少资源.

**缺点**：
I/O复用需要两个系统调用.


#### 信号驱动I/O
![img](https://camo.githubusercontent.com/9533dfd9ce5b31d63b70ba6ce1aeae1ae64958db/68747470733a2f2f63732d6e6f7465732d313235363130393739362e636f732e61702d6775616e677a686f752e6d7971636c6f75642e636f6d2f313439323932393535333635315f372e706e67)


**说明**:
在此模型中,进程需要为套接字开启信号驱动I/O功能,并通过sigaction系统调用安装一个信号处理函数.该系统调用立即返回,并不阻塞. 当数据准备好时,内核会为进程产生一个SIGIO信号,随后即可以在信号处理函数中调用各种I/O操作函数进行处理.


**优点**:
在等待数据时,没有被阻塞. 可以提高资源利用率

 

 #### 异步I/O
![img](https://camo.githubusercontent.com/9c1afa0a4d217e0adfc91ab3b4d7ea9f3d6b1463/68747470733a2f2f63732d6e6f7465732d313235363130393739362e636f732e61702d6775616e677a686f752e6d7971636c6f75642e636f6d2f313439323933303234333238365f382e706e67)



**说明**:
在此模型中, 异步I/O函数的工作机制一般是:告知内核启动某个操作,并让内核完成整个操作(包括将数据从内核复制到我们自己的缓冲区)完成后通知我们.

同信号驱动I/O的区别在于:信号驱动I/O是由内核通知我们何时启动一个I/O操作, 而此模型是由内核通知我们I/O操作何时完成.


**优点**:
无阻塞, 充分利用系统资源和提高CPU利用率

**缺点**:
Linux下并没有真正的异步I/O操作,而且依赖于操作系统做大量工作. Windows下通过IOCP真正的实现了异步I/O. Linux下还是通过IO复用来实现高并发网络编程.

 #### 各种I/O模型比较

![img](https://camo.githubusercontent.com/d89aed2ba6c5390aad0626b013c288d8849c4f39/68747470733a2f2f63732d6e6f7465732d313235363130393739362e636f732e61702d6775616e677a686f752e6d7971636c6f75642e636f6d2f313439323932383130353739315f332e706e67)


 * 同步I/O: 导致请求进程被阻塞,直到I/O操作完成
 * 异步I/O: 不导致请求进程阻塞

 从上图可以看出,前四种模型的主要区别在于第一阶段, 第二阶段都是一样的在数据从内核复制到进程缓冲区期间,进程被阻塞.

 异步I/O在这两个阶段都不会被阻塞.

 同步I/O包括: 阻塞式I/O、非阻塞式I/O、I/O复用、信号驱动I/O.



### 参考书目

* UNIX 网络编程 卷1:套接字联网API
* 从零开始学架构