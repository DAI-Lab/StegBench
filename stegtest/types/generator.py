from abc import ABC, abstractmethod

class Generator(ABC):

	@abstractmethod
	def __init__(self, *args):
		pass

	@abstractmethod
	def generate(self, *args):
		pass