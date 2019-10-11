from abc import ABC, abstractmethod

class Tester(ABC):
    @abstractmethod
    def __init__(self, *args):
        pass

    @abstractmethod
    def test(self, db_hash, detect_set):
        pass

