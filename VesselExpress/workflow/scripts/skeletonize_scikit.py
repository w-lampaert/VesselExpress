import time
import argparse
from skimage.morphology import skeletonize
import sys
import os

# import modules
package = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..', 'modules/'))
sys.path.append(package)

import utils


if __name__ == '__main__':
    programStart = time.time()

    parser = argparse.ArgumentParser(description='Computes scikit skeletonization on a binary image file of type .tif')
    parser.add_argument('-i', type=str, help='input tif image file to process')
    parser.add_argument('-pixel_dimensions', type=str, default="2.0,1.015625,1.015625",
                        help='Pixel dimensions in [z, y, x]')
    parser.add_argument('-prints', type=bool, default=False, help='set to True to print runtime')
    args = parser.parse_args()

    pixelDims = [float(item) for item in args.pixel_dimensions.split(',')]
    input_file = os.path.abspath(args.i).replace('\\', '/')
    output_dir = os.path.dirname(input_file)
    binArr = utils.read_img(args.i)

    skel = skeletonize(binArr, method='lee')

    utils.write_img(skel.astype('uint8'), output_dir + '/Skeleton_' + os.path.basename(output_dir) + '.'
                    + input_file.split('.')[1])

    if args.prints:
        print("Skeletonization completed in %0.3f seconds" % (time.time() - programStart))
