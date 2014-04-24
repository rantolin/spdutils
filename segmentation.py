#!/usr/bin/python2.7
# encoding: utf-8
'''
segmentation -- Segmentates a raster image based in LiDAR height metrics

@author:     Roberto Antolín

@copyright:  2014 Roberto Antolín. All rights reserved.

@license:    license

@contact:    roberto dot antolin at forestry dot gsi dot gov dot uk
@deffield    updated: Updated
'''

import sys, os
from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter

# Import rsgislib modules
from rsgislib.segmentation import segutils
import rsgislib.segmentation
import rsgislib.rastergis



__all__ = []
__version__ = 0.1
__date__ = '2014-04-23'
__updated__ = '2014-04-24'

DEBUG = 0
TESTRUN = 0
PROFILE = 0

class CLIError(Exception):
    '''Generic exception to raise and log different fatal errors.'''
    def __init__(self, msg):
        super(CLIError).__init__(type(self))
        self.msg = "E: %s" % msg

    def __str__(self):
        return self.msg

    def __unicode__(self):
        return self.msg


def main(argv=None):    # IGNORE:C0111
    '''Command line options.'''


    if argv is None:
        argv = sys.argv
    else:
        sys.argv.extend(argv)

    program_name = os.path.basename(sys.argv[0])
    program_version = "v%s" % __version__
    program_build_date = str(__updated__)
    program_version_message = '%%(prog)s %s (%s)' % (program_version, program_build_date)
    program_shortdesc = __import__('__main__').__doc__.split("\n")[1]
    program_license = '''%s

  Created by rantolin on %s.
  Copyright 2014 NRS. All rights reserved.

  Licensed under the Apache License 2.0
  http://www.apache.org/licenses/LICENSE-2.0

  Distributed on an "AS IS" basis without warranties
  or conditions of any kind, either express or implied.

USAGE

Segmentates a raster image based in LiDAR height metrics
''' % (program_shortdesc, str(__date__))

    try:
        # Setup argument parser

        parser = ArgumentParser(description=program_license, formatter_class=RawDescriptionHelpFormatter)
        parser.add_argument("input", help="The input image for the segmentation", metavar='file')
        parser.add_argument("-o", "--output", help="The output clump means image (for visualsation)", metavar="file", required=True)
        parser.add_argument("-t", "--thermal", help="Thermal image to populate the Segments with Stats", metavar="file")
        parser.add_argument("-n", "--numclusters", help="The number of clusters (k) in the KMeans [default: %(default)s]", metavar='int', default=8, type=int)
        parser.add_argument("-m", "--min_size", help="The minimum object size in pixels. [default: %(default)s]", metavar='int', default=50, type=int)
        parser.add_argument("-d", "--distance", help="The distance threshold to prevent merging. This has been set to an arbitrarily large number to disable this function [default: %(default)s]", metavar='float', default=1000000, type=float)
        parser.add_argument("-s", "--sampling", help="The sampling of the input image for KMeans (every 10th pixel). [default: %(default)s]", metavar='float', default=10, type=float)
        parser.add_argument("-I", "--iterations", help="Max. number of iterations for the KMeans. [default: %(default)s]", metavar='int', default=200, type=int)

        parser.add_argument("-V", "--version", action="version", version=program_version_message)

        # Process arguments
        args = parser.parse_args()

        inputImage = args.input
        # segmentClumps = args.clumps
        outputMeanSegments = args.output
        numClusters = args.numclusters
        thermalInImage = args.thermal
        minObjectSize = args.min_size
        distThres = args.distance
        sampling = args.sampling
        kmMaxIter = args.iterations

        # Name of auxiliar files
        baseOutput = os.path.basename(outputMeanSegments).split('.')[0]
        segmentClumps = baseOutput + '_segs.kea'
        inputSegmentations = [segmentClumps] #, 'Aberfoyle_SubCompartments.kea']
        segmentClumpsWithSubCompartments = baseOutput + '_segs_sc.kea'
        segmentClumpsWithSubCompartmentsRMSmallSegs = baseOutput + '_segs_sc_rmsmall.kea'
        segmentClumpsWithSubCompartmentsFinal = baseOutput + '_segs_final.kea'

        tmpPath = "./tmp/"

        ##################### Perform Segmentation #####################

        # RSGISLib function call to execute the segmentation
        # Utility function to call the segmentation algorithm of Shepherd et al. (2014).
        # Shepherd, J., Bunting, P., Dymond, J., 2013. Operational large-scale segmentation 
        # of imagery based on iterative elimination. Journal of Applied Remote Sensing. Submitted.
        segutils.runShepherdSegmentation(inputImage, segmentClumps, 
                                         outputMeanImg=outputMeanSegments,
                                         tmpath=tmpPath,
                                         gdalFormat="KEA",
                                         noStats=False,
                                         noStretch=False,
                                         noDelete=False,
                                         numClusters=numClusters,
                                         minPxls=minObjectSize,
                                         distThres=distThres, 
                                         bands=None, 
                                         sampling=sampling, 
                                         kmMaxIter=kmMaxIter)
        ################################################################


        ##################### Merge Segmentations #####################
        # Union of Clumps
        rsgislib.segmentation.UnionOfClumps(segmentClumpsWithSubCompartments, "KEA", inputSegmentations, 0)     # Output

        # Populates statics for thematic images
        rsgislib.rastergis.populateStats(segmentClumpsWithSubCompartments, True, True)                          # Input

        # eliminate clumps smaller than a given size from the scene
        rsgislib.segmentation.RMSmallClumpsStepwise(inputImage, segmentClumpsWithSubCompartments, segmentClumpsWithSubCompartmentsRMSmallSegs, "KEA", False, "", False, False, 5, 1000000)
        rsgislib.segmentation.relabelClumps(segmentClumpsWithSubCompartmentsRMSmallSegs, segmentClumpsWithSubCompartmentsFinal, "KEA", False)
        rsgislib.rastergis.populateStats(segmentClumpsWithSubCompartmentsFinal, True, True)
        ################################################################

        ############# Populate the Segments with Stats #################
        
        # TODO: Change bandStats to fit number of bands of input


        bandStats = []

        bandStats.append(rsgislib.rastergis.BandAttStats(band=1, meanField='GapFractionMean', stdDevField='GapFractionStdDev'))
        bandStats.append(rsgislib.rastergis.BandAttStats(band=2, meanField='CCPercentMean', stdDevField='CCPercentStdDev'))
        bandStats.append(rsgislib.rastergis.BandAttStats(band=3, meanField='HSCOIMean', stdDevField='HSCOIStdDev'))
        bandStats.append(rsgislib.rastergis.BandAttStats(band=4, meanField='95thPerHMean', stdDevField='95thPerHStdDev'))
        bandStats.append(rsgislib.rastergis.BandAttStats(band=5, meanField='50thPerHMean', stdDevField='50thPerHStdDev'))

        # Run the RSGISLib command with the input parameters.
        rsgislib.rastergis.populateRATWithStats(inputImage, segmentClumpsWithSubCompartmentsFinal, bandStats)

        ################################################################

        ############# Populate the Segments with Stats #################
        bandStats = []
        if thermalInImage:
            bandStats.append(rsgislib.rastergis.BandAttStats(band=1, meanField='ThermalMean', stdDevField='ThermalStdDev', minField='ThermalMin', maxField='ThermalMax'))
            # Run the RSGISLib command with the input parameters.
            rsgislib.rastergis.populateRATWithStats(thermalInImage, segmentClumpsWithSubCompartmentsFinal, bandStats)
        ################################################################

        return 0

    except KeyboardInterrupt:
        ### handle keyboard interrupt ###
        return 0
    except Exception, e:
        if DEBUG or TESTRUN:
            raise(e)
        indent = len(program_name) * " "
        sys.stderr.write(program_name + ": " + repr(e) + "\n")
        sys.stderr.write(indent + "  for help use --help")
        return 2

if __name__ == "__main__":
    if DEBUG:
        sys.argv.append("-h")
        sys.argv.append("-v")
        sys.argv.append("-r")
    if TESTRUN:
        import doctest
        doctest.testmod()
    if PROFILE:
        import cProfile
        import pstats
        profile_filename = 'argparse_module_profile.txt'
        cProfile.run('main()', profile_filename)
        statsfile = open("profile_stats.txt", "wb")
        p = pstats.Stats(profile_filename, stream=statsfile)
        stats = p.strip_dirs().sort_stats('cumulative')
        stats.print_stats()
        statsfile.close()
        sys.exit(0)
    sys.exit(main())

