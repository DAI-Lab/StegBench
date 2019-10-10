from abc import ABC, abstractmethod

class Processor(ABC):

	@abstractmethod
    def initialize(self, *args):
        pass

    @abstractmethod
    def connect(self, db_info):
    	pass

    @abstractmethod
    def parse(self, )
    	pass

   