from abc import ABC, abstractmethod

class Extractor(ABC):

	@abstractmethod
    def train(self, path_to_directory):
        pass

    @abstractmethod
    def detect_bulk(self, path_to_directory):
        pass

    @abstractmethod
    def detect(self, path_to_file):
        pass