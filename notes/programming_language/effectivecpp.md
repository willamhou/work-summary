1.尽量以const、inline、enum 替代define
 A.class专属常量为了保证只存在一份实体,必须成为static成员. static const T val;
 B.常量指针
 单常量最好用const或enum 替换define
 对于形似函数的宏,最好用inline替换define

2.尽可能使用const
  const出现星号左边,被指物为常量
  const出现星号右边,指针自身是常量
  const出现在在星号两边,指针和被指物都是常量

  除非有需要改动参数或者local对象,否则最好声明为const
  const成员函数为了保证成员函数可以作用在const对象上.(使得class接口容易理解, 使得操作const对象成为可能).
  利用mutable对非staic成员变量进行声明, 可以确保在const成员函数内进行变量修改.
  A.当const和non-const成员函数有着实质的等价实现时,可以利用non-const调用const

3.确定对象被使用前已经被初始化
	

	永远在使用对象之前进行初始化.
	A.对于无成员的内置类型需要手工完成.
	B.对于除内置类型以外的东西,依赖于构造函数初始化.构造函数需要确保对象的每个成员都被初始化.
	c++ 对象成员的初始化在进入构造函数本体之前.
	   
	总是使用初始化列表,比赋值更高效
	
	A.对内置类型进行手工初始化,C++不保证初始化他们
	B.构造函数应该使用成员初始化列表而非在构造函数体内部使用赋值操作.初值列出的成员变量的次序应该同class中的声明次序相同
	C.为了避免跨单元初始化问题,需要以local static代替non-local static对象.

构造、析构与赋值运算

4.编译器可以暗自为class提供默认构造、拷贝构造、移动构造、copy赋值、移动赋值操作符及析构函数

5.为了阻止copy构造和copy赋值可以将对应的成员函数声明为private且不实现 或者直接用delete标识符表明

6.多态基类应该声明一个virtual析构函数,如果一个类存在virtual成员函数,就应该拥有一个virtual析构函数.如果class不是作为base class或者多态,则不应该有virtural析构函数.

7.别让异常逃离析构
  A.析构函数不应该吐出异常,但是应该捕获异常
  B.如果用户需要对函数运行期间的异常做反应,那么类应该提供一个普通函数中执行该操作

9.不要在构造和析构函数中调用virtual函数
	基类构造期间,virtual函数不会下降到派生类中.

10.令operator = 返回一个reference to *this
11.在operator = 中处理自我赋值
	A.确保对象自我赋值时有良好的行为.其中技术包括"来源对象"和"目标对象"的地址比较,精心周到的语句顺序以及copy and swap
	B.确定任何函数如果操作一个以上的对象,而其中多个对象是同一个对象时,其行为仍然正确.

12.复制对象时勿忘其每一个成分
	A.一个copying函数应该确保复制所有local成员的变量, 同时调用所有base class中合适的copying函数
	B.不要试图以某个copying函数去实现另一个copying函数,应该将共同的部分放入第三个函数中为其他copying函数调用

资源管理
13.以对象管理资源(巧妙利用智能指针)
    A.获得资源后立即放入管理对象 --- 即对智能指针的初始化
    B.管理对象(智能指针)运用析构函数确保资源释放
    为了防止资源泄漏,使用RAII对象,在构造函数中获得资源,在析构函数中释放资源

14.资源管理类中小心copying行为
	A.复制RAII对象必须一并复制它所管理的资源,所以资源的copying行为决定了RAII对象的copying行为
	B.常见的RAII class copying行为: 禁止复制, 引用计数(shared_ptr), 复制底部资源和转移底部资源所有权(unique_ptr)

15.资源管理类中,提供对原始资源的访问.
	A.API中往往要求访问原始资源(raw resources),所以每一个RAII class应该提供一个"取得其所管理的之资源的办法".
	B.对原始资源的访问可能经由显示转换或隐式转换.一般而言,显示转换比较安全,但隐式转换对客户比较方便.

