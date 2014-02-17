#!/usr/bin/python2.7
# encoding: utf-8
'''
metrics2xml -- Generates a xml file containing SPD metrics

@author:     Roberto Antolín

@copyright:  2014 Roberto Antolín. All rights reserved.

@license:    license

@contact:    roberto dot antolin at forestry dot gsi dot gov dot uk
@deffield    updated: Updated
'''

import sys, os
from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter

__all__ = []
__version__ = 0.1
__date__ = '2014-02-06'
__updated__ = '2014-02-06'
__author__ = 'Roberto Antolin'


DEBUG = 0
TESTRUN = 0
PROFILE = 0

# Height percentiles
pH99 = {'metric':"percentileheight", 'field':"99thPerH", 'percentile':"99", 'return':"All", 'class':"NotGrd", 'lowthreshold':"0.1"}
pH95 = {'metric':"percentileheight", 'field':"95thPerH", 'percentile':"95", 'return':"All", 'class':"NotGrd", 'lowthreshold':"0.1"}
pH90 = {'metric':"percentileheight", 'field':"90thPerH", 'percentile':"90", 'return':"All", 'class':"NotGrd", 'lowthreshold':"0.1"}
pH80 = {'metric':"percentileheight", 'field':"80thPerH", 'percentile':"80", 'return':"All", 'class':"NotGrd", 'lowthreshold':"0.1"}
pH70 = {'metric':"percentileheight", 'field':"70thPerH", 'percentile':"70", 'return':"All", 'class':"NotGrd", 'lowthreshold':"0.1"}
pH60 = {'metric':"percentileheight", 'field':"60thPerH", 'percentile':"60", 'return':"All", 'class':"NotGrd", 'lowthreshold':"0.1"}
pH50 = {'metric':"percentileheight", 'field':"50thPerH", 'percentile':"50", 'return':"All", 'class':"NotGrd", 'lowthreshold':"0.1"}
pH40 = {'metric':"percentileheight", 'field':"40thPerH", 'percentile':"40", 'return':"All", 'class':"NotGrd", 'lowthreshold':"0.1"}
pH30 = {'metric':"percentileheight", 'field':"30thPerH", 'percentile':"30", 'return':"All", 'class':"NotGrd", 'lowthreshold':"0.1"}
pH20 = {'metric':"percentileheight", 'field':"20thPerH", 'percentile':"20", 'return':"All", 'class':"NotGrd", 'lowthreshold':"0.1"}
pH10 = {'metric':"hscoi", 'field':"hscoi", 'percentile':"10", 'return':"First", 'class':"NotGrd", 'lowthreshold':"0.1"}
hcoi = {'metric':"percentileheight", 'field':"10thPerH", 'return':"All", 'class':"NotGrd", 'lowthreshold':"2", 'vres':"0.5"}

# General statistics
numReturnsAll = {'metric':"numreturnsheight", 'field':"numReturnsAll", 'return':"All", 'class':"All", 'lowthreshold':"2", 'vres':"0.5"}
numReturnsNotGround = {'metric':"numreturnsheight", 'field':"numReturnsNotGround", 'return':"All", 'class':"NotGrd"}
numReturnsGround = {'metric':"numreturnsheight", 'field':"numReturnsGround", 'return':"All", 'class':"Grd"}
numReturns1 = {'metric':"numreturnsheight", 'field':"Return_1", 'return':"1", 'class':"All"}
numReturns2 = {'metric':"numreturnsheight", 'field':"Return_2", 'return':"2", 'class':"All"}
numReturns3 = {'metric':"numreturnsheight", 'field':"Return_3", 'return':"3", 'class':"All"}
numReturns4 = {'metric':"numreturnsheight", 'field':"Return_4", 'return':"4", 'class':"All"}
ccpercent = {'metric':"canopycoverpercent", 'field':"CCPercent", 'return':"First", 'class':"NotGrd", 'lowthreshold':"2", 'radius':"0.25", 'resolution':"0.1"}
groundCover= {'metric':"canopycover", 'field':"groundCover", 'return':"All", 'class':"Grd", 'radius':"1.4", 'lowthreshold':"0.0"}
canopyCover= {'metric':"canopycover", 'field':"canopyCover", 'return':"All", 'class':"NotGrd", 'radius':"1.4", 'lowthreshold':"0.0"}

