from abc import ABC, abstractmethod
from pathos.multiprocessing import ProcessingPool as Pool

class Detector(ABC):

    @abstractmethod
    def __init__(self, *args):
        pass

    @abstractmethod
    def train(self, path_to_directory):
        pass

    @abstractmethod
    def detect(self, path_to_input):
        pass

    def detect_bulk(self, input_list, path_to_directory=None):
        pool = Pool().map
        results = pool(self.detect, input_list)
        return results