16.成对使用new和delete时要采取相同形式
	A.如果你在new表达式中使用了[],必须在对应的delete表达式中也使用[].
	B.如果你在new中表达式中不使用[],一定不要在相应的delete中使用[].

17.以独立的语句将new对象置入智能指针
	std::shared_ptr<T> ptr(new T);

设计与声明
18.让接口容易被使用,不易被误用.
	行为一致的接口更容易被使用,以及与内置类型的行为兼容
	"阻止误用"的方法包括建立新类型、限制类型上的操作、束缚对象值、以及消除客户的资源管理责任.
	shared_ptr支持定制删除器,可以防范DDL问题.可以被用来自动解除互斥锁.

19.设计class犹如设计type
	设计一个class时需要考虑的一些问题

20.宁以pass-by-reference-to-const 替换 pass-by-value
	A.pass-by-value 会调用构造和析构函数, pass-by-reference则不会
	B.pass-by-value 当一个派生类对象以pass-by-value的方式传递并被视为一个基类对象时,会发生对象切割(即派生类的特性消失),pass-by-reference可以避免这种问题
	C.以上规则并不适用于内置类型、STL容器的迭代器和函数对象,对他们而言pass-by-value更合适.

21.必须返回对象时,不要妄想返回其reference.
	一个必须返回新对象的写法是:就直接让那个函数返回一个新对象
	inline const T operator* (const T &lhs, const T &rhs) {
		return T(lhs, rhs);
	}

	在返回reference和object中抉择时,需要挑出行为正确的那个.
	
	A.禁止返回一个指向local stack的pointer或者reference
	B.禁止返回一个指向heap-allocated的reference
	C.禁止返回一个指向local static的pointer或者reference,因为可能需要多个这样的对象


22.将成员变量声明为private
	1.使用函数可以让你对成员变量的处理有更精确的控制.
	2.封装,class客户对成员变量的变更无感
	3.将成员变量隐藏在函数的接口背后,可以为所有可能的实现提供弹性.
	A.protected并不比private更具封装性
	B.切记将成员变量声明为private,这可以赋予客户访问的数据一致性, 可以细微划分访问控制, 允许约束条件获得保证,
	并给class的实现提供弹性.

23.宁以non-member non-friend函数替换member函数
    1.这样可以增加封装性,包裹弹性和机能扩充性


24.若参数需要类型转换,则为此采用non-member函数
    1.除数值类型外,class支持隐式类型转换是个糟糕的主意
    2.如果你需要为某个函数的所有参数(包括被this指针所指的那个隐喻参数)进行类型转换,那么这个函数必须是个non-member


25.考虑写一个不抛异常的swap函数
	1.当std::swap对你的效率不高时,提供一个swap成员函数,并确保它不抛出异常
	2.如果你提供一个member swap,同时也应该提供一个non-member swap.对于class也请对std::swap特化
	3.调用swap时,应该针对std::swap使用using声明式,然后调用swap且不带任何空间修饰符
	4.为用户定义类型进行std templates全特化是好的,但是不要尝试在std内加入某些对于std而言是新的东西

实现
26.尽可能的延后变量定义式的出现(可以增加程序的清晰度并改善效率)
	1.不仅仅延后变量定义直到使用该变量的前一刻为止
	2.甚至应该延后这份定义直到能够给它初值实参为止
	3.用具备明显意义的初始化值将变量初始化,附带说明变量的目的
	4.如果在循环中使用, 一个class的复制成本低于一组构造+析构成本,且效率高度敏感, class定义在循环外面;否则定义在循环内部.

27.尽量少做转型动作
	1.尽量避免转型动作
	2.如果转型是必要的,试着将他隐藏于某个函数背后
	3.宁可用C++ style的转型,不要使用旧式转型,前者容易识别

28.避免返回handles指向对象内部成分
	1.避免返回handles(reference、pointer、迭代器)指向对象内部
	2.遵守这个条款可增加封装性,帮助const成员函数的行为像个const.并将发生"虚吊号码牌(dangling handles)"的可能性降到最低

