from abc import ABC, abstractmethod

class Generator(ABC):

	@abstractmethod
    def initialize(self, *args):
        pass

    @abstractmethod
    def connect(self, db_info):
    	pass

    @abstractmethod
    def parse(self, )
    	pass

   