# Height metrics
sumHeight = {'metric':"sumheight", 'field':"sumH", 'return':"All", 'class':"NotGrd", 'lowthreshold':"0.0"}
stddevHeight = {'metric':"stddevheight", 'field':"std", 'return':"All", 'class':"NotGrd", 'lowthreshold':"0.0"}
varianceHeight= {'metric':"varianceheight", 'field':"var", 'return':"All", 'class':"NotGrd", 'lowthreshold':"0.0"}
minHeight = {'metric':"minheight", 'field':"minH", 'return':"All", 'class':"NotGrd", 'lowthreshold':"0.0"}
maxHeight = {'metric':"maxheight", 'field':"maxH", 'return':"All", 'class':"NotGrd", 'lowthreshold':"0.0"}
meanHeight = {'metric':"meanheight", 'field':"meanH", 'return':"All", 'class':"NotGrd", 'lowthreshold':"0.0"}
medianHeight = {'metric':"medianheight", 'field':"medianH", 'return':"All", 'class':"NotGrd", 'lowthreshold':"0.0"}
modeHeight = {'metric':"modeheight", 'field':"modeH", 'return':"All", 'class':"NotGrd", 'lowthreshold':"0.0"}
dominantHeight = {'metric':"dominantheight", 'field':"dominantH", 'return':"All", 'class':"NotGrd", 'lowthreshold':"0.0"}
canopycoverHeight = {'metric':"canopycoverheight", 'field':"canopycoverH", 'return':"All", 'class':"NotGrd", 'lowthreshold':"0.0"}
kurtosisHeight = {'metric':"kurtosisheight", 'field':"kurtosis", 'return':"All", 'class':"NotGrd", 'lowthreshold':"0.0"}
skewnessHeight = {'metric':"skewnessheight", 'field':"skewness", 'return':"All", 'class':"NotGrd", 'lowthreshold':"0.0"}

metric_choices = ['ALL', 'pH99', 'pH95', 'pH90', 'pH80', 'pH70', 'pH60', 'pH50', 'pH40', 'pH30', 'pH20', 'pH10',\
    'numReturnsAll', 'numReturnsNotGround', 'numReturnsGround', 'numReturns1', 'numReturns2',\
    'numReturns3', 'numReturns4', 'ccpercent', 'groundCover', 'canopyCover', 'sumHeight',\
    'stddevHeight', 'varianceHeight', 'minHeight', 'maxHeight', 'meanHeight', 'medianHeight',\
    'modeHeight', 'dominantHeight', 'canopycoverHeight', 'kurtosisHeight', 'skewnessHeight']


class CLIError(Exception):
    '''Generic exception to raise and log different fatal errors.'''
    def __init__(self, msg):
        super(CLIError).__init__(type(self))
        self.msg = "E: %s" % msg

    def __str__(self):
        return self.msg

    def __unicode__(self):
        return self.msg


def generateXML(metrics):
    """ (List metrics) -> string"""
    xml = """<?xml version="1.0" encoding="UTF-8" ?>
<!--
    Description:
        XML File for execution within SPDLib
        This file contains a template for the
        metrics XML interface.
        
    Created by {1} on {0}.
    Copyright (c) 2011 Pete Bunting. All rights reserved.
--> 

<spdlib:metrics xmlns:spdlib="http://www.spdlib.org/xml/">\n""".format(str(__updated__), str(__author__))
    for metric in metrics:
        xml += getXmlString(metric)
    xml += "</spdlib:metrics>"
    return xml


def getXmlString(metric):
    xmlString = '    <spdlib:metric' 
    for key in metric.keys():
        xmlString += ' {0}="{1}"'.format(key,metric[key])
    xmlString += ' />\n'
    return xmlString


