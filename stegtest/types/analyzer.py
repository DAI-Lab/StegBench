from abc import ABC, abstractmethod

class Analyzer(ABC):

	@abstractmethod
	def __init__(self, *args):
		pass

	@abstractmethod
	def analyze(self, *args):
		pass