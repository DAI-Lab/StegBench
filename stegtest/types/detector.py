from abc import ABC, abstractmethod
from pathos.multiprocessing import ProcessingPool as Pool

class Detector(ABC):

    @abstractmethod
    def __init__(self, detector_set):
        pass

    @abstractmethod
    def detect(self, testdb:str, output_file:str=None):
        pass