def addmetric(metricsList, metric):
    if metric == 'pH99': metricsList.append(pH99); return
    if metric == 'pH95': metricsList.append(pH95); return
    if metric == 'pH90': metricsList.append(pH90); return
    if metric == 'pH80': metricsList.append(pH80); return
    if metric == 'pH70': metricsList.append(pH70); return
    if metric == 'pH60': metricsList.append(pH60); return
    if metric == 'pH50': metricsList.append(pH50); return
    if metric == 'pH40': metricsList.append(pH40); return
    if metric == 'pH30': metricsList.append(pH30); return
    if metric == 'pH20': metricsList.append(pH20); return
    if metric == 'pH10': metricsList.append(pH10); return

    if metric == 'numReturnsAll': metricsList.append(numReturnsAll); return
    if metric == 'numReturnsNotGround': metricsList.append(numReturnsNotGround); return
    if metric == 'numReturnsGround': metricsList.append(numReturnsGround); return
    if metric == 'numReturns1': metricsList.append(numReturns1); return
    if metric == 'numReturns2': metricsList.append(numReturns2); return
    if metric == 'numReturns3': metricsList.append(numReturns3); return
    if metric == 'numReturns4': metricsList.append(numReturns4); return
    if metric == 'ccpercent': metricsList.append(ccpercent); return
    if metric == 'groundCover': metricsList.append(groundCover); return
    if metric == 'canopyCover': metricsList.append(canopyCover); return

    if metric == 'sumHeight': metricsList.append(sumHeight); return
    if metric == 'stddevHeight': metricsList.append(stddevHeight); return
    if metric == 'varianceHeight': metricsList.append(varianceHeight); return
    if metric == 'minHeight': metricsList.append(minHeight); return
    if metric == 'maxHeight': metricsList.append(maxHeight); return
    if metric == 'meanHeight': metricsList.append(meanHeight); return
    if metric == 'medianHeight': metricsList.append(medianHeight); return
    if metric == 'modeHeight': metricsList.append(modeHeight); return
    if metric == 'dominantHeight': metricsList.append(dominantHeight); return
    if metric == 'canopycoverHeight': metricsList.append(canopycoverHeight); return
    if metric == 'kurtosisHeight': metricsList.append(kurtosisHeight); return
    if metric == 'skewnessHeight': metricsList.append(skewnessHeight); return


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
  Copyright 2014 Forest Research. All rights reserved.

  Licensed under the Apache License 2.0
  http://www.apache.org/licenses/LICENSE-2.0

  Distributed on an "AS IS" basis without warranties
  or conditions of any kind, either express or implied.

USAGE
''' % (program_shortdesc, str(__date__))

    try:
        # Setup argument parser
        parser = ArgumentParser(description=program_license, formatter_class=RawDescriptionHelpFormatter)
        parser.add_argument('-m', '--metric', dest='metric', help='Metrics: %(choices)s', metavar='metric', choices=metric_choices, nargs='+', required=True)
        parser.add_argument('-o', '--output', dest='output', help='File of the xml output', metavar='OUTPUT') #, required=True)
        # parser.add_argument('-A', '--all', action="store_true", help="Compute all the metrics")
        parser.add_argument("-V", "--version", action="version", version=program_version_message)

        # Process arguments
        args = parser.parse_args()

        # inFiles = args.infile
        metrics = args.metric
        output = args.output
        # allm = args.all

        if 'ALL' in metrics:
            metricsList = [pH99, pH95, pH90, pH80, pH70, pH60, pH50, pH40, pH30, pH20, pH10,\
            numReturnsAll, numReturnsNotGround, numReturnsGround, numReturns1, numReturns2,\
            numReturns3, numReturns4, ccpercent, groundCover, canopyCover, sumHeight,\
            stddevHeight, varianceHeight, minHeight, maxHeight, meanHeight, medianHeight,\
            modeHeight, dominantHeight, canopycoverHeight, kurtosisHeight, skewnessHeight]
        else:
            metricsList = []
            for metric in metrics:
                addmetric(metricsList, metric)

        if output is None:
            print "{0}: Please, provide a output name".format(program_name.split('.')[0])
            print ""
            print parser.print_help()
            return 2
        
        fxml = open(os.path.abspath(output), 'w')
        fxml.write(generateXML(metricsList))
        fxml.close()
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
