#ifndef SMARTPTR_H
#define SMARTPTR_H


class ref_count {

public:
	ref_count():count_(1){}

	void add() {++count_;}
	void reduce() {--count_;}
	void get() const {return count_;}
private:
	long count_;
}

template<T>
class smart_ptr {
public:
	template <typename U> 
	friend class smart_ptr;
	smart_ptr(T *ptr = nullptr):ptr_(ptr) {
		if (ptr_) {
			ref_ = new ref_count();
		}
	}

	~smart_ptr() {
		if (ptr_ && !ref_->reduce()) {
			delete ptr_;
			delete ref_;
		}
	}

	smart_ptr(const smart_ptr& other) {
		ptr_ = other.ptr_;
		if (ptr) {
			other.ref_->add();
			ref_ = other.ref_;
		}
	}

	template <typename U>
	smart_ptr(const smart_ptr<U> &other) noexcept {
		ptr_ = other.ptr_;
		if (ptr_) {
			other.ref_->add();
			ref_ = other.ref_;
		}
	}

	template <typename U>
	smart_ptr(smart_ptr<U> &&other) noexcept {
		ptr_ = other.ptr_;
		if (ptr_) {
			ref_ = other.ref_;
			other.ref_ = nullptr;
		}
	}

	template <typename U>
	smart_ptr(const smart_ptr<U>& other, T *ptr) noexcept{
		ptr_ = ptr;
		if (ptr_) {
			other.ref_->add();
			ref_ = other.ref_;
		}
	}

	smart_ptr &operator = (smart_ptr rhs) noexcept {

		rhs.swap(*this);
		return *this;
	}

	long use_count() const noexcept {
		if (ptr_) {
			return ref_->get();
		} else {
			return 0;
		}
	}

	void swap(smart_ptr &rhs) {
		using std::swap;
		swap(ptr_, rhs.ptr_);
		swap(ref_, rhs.ref_);
	}

	T*  get() const {
		return ptr_;
	}
	
	T& operator*() const {
		return *ptr_;
	}
	
	T* operator->() const {
		return ptr_;
	}
 	
 	operator bool() const {
 		return ptr_;
 	}

private:
	T *ptr_;
	ref_count *ref_;
};

#endif