29.为"异常安全"而努力是值得的
	1."异常安全"的两个标准 --- (不泄漏任何资源、不允许数据败坏)
	2."异常安全函数"的三个保证 ---(基本承诺、强烈保证、不抛掷)
	3.强烈保证往往能够以copy-and-swap的方式实现出来,但是"强烈保证"并非对所有函数都可以实现或者具备现实意义
	4.函数提供的异常安全保证通常等于其所调用的各个函数的"异常安全保证"中的最弱者
	5.copy-and-swap:
		A.为你打算修改的对象(原件)做出一份副本,然后在那副本上做一切必要的修改
		B.若有修改动作抛出异常,原对象扔保持未改变状态
		C.待所有改变都成功后,再将修改后的那个副本和原对象在一个不抛出异常的操作中置换(swap).

30.inline
	1.inline 不能断点调试 且如果对大型函数声明为inline会导代码膨胀问题
	2.inline应该被限制在小型、被频繁调用的函数上(调试过程和二进制升级更容易,代码膨胀问题最小化,程序的速度提升机会最大化)
	3.不要只因为function templates出现在头文件,就将他们声明为inline

31.将文件间的编译依赖关系降至最低
	1.相依于声明式,不要依赖于定义式.基于此构想的是Handle classes与Interface classes
	2.程序库文件应该以"完全仅有声明式"的形式存在.这种做法无论是否涉及templates都适用


继承与面向对象设计

32.确定public继承是is-a的关系
	1.适用于base class的事情一定适用于derived classes身上,因为每个derived class同时也是一个base class对象.

33.避免遮掩继承而来的名称
	1.derived classes内的名称会遮掩base classes内的名称.在public继承下没有人希望如此
	2.为了让base classes内被遮掩的名称再见天日,可以使用using声明式或转交函数(forwarding functions)

34.区分接口继承和实现继承
	1.成员函数的接口总是会被继承
	2.声明为pure virtual函数的目的是为了让derived classes只继承函数接口
	3.声明简朴的impure virtual函数的目的是为了让derive classes继承该函数的接口和缺省实现
	4.non-virtual函数的目的是为了让derive classes继承该函数的接口及强制性实现

35.考虑virtual函数以外的选择

​	1.使用non virtual interface方式Template Method设计模式的一种,以public non
​	-vritual成员函数包裹较低访问性的virtual函数(private或proteced)
​	2.将virtual函数替换为"函数指针成员变量" --- 这是一种strategy设计模式的表现形式
​	3.利用std::function 成员变量来替换virtual函数
​	4.将继承体系内的virtual函数转换为另一个继承体系的virtual函数strategy模式的传统实现手法~~
​	5.将机能从成员函数转移到class外部函数的缺点:非成员函数无法访问class non-public成员~~~~

36.绝不重新定义继承而来的non-virtual函数

37.绝不重新定义继承而来的缺省参数值
	1.缺省参数值是静态绑定
	2.virtual函数(唯一应该覆写的东西)是动态绑定的

38.通过复合模塑出has-a 或 根据某物实现出
	1.复合发生在应用域(has-a),意味着有一个
	2.复合发生在实现域(is-implemented-in-terms-of),根据某物实现

39.明智而谨慎的使用private继承
	1.private继承意味着编译器不会自动将derived class转化为base class
	2.private继承来的所有成员在derived class中都是private属性
	3.private继承意味着is-implemented-in-terms-of,通常比复合级别低,但是当derived class需要访问base class的protected成员或需要重新定义继承而来的virtual时,这么设计是合理的
	4.private继承可以造成empty class的最优化~~这对致力于对象尺寸最小化的程序开发者而言,可能很重要

40.明智而审慎的使用多重继承
	1.多重继承比单一继承复杂,可能导致新的歧义性和virtual继承的需要
	2.virtual继承会增加大小、速度、初始化(赋值)等等成本.如果virtual base classes不带任何数据,将是最实用的情况
	3.多重继承有正当的用途,其中一个是"pulic继承interface class和private继承某个协助实现的class的两相组合""


