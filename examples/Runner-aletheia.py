#Code based of https://github.com/daniellerch/aletheia
import os
import sys
import shutil
import ntpath
import tempfile
import subprocess

from aletheialib import stegosim, utils

import numpy as np
from scipy import ndimage, misc
from cmath import sqrt

from PIL import Image
from PIL.ExifTags import TAGS

from aletheialib.jpeg import JPEG

import multiprocessing
from multiprocessing.dummy import Pool as ThreadPool 
from multiprocessing import cpu_count

# {{{ lsbm()
def lsbm(path, payload):
    X = misc.imread(path)
    sign=[1, -1]
    for j in range(X.shape[0]):
        for i in range(X.shape[1]):
            if random.randint(0,99)>int(float(payload)*100):
                continue
 
            if len(X.shape)==2:
                k=sign[random.randint(0, 1)]
                if X[i, j]==0: k=1
                if X[i, j]==255: k=-1
                if X[i, j]%2!=random.randint(0,1): # message
                    X[i, j]+=k
            else:
                kr=sign[random.randint(0, 1)]
                kg=sign[random.randint(0, 1)]
                kb=sign[random.randint(0, 1)]
                if X[i, j][0]==0: kr=1
                if X[i, j][1]==0: kg=1
                if X[i, j][2]==0: kb=1
                if X[i, j][0]==255: kr=-1
                if X[i, j][1]==255: kg=-1
                if X[i, j][2]==255: kb=-1
                # message
                if X[i, j][0]%2==random.randint(0,1): kr=0
                if X[i, j][1]%2==random.randint(0,1): kg=0
                if X[i, j][2]%2==random.randint(0,1): kb=0
                X[i, j]=(X[i,j][0]+kr, X[i,j][1]+kg, X[i,j][2]+kb)
    return X
# }}}

# {{{ lsbr()
def lsbr(path, payload):
    X = misc.imread(path)
    sign=[1, -1]
    for j in range(X.shape[0]):
        for i in range(X.shape[1]):
            if random.randint(0,99)>int(float(payload)*100):
                continue
 
            if len(X.shape)==2:
                k=sign[random.randint(0, 1)]
                if X[i, j]==0: k=1
                if X[i, j]==255: k=-1
                if X[i, j]%2!=random.randint(0,1): # message
                    if X[i, j]%2==0: X[i, j]+=1
                    else: X[i, j]-=1
            else:
                # message
                kr=0; Kg=0; kb=0

                if X[i, j][0]%2==0: kr=1
                else: kr=-1

                if X[i, j][1]%2==0: kg=1
                else: kg=-1

                if X[i, j][2]%2==0: kb=1
                else: kb=-1

                if X[i, j][0]%2==random.randint(0,1): kr=0
                if X[i, j][1]%2==random.randint(0,1): kg=0
                if X[i, j][2]%2==random.randint(0,1): kb=0
                X[i, j]=(X[i,j][0]+kr, X[i,j][1]+kg, X[i,j][2]+kb)
    return X
# }}}


import sys
from os import path
from os.path import abspath, join
import stegbench.utils.filesystem as fs

class Runner(object):
    """docstring for Processor"""
    def embed(input_file, output_file, *args):
        raise NotImplementedError

    def detect(input_file, output_file, *args):
        raise NotImplementedError

if __name__ == "__main__":
    args = sys.argv[1:]

    assert(len(args) == 3)
    input_file = args[0]
    result_file = args[1]
    args = args[2]

    runner = Runner()
    runner.embed(input_file, output_file, args)
    runner.detect(input_file, output_file, args)

