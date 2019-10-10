from abc import ABC, abstractmethod

class Embeddor(ABC):

    @abstractmethod
    def __init__(self, *args):
        pass

    @abstractmethod
    def embed(self, path_to_image, path_to_output):
        pass

  	## TODO - declare this abstract?? ###
    def embed_bulk(self, input_list, output_list):
    	assert(len(input_list) == len(output_list))

    	num_images = len(input_list)

    	for i in range(num_images): #can parallelize this code a lot
    		self.embed(input_list[i], output_list[i])

