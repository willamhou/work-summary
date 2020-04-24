from utility import load_dict



def fully_segment(text:str, dic:dict)->list:
	"""
	1.枚举出文本中全部可能出现的词
	2.如果可能出现的词在字典里,则认为其是一个词
	"""
	words_list = []

	text_len = len(text)
	for i in range(text_len):
		for j in range(i + 1, text_len + 1):
			word = text[i:j]
			if word in dic:
				words_list.append(word)

	return words_list


def forward_segment(text:str, dic:dict)->list:
	words_list = []
	text_len = len(text)
	i = 0
	while i < text_len:
		longest_word = text[i]
		for j in range(i + 1, text_len + 1):
			word = text[i:j]

			if word in dic:
				if len(word) > len(longest_word):
					longest_word = word
		i += len(longest_word)
		words_list.append(longest_word)

	return words_list

def backward_segment(text:str, dic:dict)->list:
	words_list = []
	text_len = len(text)
	i = text_len - 1
	while i >= 0:
		longest_word = text[i]
		for j in range(0, i):
			word = text[j:i + 1]

			if word in dic:
				if len(word) > len(longest_word):
					longest_word = word
		i -= len(longest_word)
		words_list.append(longest_word)

	words_list.reverse()
	return words_list

def count_single(words:list):
	return sum(1 for word in words if len(word) == 1)

def bi_segment(text:str, dic:dict)->list:
	f = forward_segment(text, dic)
	b = backward_segment(text, dic)

	if len(f) < len(b):
		return f
	elif len(f) > len(b):
		return b
	else:
		if (count_single(f) < count_single(b)):
			return f
		else:
			return b

if __name__ == "__main__":
	dic = load_dict()
	words = fully_segment("商品和服务", dic)
	print(words)

	words = forward_segment("研究生命的起源", dic)
	print(words)

	words = backward_segment("研究生命的起源", dic)
	print(words)

	words = bi_segment("当下雨天地面积水", dic)
	print(words)