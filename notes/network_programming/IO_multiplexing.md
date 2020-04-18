## I/O复用

select/poll/epoll~都是I/O复用的具体实现

### select

~~~c

int select(int maxfd, fd_set *readset, fd_set *writeset, fd_set *exceptset, struct timeval *timeout);

返回：若有就绪描述符则为其数目，若超时则为0，若出错则为-1
~~~

**说明**:

* maxfd:指定待测试的描述符个数, 它的值是待测试的最大描述符加1. 描述符从0, 1, 2, .... 一直到maxfd-1均会被测试

* fd_set:读描述符集合 readset、写描述符集合 writeset 和异常描述符集合 exceptset.  如果对某个描述符集合不感兴趣则将其设置成NULL, 此时内核将不会对其进行检测;否则内核会对描述符状态进行检测.

* timeout:

  ~~~c
  struct timeval { 
      long tv_sec; /* seconds */
      long tv_usec; /* microseconds */
  };
  ~~~

  * 永远等待下去:  表示没有I/O事件, select会一直等待下去. 此时值timeout的值是NULL
  * 等待一段固定时间: 表示等待一段固定时间后,  从select阻塞调用中返回.
  * 根本不等待: tv_sec 和 tv_usec的值都是零, 描述符检测完毕后立即返回, 这种称为轮询(polling)

     在前两种情况的等待下通常会被进程在等待期间捕获的信号中断,并返回信号处理函数

* 当select函数返回后, 通过遍历fd_set 可以找到就绪的描述符

**优点**：

* 可移植性好

**缺点**：

* 在Linux系统上最大支持的描述符数量为1024, 可以通过修改宏定义重新编译内核的方式来改变, 但是影响效率
* select每次调用完成后, 返回的是全部描述符集合且内核会修改描述符集合状态. 因此当我们调用select后, 需要重置描述符集合.



### poll

~~~C

int poll(struct pollfd *fds, unsigned long nfds, int timeout); 
　　　
返回值：若有就绪描述符则为其数目，若超时则为0，若出错则为-1

struct pollfd {
    int   fd;         /* file descriptor */
    short events;     /* requested events */
    short revents;    /* returned events */
};  
~~~

**说明**：

* fds:是一个pollfd数组指针, 其中第一个元素指向的fd是listen_fd
* nfds:是fds的大小
* timeout
  * 永远等待: timeout 为负数
  * 立即返回: timeout 等于零
  * 固定等待: timeout > 0, 等待指定数目的毫秒数

**优点**:

* 同select比, 没有描述符数量的限制
* 同select比, poll比select支持更多的事件类型
* 同select相比, poll 不修改描述符集合

**缺点**:

* 每次调用返回全部描述符集合



### epoll

~~~C
int epoll_create(int size);
返回值: 若成功返回一个大于0的值，表示epoll实例；若返回-1表示出错
int epoll_ctl(int epfd, int op, int fd, struct epoll_event *event)；
返回值: 若成功返回0；若返回-1表示出错
int epoll_wait(int epfd, struct epoll_event * events, int maxevents, int timeout);
返回值: 成功返回的是一个大于0的数，表示事件的个数；返回0表示的是超时时间到；若出错返回-1.
~~~



**说明**:

* epoll_create: 从Linux2.6.8开始, size函数没有实际含义, 但仍旧需要一个大于零的数. 返回的epoll fd作为epoll_ctl和epoll_wait的入参.

* epoll_ctl:

  * epfd是epoll_create的返回值

  * op: 一共支持三种操作,  表示对fd的监听事件

    * EPOLL_CTL_ADD： 向 epoll 实例注册文件描述符对应的事件
    * EPOLL_CTL_DEL：向 epoll 实例删除文件描述符对应的事件
    * EPOLL_CTL_MOD： 修改文件描述符对应的事件

  * fd: 表示注册的事件的文件描述符

  * event: 表示注册事件类型

    ~~~c
    typedef union epoll_data { 
        void *ptr; 
        int fd;
        uint32_t u32; 
        uint64_t u64; 
    }epoll_data_t;
    
    struct epoll_event { 
        uint32_t events; /* Epoll events */ 
        epoll_data_t data; /* User data variable */ 
    };
    ~~~

    * EPOLLIN：表示对应的文件描述字可以读, 包括对端描述符正常关闭
    * EPOLLOUT：表示对应的文件描述字可以写
    * EPOLLRDHUP：表示套接字的一端已经关闭，或者半关闭
    * EPOLLHUP：表示对应的文件描述字被挂起
    * EPOLLET：设置为 edge-triggered，默认为 level-triggered

* epoll_wait

  * epfd: epoll_create的返回值, epoll实例
  * events: 返回给用户空间的需要处理的I/O事件数组, 数组大小由返回值决定. 其中events的取值同epoll_ctl里面的设置一样,  data就是epoll_ctl里面设置的data, 是用户空间和内核空间的调用时需要的参数.
  * maxevents: 表示epoll_wait返回的最大事件值, 必须大于零.
  * timeout: 超时时间
    * 立即返回: timeout 等于零
    * 无限期等待: timeout 等于 -1

* 工作模式

  * LT (水平触发)
    * 只要满足evetns的条件,  每次调用epoll_wait都会通知该事件的存在, 就一直不断的把这个事件传递给用户
  * ET (边缘触发)
    * 只有第一满足events的条件,  epoll_wait才会通知该事件的存在, 后续都不会传递该事件了.

**优点**:

* 同select比, 没有描述符数量的限制
* 同select和poll相比, epoll返回的就绪的描述符集合而非全部描述符集合
* 同select和poll相比, epoll的I/O效率不会随着监视的fd数量增长而下降

**缺点**:

* 当前仅支持Linux



### 参考书目

* UNIX网络编程 卷1:套接字联网API
* http://man7.org/linux/man-pages/man2/select.2.html
* http://man7.org/linux/man-pages/man2/poll.2.html
* http://man7.org/linux/man-pages/man2/epoll_wait.2.html
* [Linux IO模式及 select、poll、epoll详解](https://segmentfault.com/a/1190000003063859)
* [IO多路复用之epoll总结](http://www.cnblogs.com/Anker/archive/2013/08/17/3263780.html)
* [极客时间:网络编程实战](https://time.geekbang.org/column/article/111267)