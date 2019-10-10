from abc import ABC, abstractmethod

class Scheduler(ABC):

	@abstractmethod
    def train(self, path_to_directory):
        pass

    @abstractmethod
    def detect_bulk(self, path_to_directory):
        pass

    @abstractmethod
    def detect(self, path_to_file):
        pass