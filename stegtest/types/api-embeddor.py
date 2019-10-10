from abc import ABC, abstractmethod
from stegtest.types.embeddor import Embeddor

class API-Embeddor(Embeddor):
    def __init__(self, API)
        self.API = API

    def initialize(self, *args):
        continue

    def embed(self, path_to_image, path_to_output):
        self.API.embed(path_to_image, path_to_output)



