import time
import tifffile
import numpy as np
import os
import argparse

from Graph import networkx_graph_from_array as netGrArr
import Statistics.graph as graph
import Statistics.utils as utils


def processImage(imgFile, parameterDict):
    input_file = os.path.abspath(imgFile).replace('\\', '/')
    dir = os.path.dirname(input_file)
    file_name = os.path.basename(dir)

    if parameterDict.get("info_file") is True:
        finfo = dir + '/' + file_name + '_info.csv'
    else:
        finfo = None

    # Graph construction
    print("Graph construction")

    binImage = tifffile.imread(dir + "/Binary_" + file_name + '.tif')
    binImage = binImage / np.max(binImage)
    skeleton = tifffile.imread(dir + "/Skeleton_" + file_name + '.tif')
    skeleton = skeleton / np.max(skeleton)

    start = time.time()
    networkxGraph = netGrArr.get_networkx_graph_from_array(skeleton)
    graphTime = round(time.time() - start, 3)
    print("elapsed time: %0.3f seconds" % (time.time() - start))

    # Statistical Analysis
    print("Statistical Analysis")
    start = time.time()
    stats = graph.Graph(binImage, skeleton, networkxGraph, parameterDict.get("pixel_dimensions"),
                        pruningScale=parameterDict.get("pruning_scale"), lengthLimit=parameterDict.get("length_limit"),
                        infoFile=finfo)
    stats.setStats()
    print("elapsed time: %0.3f seconds" % (time.time() - start))

    # Export statistics to csv and save segmentation and skeleton mask as tif images
    print("Saving statistics as csv files")
    statsDir = dir + '/Statistics/'
    os.makedirs(os.path.dirname(statsDir), exist_ok=True)

    utils.saveFilamentDictAsCSV(stats.countBranchPointsDict, statsDir + file_name +
                                '_Filament_No._Segment_Branch_Points.csv', 'Filament No. Segment Branch Pts')
    utils.saveFilamentDictAsCSV(stats.countEndPointsDict, statsDir + file_name +
                                '_Filament_No._Segment_Terminal_Points.csv', 'Filament No. Segment Terminal Pts')
    utils.saveFilamentDictAsCSV(stats.sumLengthDict, statsDir + file_name + '_Filament_Length_(sum).csv',
                                'Filament Length (sum)', 'um')
    utils.saveSegmentDictAsCSV(stats.lengthDict, statsDir + file_name + '_Segment_Length.csv', 'Segment Length',
                               'um')
    utils.saveSegmentDictAsCSV(stats.straightnessDict, statsDir + file_name + '_Segment_Straightness.csv',
                               'Segment Straightness')
    utils.saveSegmentDictAsCSV(stats.degreeDict, statsDir + file_name + '_Segment_Branching_Angle.csv',
                               'Segment Branching Angle', '°')
    utils.saveSegmentDictAsCSV(stats.volumeDict, statsDir + file_name + '_Segment_Volume.csv',
                               'Segment Volume', 'um^3')
    utils.saveSegmentDictAsCSV(stats.diameterDict, statsDir + file_name + '_Segment_Diameter.csv',
                               'Segment Diameter', 'um')
    utils.saveSegmentDictAsCSV(stats.branchPointsDict, statsDir + file_name + '_BranchPt_No._Branches.csv',
                               'BranchPt No. Branches', category='Branch')
    print("elapsed time: %0.3f seconds" % (time.time() - start))


if __name__ == '__main__':
    programStart = time.time()

    parser = argparse.ArgumentParser(description='Computes graph analysis on skeleton image file of type .tif')
    parser.add_argument('-i', type=str, help='input skeleton tif image file to process')
    parser.add_argument('-pixel_dimensions', type=str, default="2.0,1.015625,1.015625",
                        help='Pixel dimensions in [z, y, x]')
    parser.add_argument('-info_file', type=bool, default=False, help='set to true to create info file')
    # Pruning and postprocessing parameters
    parser.add_argument('-pruning_scale', type=float, default=1.5,
                        help='Pruning scale for insignificant branch removal')
    parser.add_argument('-length_limit', type=float, default=3, help='Limit of vessel lengths')
    args = parser.parse_args()

    parameters = {
        "pixel_dimensions": [float(item) for item in args.pixel_dimensions.split(',')],
        "info_file": args.info_file,
        "pruning_scale": args.pruning_scale,
        "length_limit": args.length_limit
    }

    processImage(args.i, parameters)

    print("Graph extraction and statistical analysis completed in %0.3f seconds" % (time.time() - programStart))
