from abc import ABC, abstractmethod

class Trainer(ABC):
    @abstractmethod
    def __init__(self, *args):
        pass

    @abstractmethod
    def train(self, db_hash, detector_hash):
        pass

