#!/usr/bin/python2.7
# encoding: utf-8
'''
allin1 -- ThermoLiDAR whole workflow

allin1 intends to be a script interface that computes in a single call, the most common LiDAR products from DTM to CHM,
including height metrics. It is based on the workflow chart that appears in Bunting et al. (2013).
allin1 performs a default analysis and lacks for many the capabilities that are included in the single spdtools. The main reason is to not overwhelm the 
user with options and parameters. Exceptions are made for single options as for the binsize and metrics (in coming version)

As point out in the spdlib tutorials (http://http://www.spdlib.org/), default values for --blockcols and --blockrows are both set 
to 100. Default interpolation is made by the Natural Neighbor method which masks outputs in order to avoid interpolation in empty zones.
Currently, the default raster output format is the ENVI format. Ground is classify by means of the progressive morphology algorithm: spdpmfgrd. 
Point heights from ground are obtained by performing an interpolation during the execution of spddefheight by the --interp option and an 
--overlap value equal to 10. 

@author:     rantolin
        
@copyright:  2013 Roberto Antolin. All rights reserved.
        
@license:    license

@contact:    roberto dot antolin at forestry dot gsi dot gov dot uk
@deffield    updated: Updated
'''

import sys
import os
import subprocess

from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter

__all__ = []
__version__ = 0.1
__date__ = '2013-10-07'
__updated__ = '2013-10-07'

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

def printVerbose(process):
        out, err = process.communicate()
        process.returncode
        print out


def main(argv=None): # IGNORE:C0111
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
  Copyright 2013 organization_name. All rights reserved.
  
  Licensed under the Apache License 2.0
  http://www.apache.org/licenses/LICENSE-2.0
  
  Distributed on an "AS IS" basis without warranties
  or conditions of any kind, either express or implied.

USAGE
''' % (program_shortdesc, str(__date__))

    try:
        # Setup argument parser
        parser = ArgumentParser(description=program_license, formatter_class=RawDescriptionHelpFormatter)
        parser.add_argument("-b", "--binsize", help="bin size for SPD file index [Default: 1]", default=1, type=float)
        parser.add_argument("-m", "--xml", help="metrix XML file")
        parser.add_argument(dest="infile", help="input file [default: %(default)s]", metavar="in", nargs='+')
        parser.add_argument("-o", "--output", help="path to output files [default: %(default)s]", metavar="Path")
        #parser.add_argument(dest="outpath", help="Path to output files [default: %(default)s]", metavar="out")
        #parser.add_argument(dest="temp", help="path to temporal folder [default: %(default)s]", default="/tmp", metavar="path")
        parser.add_argument("-L", "--las", action="store_true", help="input file is a LAS file")
        parser.add_argument("-v", "--verbose", dest="verbose", action="count", help="set verbosity level [default: %(default)s]")
        parser.add_argument('-V', '--version', action='version', version=program_version_message)
        #parser.add_argument("-r", "--recursive", dest="recurse", action="store_true", help="recurse into subfolders [default: %(default)s]")
        
        # Process arguments
        args = parser.parse_args()
        
        #paths = args.paths
        verbose = args.verbose
        #recurse = args.recurse
        las = args.las
        binsize = args.binsize
        inFiles = args.infile
        inXML = args.xml
        outPath = args.output
                
        for inFile in inFiles:
            inSPD = inFile
            inputName = os.path.basename(inSPD)
            baseName = inputName.split('.')[0]
            if os.path.isdir(outPath):
                outPathName = os.path.abspath(outPath) + '/' + baseName
            else:
                print "%s: %s is not a valid path" %(program_name.split('.')[0], outPath)
                print ""
                print parser.print_help()
                return 2
            print "Processing %s file..." %baseName 
            print outPathName

            # TODO: Change -c and -r values

            if las:
                inLAS = inSPD
                outSPD = baseName + ".spd"
                inSPD = outSPD
                commandline = 'spdtranslate --if LAS --of SPD -x LAST_RETURN -b %f -i %s -o %s' % (binsize, inLAS, outSPD)
                print commandline
                
            # Create DSM 
            outDSM = outPathName + "_DSM.img"
            commandline = 'spdinterp -r 100 -c 100 --dsm --height -f ENVI --in NATURAL_NEIGHBOR -b %f -i %s -o %s' % (binsize, inSPD, outDSM)
            print commandline
            proc = subprocess.Popen(commandline, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=False)
            proc.wait()
            if verbose > 0:
                printVerbose(proc)

            # Classify Ground
            inPmfGrd = inSPD
            outPmfGrd = outPathName + "_ground.spd"
            commandline = 'spdpmfgrd -i %s -o %s' %(inPmfGrd, outPmfGrd)
            print commandline
            proc = subprocess.Popen(commandline, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=False)
            proc.wait()
            if verbose > 0:
                printVerbose(proc)

            # Create DTM 
            inDTM = outPmfGrd
            outDTM = outPathName + "_DTM.img"
            commandline = 'spdinterp -r 100 -c 100 --dtm --topo -f ENVI --in NATURAL_NEIGHBOR -b %f -i %s -o %s' % (binsize, inDTM, outDTM)
            print commandline
            proc = subprocess.Popen(commandline, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=False)
            proc.wait()
            if verbose > 0:
                printVerbose(proc)

            # Define Height
            inDefHeight = outPmfGrd
            outDefHeight = outPathName + "_height.spd"
            commandline = 'spddefheight --interp -r 100 -c 100 --overlap 10 -i %s -o %s' % (inDefHeight, outDefHeight)
            print commandline
            proc = subprocess.Popen(commandline, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=False)
            proc.wait()
            if verbose > 0:
                printVerbose(proc)
            
            # Create CHM 
            inCHM = outDefHeight
            outCHM = outPathName + "_CHM.img"
            commandline = 'spdinterp -r 100 -c 100 --chm --height -f ENVI -b %f -i %s -o %s' % (binsize, inCHM, outCHM)
            print commandline
            proc = subprocess.Popen(commandline, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=False)
            proc.wait()
            if verbose > 0:
                printVerbose(proc)

            # Derive Metrics
            if inXML:
                inMetrics = outDefHeight
                outMetrics = outPathName + "_metrics.img"
                commandline = 'spdmetrics --image -f ENVI -r 100 -c 100 -m %s -i %s -o %s' %(inXML, inMetrics, outMetrics)
                print commandline
                proc = subprocess.Popen(commandline, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=False)
                if verbose > 0:
                    printVerbose(proc)

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