import imageio
from cmath import sqrt
import stegtest.utils.filesystem as fs
import sys

##Code from https://github.com/daniellerch/aletheia/tree/master/aletheialib

class Runner(object):
    """docstring for Runner"""
    def detect(self, input_file, output_file): 
        I3d = imageio.imread(input_file)
        if len(I3d.shape) == 3:
            width, height, channels = I3d.shape
        else:
            width, height = I3d.shape
            channels = 1
        beta = 0.0
        for channel in range(channels):
            if channels == 1:
                I = I3d[:,:]
            else:
                I = I3d[:,:,channel]

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

            beta += min(bp.real, bm.real)

        beta /= (channels + 0.0)

        fs.write_to_text_file(output_file, [beta], override=True)

if __name__ == "__main__":
    args = sys.argv[1:]

    assert(len(args) == 2)
    input_file = args[0]
    output_file = args[1]

    runner = Runner()
    runner.detect(input_file, output_file)
