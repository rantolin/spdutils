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
import subprocess
import xml.etree.ElementTree as ET

from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter

# Import rsgislib modules
from rsgislib.segmentation import segutils
import rsgislib.segmentation
import rsgislib.rastergis



__all__ = []
__version__ = 0.1
__date__ = '2014-04-23'
__updated__ = '2014-04-23'

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
        parser.add_argument("-i", "--input", help="The input image for the segmentation", metavar="raster", required=True)
        parser.add_argument("-c", "--clumps", help="The output segments (clumps) image", metavar="raster", required=True)
        parser.add_argument("-o", "--output", help="The output clump means image (for visualsation)", metavar="raster", required=True)
        parser.add_argument("-n", "--numclusters", help="The number of clusters (k) in the KMeans [default: %(default)s]", default=8)
        parser.add_argument("-m", "--min_size", help="The minimum object size in pixels. [default: %(default)s]", default=50)
        parser.add_argument("-d", "--distance", help="The distance threshold to prevent merging. This has been set to an arbitrarily large number to disable this function [default: %(default)s]", default=1000000)
        parser.add_argument("-s", "--sampling", help="The sampling of the input image for KMeans (every 10th pixel). [default: %(default)s]", default=10)
        parser.add_argument("-I", "--iterations", help="Max. number of iterations for the KMeans.. [default: %(default)s]", default=200)

        parser.add_argument("-V", "--version", action="version", version=program_version_message)

        # Process arguments
        args = parser.parse_args()

        inputImage = args.input
        segmentClumps = args.clumps
        outputMeanSegments = args.output
        numClusters = args.numClusters
        minObjectSize = args.min_size
        distThres = args.distance
        sampling = args.sampling
        kmMaxIter = args.iterations

        ##################### Perform Segmentation #####################
        # The input image for the segmentation
        inputImage = "500m_row13col16_10m_metrics.kea"
        # The output segments (clumps) image
        segmentClumps = "500m_row13col16_segs.kea"
        # The output clump means image (for visualsation) 
        outputMeanSegments = "500m_row13col16_meansegs.kea"
        # A temporary path for layers generated during the
        # segmentation process. The directory will be created
        # and deleted during processing.
        tmpPath = "./tmp/"
        # The number of clusters (k) in the KMeans.
        numClusters = 8
        # The minimum object size in pixels.
        minObjectSize = 50
        # The distance threshold to prevent merging.
        # this has been set to an arbitrarily large 
        # number to disable this function. 
        distThres = 1000000
        # The sampling of the input image for KMeans (every 10th pixel)
        sampling = 10
        # Max. number of iterations for the KMeans.
        kmMaxIter = 200

        # RSGISLib function call to execute the segmentation
        segutils.runShepherdSegmentation(inputImage, segmentClumps, outputMeanSegments, 
                                         tmpPath, "KEA", False, False, False, numClusters, 
                                         minObjectSize, distThres, None, sampling, kmMaxIter)
        ################################################################


        ##################### Merge Segmentations #####################
        # inputSegmentations = [segmentClumps, 'Aberfoyle_SubCompartments.kea']
        # segmentClumpsWithSubCompartments = "500m_row13col16_segs_sc.kea"
        # segmentClumpsWithSubCompartmentsRMSmallSegs = "500m_row13col16_segs_sc_rmsmall.kea"
        segmentClumpsWithSubCompartmentsFinal = "500m_row13col16_segs_final.kea"

        # rsgislib.segmentation.UnionOfClumps(segmentClumpsWithSubCompartments, "KEA", inputSegmentations, 0)
        # rsgislib.rastergis.populateStats(segmentClumpsWithSubCompartments, True, True)
        # rsgislib.segmentation.RMSmallClumpsStepwise(inputImage, segmentClumpsWithSubCompartments, segmentClumpsWithSubCompartmentsRMSmallSegs, "KEA", False, "", False, False, 5, 1000000)
        # rsgislib.segmentation.relabelClumps(segmentClumpsWithSubCompartmentsRMSmallSegs, segmentClumpsWithSubCompartmentsFinal, "KEA", False)
        # rsgislib.rastergis.populateStats(segmentClumpsWithSubCompartmentsFinal, True, True)
        ################################################################


        ############# Populate the Segments with Stats #################
        bandStats = []

        bandStats.append(rsgislib.rastergis.BandAttStats(band=1, meanField='GapFractionMean', stdDevField='GapFractionStdDev'))
        bandStats.append(rsgislib.rastergis.BandAttStats(band=2, meanField='CCPercentMean', stdDevField='CCPercentStdDev'))
        bandStats.append(rsgislib.rastergis.BandAttStats(band=3, meanField='HSCOIMean', stdDevField='HSCOIStdDev'))
        bandStats.append(rsgislib.rastergis.BandAttStats(band=4, meanField='95thPerHMean', stdDevField='95thPerHStdDev'))
        bandStats.append(rsgislib.rastergis.BandAttStats(band=5, meanField='50thPerHMean', stdDevField='50thPerHStdDev'))

        # Run the RSGISLib command with the input parameters.
        # rsgislib.rastergis.populateRATWithStats(inputImage, segmentClumpsWithSubCompartmentsFinal, bandStats)

        ################################################################

        ############# Populate the Segments with Stats #################
        thermalInImage = 'SouthOrtho_10m_kea.kea'

        bandStats = []
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

