## C++ 多态

C++中的多态可以划分为静态多态和动态多态.

* 静态多态, 通过template具现化和函数重载解析发生在编译期

  ~~~c++
  class A {
  public:
  	void draw() {cout << "class A" << endl;}
  };
  
  class B {
  public:
  	void draw() {cout << "class B" << endl;}
  };
  
  class C {
  public:
  	void draw() {cout << "class C" << endl;}
  };
  
  template <typename T>
  void draw(T &t) {
  	t.draw();
  }
  
  int main() {
      A a;
  	B b;
  	C c;
  	
      draw(a);
  	draw(b);
  	draw(c);
  }
  ~~~



* 动态多态, 通过virtual函数发生在运行期

  ~~~C++
  class Graph {
  public:
  	virtual void draw() {
  		cout << "Graph Class" << endl;
  	}
  
  	void area() {
  		cout << "Graph Area" << endl;
  	}
  };
  
  class Cricle:public Graph {
  public:
  	virtual void draw() {
  		cout << "Cricle Class" << endl;
  	}
  
  	void area() {
  		cout << "Cricle Area" << endl;
  	}
  
  };
  
  
  class Line:public Graph {
  public:	
  	virtual void draw() {
  		cout << "Line Class" << endl;
  	}
  
  	void area(int x) {
  		cout << "Line Area" << endl;
  	}
  
  };
  
  class Square:public Graph {
  public:	
  	void area(float c) {
  		cout << "Square Area" << endl;
  	}
  };
  
  int main() {
      Line l;
  	Cricle c;
  	Square s;
  
  	l.draw();
  	c.draw();
  	s.draw();
  
  	c.area();
  	l.area(1);
  	s.area(1.0);
  
  }
  ~~~

  在继承状态下,在基类与子类函数名相同的前提下，根据参数是否相同、是否具有vritual关键字，可分为4种情况：

  * 参数相同、有virtual关键字: 多态重写
  * 参数相同、无virtual关键字: 隐藏; 与重写区分
  * 参数不同、有virtual关键字: 隐藏; 与重载区分
  * 参数不同、无virtual关键字: 隐藏; 与重载区分

  

  如果基类函数是纯虚函数, 则子类必须重写该函数. 此外, 如果基类函数是虚函数,但子类没有进行重写, 则子类默认使用基类函数.

  