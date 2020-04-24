
from pyhanlp import *

def load_dict()->set:

	IOUtil = JClass('com.hankcs.hanlp.corpus.io.IOUtil')
	path = HanLP.Config.CoreDictionaryPath.replace('.txt', '.mini.txt')
	dic = IOUtil.loadDictionary([path])
	return set(dic.keySet())


if __name__ == "__main__":
	dic = load_dict()
	print(len(dic))
	print(dic)