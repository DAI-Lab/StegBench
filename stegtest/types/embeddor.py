from abc import ABC, abstractmethod
from pathos.multiprocessing import ProcessingPool as Pool
from functools import partial

class Embeddor(ABC):

    @abstractmethod
    def __init__(self, *args):
        pass

    @abstractmethod
    def embed(self, path_to_image, path_to_output):
        raise NotImplementedError

    @abstractmethod
    def update_parameters(self, *args):
        raise NotImplementedError

    def embed_bulk(self, input_list, output_list):
        pool = Pool().map
        pool(self.embed, input_list, output_list)