模板与泛型编程
41.了解隐式接口与编译器多态
	1.classes与templates都支持接口(interfaces)和多态(polymorphism)
	2.对于classes而言接口是显示的以函数签名为中心.多态则是通过virtual函数发生于运行期(动态绑定)
	3.对于templates而言,接口是隐式的,奠基于有效表达式.多态则是通过template具现化和函数重载解析发生于编译期.
42.了解typename的双重意义
	1.声明template参数时,前缀关键字typename和class可以互换
	2.关键字typename可以用来标识嵌套从属类型名称,但是不得在base class lists(基类列)或者member initialization list(成员值初始列)内以它作为base class修饰符

43.学习处理模版化基类的名称
	1.可以在derived class template中通过this-> 指涉及base class templates内的成员名称
	2.借由一个明白写出的"base class资格修饰符"完成
	usiing base_templte<T>::function_name;

44.将与参数无关的代码抽离templates
	1.templates生成多个class和函数,所以任何template都不应该与某个造成膨胀的template参数产生相依关系
	2.因非模版类型参数(non-type template parameters)而造成的膨胀,往往可以消除.做法是利用函数参数或者class成员变量来替换template参数
	3.因类型参数(type parameters)而造成的代码膨胀,往往可以降低.做法是让带有完全相同二进制表述的具现类型共享实现码.

45.运用成员函数模板接受所有兼容类型
	1.使用member function templates(成员函数模板)生成"可接受所有兼容类型"的函数
	2.如果你声明member templates用于"泛化copy构造"或者"泛化assignment"操作,你还是需要声明正常的copy构造函数和copy assignment操作符

46.需要类型转换时请为模板定义非成员函数
	1.当我们编写一个class template时,而它提供与此template相关的函数支持"所有参数之隐式类型转换"时,请将那些函数定义为"class template"内部的friend函数

47.使用traits classes表现类型信息
	how to use trait class?
		1.建立一组重载函数或函数模板,彼此间的差异只在于各自的trait参数.令每个函数实现与其接受之的traits信息相互对应
		2.建立一个控制函数或函数模板,它调用上述的那些"重载函数"并传递traits class所传递的信息.
	1.traits class使得"类型"相关信息在编译期间可用, 它们以templates和templates特化完成实现
	2.整合重载技术后, traits classes有可能在编译期间对类型执行if else测试

48.template 元编程
	1.将工作由运行期转向编译期,因而得以实现早期错误侦测和更高的执行效率
	2.可被用来生成"基于政策选择组合"的客户定制代码~~,也可以用来避免生成对某些类型不适合的代码

定制new和delete

49.了解new-handler的行为
	1.set_new_handler允许客户指定一个函数,在内存分配无法满足时得到调用
	2.Nothrow new是个比较局限的工具,因为仅仅适用于分配内存.但是在构造函数调用时还是会出现抛出异常的情况

50.了解new和delete的合理替换时机
	1.有很多理由需要自己写new和delete,包括改善效能、对heap运用错误进行调试及手收集heap使用信息

51.编写new和delete时需要固守成规
	1.operator new应该内包含一个无穷循环,并且在其中尝试分配内存.如果它无法满足内存分配需求,就应该调用new-handler.应该有能力处理0byte申请.class专属版本还应该能够处理"比正确大小更大的(错误)申请"
	2.operator delete应该在接收到null指针时候不做任何事情.class专属版本还应该能够处理"比正确大小更大的(错误)申请"

52.写了palcement new也要写placement delete
	1.当你写了palcement new,对应的palcement delete也要写出来.如果没有这样做,你的程序可能发生时续时断的内存泄漏
	2.当你声明了placement new 和 placement delete,请不要无意识的掩盖了它们的正常版本.

杂项

53.不要忽略编译器告警

54.熟悉包括TR1内的标准库

55.熟悉Boost
