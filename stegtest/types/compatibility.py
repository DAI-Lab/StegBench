from stegtest.utils.lookup import compatibile_types_decorator

def register(*decorators):
    def register_wrapper(func):
        for deco in decorators[::-1]:
            func = deco(func)
        func.compatibile_types = decorators        
        return func
    return register_wrapper

##TODO check if function parameters are correct for the type <- ie only jpeg input etc. and then the register function can verify that at least
#one of the decorators holds true <- this is more for v1 

def file_check(function):
	return function

def bmp(function):
	return function

def gif(function):
	return function

def jpeg(function):
	return function

def jpg(function):
	return function

def pgm(function):
	return function

def png(function):
	return function


