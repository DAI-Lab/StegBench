from abc import ABC, abstractmethod

class Downloader(ABC):

	@abstractmethod
    def initialize(self, *args):
        pass

    @abstractmethod
    def download(self, output_directory):
    	pass