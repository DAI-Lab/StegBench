from abc import ABC, abstractmethod

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

    @abstractmethod
    def detect_bulk(self, input_list, path_to_directory):
        pass