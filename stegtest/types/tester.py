from abc import ABC, abstractmethod

class Embeddor(ABC):
    @abstractmethod
    def initialize(self, *args):
        pass

    @abstractmethod
    def embed(self, path_to_image, path_to_output):
        pass

