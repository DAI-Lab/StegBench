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

found = multiprocessing.Value('i', 0)

# -- APPENDED FILES --

def extra_size(filename):
    print("WARNING! not implemented")

    name=ntpath.basename(filename)
    I = misc.imread(filename)

    misc.imsave(tempfile.gettempdir()+'/'+name, I)
    return 0


# -- EXIF --

# {{{ exif()
def exif(filename):
    image = Image.open(filename)
    try:
        exif = { TAGS[k]: v for k, v in image._getexif().items() if k in TAGS }
        return exif

    except AttributeError:
        return {}
# }}}


# -- SAMPLE PAIR ATTACK --

# {{{ spa()
"""
    Sample Pair Analysis attack. 
    Return Beta, the detected embedding rate.
"""
def spa(filename, channel=0): 

    if channel!=None:
        I3d = misc.imread(filename)
        width, height, channels = I3d.shape
        I = I3d[:,:,channel]
    else:
        I = misc.imread(filename)
        width, height = I.shape

    x=0; y=0; k=0
    for j in range(height):
        for i in range(width-1):
            r = I[i, j]
            s = I[i+1, j]
            if (s%2==0 and r<s) or (s%2==1 and r>s):
                x+=1
            if (s%2==0 and r>s) or (s%2==1 and r<s):
                y+=1
            if round(s/2)==round(r/2):
                k+=1

    if k==0:
        print("ERROR")
        sys.exit(0)

    a=2*k
    b=2*(2*x-width*(height-1))
    c=y-x

    bp=(-b+sqrt(b**2-4*a*c))/(2*a)
    bm=(-b-sqrt(b**2-4*a*c))/(2*a)

    beta=min(bp.real, bm.real)
    return beta
# }}}


# -- RS ATTACK --

# {{{ solve()
def solve(a, b, c):
    sq = np.sqrt(b**2 - 4*a*c)
    return ( -b + sq ) / ( 2*a ), ( -b - sq ) / ( 2*a )
# }}}

# {{{ smoothness()
def smoothness(I):
    return ( np.sum(np.abs( I[:-1,:] - I[1:,:] )) + 
             np.sum(np.abs( I[:,:-1] - I[:,1:] )) )
# }}}

# {{{ groups()
def groups(I, mask):
    grp=[]
    m, n = I.shape 
    x, y = np.abs(mask).shape
    for i in range(m-x):
        for j in range(n-y):
            grp.append(I[i:(i+x), j:(j+y)])
    return grp
# }}}

# {{{ difference()
def difference(I, mask):
    cmask = - mask
    cmask[(mask > 0)] = 0
    L = []
    for g in groups(I, mask):
        flip = (g + cmask) ^ np.abs(mask) - cmask
        L.append(np.sign(smoothness(flip) - smoothness(g)))
    N = len(L)
    R = float(L.count(1))/N
    S = float(L.count(-1))/N
    return R-S
# }}}

# {{{ rs()
def rs(filename, channel=0):
    I = misc.imread(filename)
    if channel!=None:
        I = I[:,:,channel]
    I = I.astype(int)

    mask = np.array( [[1,0],[0,1]] )
    d0 = difference(I, mask)
    d1 = difference(I^1, mask)

    mask = -mask
    n_d0 = difference(I, mask)
    n_d1 = difference(I^1, mask)

    p0, p1 = solve(2*(d1+d0), (n_d0-n_d1-d1-3*d0), (d0-n_d0)) 
    if np.abs(p0) < np.abs(p1): 
        z = p0
    else: 
        z = p1

    return z / (z-0.5)
# }}}

        threshold=0.05s

        # I = misc.imread(sys.argv[2])
        # if len(I.shape)==2:
        #     bitrate=attacks.rs(sys.argv[2], None)
        #     if bitrate<threshold:
        #         print("No hidden data found")
        #     else:
        #         print("Hiden data found", bitrate)
        # else:
        #     bitrate_R=attacks.rs(sys.argv[2], 0)
        #     bitrate_G=attacks.rs(sys.argv[2], 1)
        #     bitrate_B=attacks.rs(sys.argv[2], 2)

        #     if bitrate_R<threshold and bitrate_G<threshold and bitrate_B<threshold:
        #         print("No hidden data found")
        #         sys.exit(0)

        #     if bitrate_R>=threshold:
        #         print("Hiden data found in channel R", bitrate_R)
        #     if bitrate_G>=threshold:
        #         print("Hiden data found in channel G", bitrate_G)
        #     if bitrate_B>=threshold:
        #         print("Hiden data found in channel B", bitrate_B)
        #     sys.exit(0)

# -- CALIBRATION --

# {{{ calibration()
def calibration(filename): 

    if not utils.which("convert"):
        print("Error: 'convert' tool not found, please install it.\n")
        sys.exit(0)

    tmpdir = tempfile.mkdtemp()
    predfile = os.path.join(tempfile.mkdtemp(), 'pred.jpg')
    os.system("convert -chop 2x2 "+filename+" "+predfile)
 
    im_jpeg = JPEG(filename)
    impred_jpeg = JPEG(predfile)
    found = False
    for i in range(im_jpeg.components()):
        dct = np.abs(im_jpeg.coeffs(i).flatten())
        dctpred = np.abs(impred_jpeg.coeffs(i).flatten())
        Hs0 = sum(dct==0)
        Hs1 = sum(dct==1)
        Hp0 = sum(dctpred==0)
        Hp1 = sum(dctpred==1)
        Hp2 = sum(dctpred==2)

        beta = (Hp1*(Hs0-Hp0) + (Hs1-Hp1)*(Hp2-Hp1)) / (Hp1**2 + (Hp2-Hp1)**2)
        # XXX: Incomplete implementation. Check http://www.ws.binghamton.edu/fridrich/Research/mms100.pdf

        if beta > 0.05:
            print("Hidden data found in channel "+str(i)+":", beta)
            found = True

    if not found:
        print("No hidden data found")

    shutil.rmtree(tmpdir)
# }}}


# -- NAIVE ATTACKS

# {{{ high_pass_filter()
def high_pass_filter(input_image, output_image): 

    I = misc.imread(input_image)
    if len(I.shape)==3:
        kernel = np.array([[[-1, -1, -1],
                            [-1,  8, -1],
                            [-1, -1, -1]],
                           [[-1, -1, -1],
                            [-1,  8, -1],
                            [-1, -1, -1]],
                           [[-1, -1, -1],
                            [-1,  8, -1],
                            [-1, -1, -1]]])
    else:
        kernel = np.array([[-1, -1, -1],
                           [-1,  8, -1],
                           [-1, -1, -1]])


    If = ndimage.convolve(I, kernel)
    misc.imsave(output_image, If)
# }}}

# {{{ low_pass_filter()
def low_pass_filter(input_image, output_image): 

    I = misc.imread(input_image)
    if len(I.shape)==3:
        kernel = np.array([[[1, 1, 1],
                            [1, 1, 1],
                            [1, 1, 1]],
                           [[1, 1, 1],
                            [1, 1, 1],
                            [1, 1, 1]],
                           [[1, 1, 1],
                            [1, 1, 1],
                            [1, 1, 1]]])
    else:
        kernel = np.array([[1, 1, 1],
                           [1, 1, 1],
                           [1, 1, 1]])

    kernel = kernel.astype('float32')/9
    If = ndimage.convolve(I, kernel)
    misc.imsave(output_image, If)
# }}}



# {{{ remove_alpha_channel()
def remove_alpha_channel(input_image, output_image): 

    I = misc.imread(input_image)
    I[:,:,3] = 255;
    misc.imsave(output_image, I)
# }}}

