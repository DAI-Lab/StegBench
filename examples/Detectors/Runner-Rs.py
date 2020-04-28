import sys
import imageio
import numpy as np
from cmath import sqrt
import stegbench.utils.filesystem as fs

##Code from https://github.com/daniellerch/aletheia/tree/master/aletheialib

class Runner(object):
    """docstring for Runner"""
    def solve(self, a, b, c):
        sq = np.sqrt(b**2 - 4*a*c)
        return ( -b + sq ) / ( 2*a ), ( -b - sq ) / ( 2*a )

    def smoothness(self, I):
        return ( np.sum(np.abs( I[:-1,:] - I[1:,:] )) + 
                 np.sum(np.abs( I[:,:-1] - I[:,1:] )) )

    def groups(self, I, mask):
        grp=[]
        m, n = I.shape 
        x, y = np.abs(mask).shape
        for i in range(m-x):
            for j in range(n-y):
                grp.append(I[i:(i+x), j:(j+y)])
        return grp

    def difference(self, I, mask):
        print('starting this function')
        cmask = - mask
        cmask[(mask > 0)] = 0
        L = []
        for g in self.groups(I, mask):
            flip = (g + cmask) ^ np.abs(mask) - cmask
            L.append(np.sign(self.smoothness(flip) - self.smoothness(g)))
        N = len(L)
        R = float(L.count(1))/N
        S = float(L.count(-1))/N
        print('ending this function_')
        return R-S

    def detect(self, input_file, output_file):
        I3d = imageio.imread(input_file)
        width, height, channels = I3d.shape
        z_val= 0.0
        for channel in range(channels):   
            print('channel iter ' + str(channel))
            I = I3d[:,:,channel]
            I = I.astype(int)
            mask = np.array( [[1,0],[0,1]] )
            d0 = self.difference(I, mask)
            d1 = self.difference(I^1, mask)

            mask = -mask
            n_d0 = self.difference(I, mask)
            n_d1 = self.difference(I^1, mask)

            p0, p1 = self.solve(2*(d1+d0), (n_d0-n_d1-d1-3*d0), (d0-n_d0)) 
            if np.abs(p0) < np.abs(p1): 
                z = p0
            else: 
                z = p1

            z_val += z / (z-0.5)

        z_val /= (channels + 0.0)
        #z_val is max of the 3 channels...

        fs.write_to_text_file(output_file, [z_val], override=True)

if __name__ == "__main__":
    args = sys.argv[1:]

    assert(len(args) == 2)
    input_file = args[0]
    output_file = args[1]

    runner = Runner()
    print('detecting')
    runner.detect(input_file, output_file)
    print('finishied')
