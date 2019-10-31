from abc import ABC, abstractmethod

class Embeddor(ABC):
    @abstractmethod
    def __init__(self, embeddor_set):
        pass

    @abstractmethod
    def embed(self, source_db:str, embedding_ratio:float):
        pass