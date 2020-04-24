

class Node(object):
	def __init__(self, value)->None:

		self._children = {}
		self._value = value

	def _add_child(self, char, value, overwrite = False):
		child = self._children.get(char)

		if child is None:
			print("char is {}".format(char))
			child = Node(value)
			self._children[char] = child

		elif overwrite:
			print(char, value)
			child._value = value
		return child

class Trie(Node):
	def __init__(self)->None:
		super().__init__(None)

	def __contains__(self, key):
		return self[key] is not None

	def __getitem__(self, key):
		state = self
		for char in key:
			state = state._children.get(char)

			if state is None:
				return None

		return state._value

	def __getall__(self):
		pass
		# state = self
		# while (state):
		# 	for item in state._children.keys():
		# 		print(item)
		# 		state = state._children.get(item)
		# 		print(state)

	def __setitem__(self, key, value):
		state = self

		for i, char in enumerate(key):
			if i < len(key) - 1:
				state = state._add_child(char, None, False)
				print("add None")
			else:
				print("add Value")
				state = state._add_child(char, value, True)

if __name__ == "__main__":
	trie = Trie()

	trie["自然"] = "nature"
	# trie["自然语言处理"] = "NLP"

	print(trie.__getitem__("自然"))

	trie["自然语言处理"] = "NLP"
	trie["自然语人处理"] = "NLR"
	trie["自然语言"] = "NL"


	print(trie._children["自"]._children["然"]._children["语"]._children)

	trie["自然"] = None
	trie["自然语言"] = "PNL"
