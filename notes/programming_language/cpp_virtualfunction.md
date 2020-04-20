## C++ 虚函数

### 虚函数

在C++的世界里, 动态多态的实现依赖于虚函数. 在class中虚函数用virtual关键字来表示.

~~~c++
class Base {
public:
    Base() {}
    virtual ~Base() {}
	virtual void draw(); // 虚函数
	virtual void area() = 0; // 纯虚函数
};
~~~



在c++中, 基类中的某个成员函数是纯虚函数还是非纯虚函数, 对于子类而言,  对于该成员函数的处理方式是不同的.

* 成员函数是纯虚函数
  * 子类必须重写该函数, 在子类中实现子类版本; 否则会编译报错.
* 成员函数是虚函数
  * 如果子类中不对该函数重写, 则默认继承基类的虚函数实现
  * 如果子类中对该函数重写,  则需要在子类中实现子类版本

~~~C++
class Base {
public:
	Base() {}
	virtual ~Base() {}

	virtual void draw() {
		std::cout << "Base draw" << std::endl;
	}

	virtual void area() {
		std::cout << "Base area" << std::endl;		
	}
    virtual void length() = 0; // 子类必须重写,否则编译报错.
};

class Derived:public Base {
public:
	Derived(){};
	~Derived() {};

	void draw() {
		std::cout << "Derived draw" << std::endl;		
	}
	void length() {
        std::cout << "Derived length" << std::endl;
    }
};

int main() {
	Derived d;
	d.draw();
	d.area();
}
~~~



一个class中如果拥有了一个纯虚函数, 则被称为抽象基类. 无法定义对象, 但是可以定义引用或者指针.



### 内存布局与虚函数表

众所周知, class由成员变量和成员函数组成.

 * 成员变量
   	* 静态成员变量
   	* 非静态成员变量
 * 成员函数
   	* 静态成员函数
    * 非静态成员函数
      	* 虚函数
      	* 非虚函数

* 静态成员部分本身是不对内存布局有所影响的.

~~~C++
class Base {
public:
	int x;
	int y;
};

class BaseStatic {
public:
	int x;
	int y;
	static int var;
};

int main() {
	std::cout << sizeof(Base) << std::endl;
	std::cout << sizeof(BaseStatic) << std::endl;
	/* 这两个class的sizeof的结果是一样的 */
}
~~~



* 同样非虚成员函数和静态成员函数对class的内存布局也是没有影响的.

~~~C++
class Base{
public:
	int x;
	int y;
};

class BaseStatic {
public:
	void draw() {
		std::cout << "Base draw"  << std::endl;
	};
	
	static void area() {
		std::cout << "Static area" << std::endl;
	}

public:
	int x;
	int y;
};

int main() {
    std::cout << sizeof(Base) << std::endl;
	std::cout << sizeof(BaseStatic) << std::endl;
    /* 这两个class的sizeof的结果是一样的 */
}
~~~



* 虚成员函数对class的内存布局是有影响的

~~~C++
class Base{
public:
	Base() {}
	~Base() {}
public:
	int x;
	int y;
};

class BaseVirtual {
public:
	BaseVirtual() {}
	virtual ~BaseVirtual() {}
public:
	int x;
	int y;
};

int main() {
	std::cout << sizeof(Base) << std::endl;
	std::cout << sizeof(BaseVirtual) << std::endl;

	Base b;
	BaseVirtual vb;
	std::cout << "The base class addr " << &b << std::endl;
	std::cout << "The base member X addr " << &b.x << std::endl;
	/* 对于b而言, b的地址和b.x的地址相同*/
    
	std::cout << "The base class addr " << &vb << std::endl;
	std::cout << "The base member X addr " << &vb.x << std::endl;
	/* 对于vb而言, 在g++下， 由于虚函数的存在, vb的地址和vb.x的地址不同. 虚函数指针在class的前端*/
}
~~~

 在深度探索c++对象模型一书中提到过, 虚函数是通过虚函数表来实现的, 而class存储了虚函数指针指向虚函数表. 而虚函数指针要么被放在class的前端,要么被放在class的尾端.



* 单一继承

  ~~~C++
  class Point {
  public:
  	Point(float x = 0.0) {}
  	virtual ~Point() {}
  	virtual Point& mult(float) = 0;
  	float x() const {return x_;}
  	virtual float y() const {return 0;}
  	virtual float z() const {return 0;}
  
  private:
  	float x_;
  };
  
  
  class Point2d:public Point{
  public:
  	Point2d(float x = 0.0, float y = 0.0):Point(x), y_(y){}
  	~Point2d() {};
  
  	Point2d& mult(float) {
  
  	}
  
  	float y() const {return y_;}
  private:
  	float y_;
  };
  
  class Point3d:public Point2d{
  public:
  	Point3d(float x = 0.0, float y = 0.0, float z = 0.0):Point2d(x,y), z_(z){}
  	~Point3d() {};
  
  	Point3d& mult() {
  
  	}
  
  	float z() const {return z_;}
  private:
  	float z_;
  };
  
  
  ~~~

  * 对于Point的内存布局来说,可能是这样的

    * x_
    * point vptr
      * type_info for Point
      * Point:~Point()
      * pure_virtual_called()
      * Point: y()
      * Point: z()

  * 对于Ponit2d的内存布局来说,可能是这样的

    * x_
    * point vptr
      * type_info for Point2d
      * Point2d:~Point2d()
      * Point2d: mult()
      * Point2d: y()
      * Point: z()
    * y_

    对于一个继承了基类的子类来说, 可能有三种可能性

    1. 它可以继承base classes所声明的virtual function的实例, 正确的来说该函数实例的地址会被拷贝到derived class的virtual table相对应的slot中
    2. 它可以使用自己的函数实例,这表示它自己的函数实例必须在对应的slot中
    3. 它可以加入一个新的virtual function, 这时候virtual table的尺寸会增大一个slot. 而新的实例函数的地址会被放进该slot中.

* 多重继承

  多重继承的虚函数表比较复杂~~一般而言

  * 对于通过第一个基类指针访问时, 不需要调整thisz指针. 其virtual table slot需要放置真正的destructor地址
  * 对于通过第二个以后的基类指针访问时, 需要调整this指针. 其virtual table slot需要相关的thunk地址

~~~C++
class Base1 {
public:
	Base1() {}
	virtual ~Base1() {}
	virtual void speak() {}
	virtual Base1 *clone() const {

	}

private:
	float data1;
};

class Base2 {
public:
	Base2() {}
	virtual ~Base2() {}
	virtual void mute() {}
	virtual Base2 *clone() const {

	}

private:
	float data2;
};


class Derived:public Base1, public Base2 {
public:
	Derived(){}
	virtual ~Derived(){}

	virtual Derived *clone() const {

	}
private:
	float datad;
};

~~~

* 虚继承

  虚继承可以解决菱形继承引发的二义性问题,  同样它virtual table布局也很复杂



 对于一个class而言, 实际大小受到以下几点影响

* 语言本身本身带来的影响, 比如虚函数指针
* 编译器对某些特殊情况提供的优化处理, 比如 empty class的大小 g++上1 byte.
* Alignment对齐的限制



###  参考书目

* 深度探索C++对象模型
* c++ primer(第五版, 中文版)
*  https://en.cppreference.com/w/cpp/language/member_functions 

