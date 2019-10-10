from abc import ABC, abstractmethod

class Pipeline(ABC):

	@abstractmethod
	def __init__(self, *args):

	@abstractmethod
	def _loadDB(self, ):
		pass

	@abstractmethod
	def _generateTestDB(self, ):
		pass

	@abstractmethod
	def _test(self, ):
		pass
