import re
import jieba
from collections import Counter
import numpy as np

class KeyWordExtractor(object):

	def __init__(self):
		pass

	def add(self):
		return NotImplemented

	def train(self):
		return NotImplemented

	def getKeyWord(self):
		return NotImplemented

class TfCounter(KeyWordExtractor):

	def __init__(self, stopped = False, stopwords_path = None):
		self.stopped = stopped
		self.stopwords_path = stopwords_path
		self.words_list = []
		self.cnt = Counter()

	def add(self, document):

		self.words_list.expand(jieba.lcut(document))

	def train(self):
		
		self.cnt.update(self.words_list)

	def top(self, n):
		return self.cnt.most_common(n)

	def getKeyWords(self, document, n = None):

		return Counter(jieba.lcut(document)).most_common(n)

# tf = TfCounter()
# print(tf.getKeyWords("女排夺冠观众欢呼欢呼女排", 3))


class TfidfCounter(KeyWordExtractor):

	def __init__():
		self.tf = dict()
		self.idf = dict()
		self.id2doc = dict()
		self.words = set()

	def add(self, id, document):
		
		words = jieba.lcut(document)
		self.id2doc[id] = words
		self.words.update(words)
		self.doclens = len(self.id2doc)

	def train(self, document):
		
		for item in self.id2doc.keys():
			self.tf[item] = Counter(self.id2doc[item])

		for word in self.words:
			self.idf.setdefault(word, 0)
			for item in self.id2doc.keys():
				if self.tf[item][word] != 0:
					self.idf[word] += 1

		for word in self.idf.keys():
			self.idf[word] = np.log(doclens / self.idf[word]) + 1
	def documents(self):
		pass

	def getKeyWords(self, document):
		pass
