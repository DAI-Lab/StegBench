from abc import ABC, abstractmethod

class API(ABC):
    @abstractmethod
    def load_image(self, path_to_image):
        pass

    @abstractmethod
    def embed_image(self, path_to_image, path_to_output):
        pass