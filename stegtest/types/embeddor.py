from abc import ABC, abstractmethod
from pathos.multiprocessing import ProcessingPool as Pool
from functools import partial

import inspect

import stegtest.utils.lookup as lookup

class Embeddor(ABC):

    # def __init__(self, docker_config):
    #     raise NotImplementedError

    def embed_bpp(self, bpp:float, file_input_info:dict, path_to_output:str):
        """THIS WILL ORCHESTRATE THE EMBEDDING PROCESS AND SEND OUT COMMANDS TO THE DOCKER FILES"""

        """
        WILL READ SELF.DOCKERCONFIG FOR SPECIFIC INFORMATION TO GENERATE THE SPECIFIC INPUT
        WILL GENERATE THE COMMAND 

        """
        secret_txt = lookup.generate_secret_text(file_input_info, bpp)

        #get params -- can pull this out of this function in next iteration of cleanup
        args = inspect.signature(self.embed)
        parameters = list((tuple(args.parameters.values())))
        filtered_parameters = list(filter(lambda p: p.name not in ['self', 'path_to_input', 'path_to_output', 'secret_txt'], parameters))
        generated_params = [lookup.generate_param(parameter.annotation.__name__) for parameter in filtered_parameters]
        
        #clean this up
        self.embed(file_input_info[lookup.file_path], path_to_output, secret_txt, *generated_params)
        
    @abstractmethod
    def embed(self, path_to_input:str, path_to_output:str, secret_txt:str, *args):
        raise NotImplementedError

    def embed_bulk(self, bpp, input_list, output_list):
        pool = Pool().map
        pool(self.embed_bpp, bpp, input_list, output_list)