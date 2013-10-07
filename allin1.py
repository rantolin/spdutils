#!/usr/bin/python2.7
# encoding: utf-8
'''
ThL_allinone -- ThermoLiDAR whole workflow

ThL_allinone is a description

It defines classes_and_methods

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
        parser.add_argument("-b", "--binsize", help="Bin size for SPD file index [Default: 1]", default=1, type=float)
        parser.add_argument("-x", "--xml", help="XML file defining metrics")
        parser.add_argument("-L", "--las", action="store_true", help="input file is a LAS file")
        parser.add_argument(dest="infile", help="Input file [default: %(default)s]", metavar="in", nargs='+')
        parser.add_argument(dest="oufile", help="Base name for output files [default: %(default)s]", metavar="out")
        #parser.add_argument(dest="temp", help="path to temporal folder [default: %(default)s]", default="/tmp", metavar="path")
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
        inFile = args.infile
        inXML = args.xml
        outFiles = args.outfile
        
        # if verbose > 0:
        #     print("Verbose mode on")
        #     if recurse:
        #         print("Recursive mode on")
        #     else:
        #         print("Recursive mode off")
        
        # for inpath in paths:
        #     ### do something with inpath ###
        #     print(inpath)

        outDSM = 'dsm.img'
        inSPD = 'spdfile.spd'
        
        if las:
            inLAS = inFile
            outSPD = outFiles + ".spd"
            commandline = 'spdtranslate --if LAS --of SPD -o %s -i %s -x LAST_RETURN -b {}' % (inLAS, outSPD, binsize)

        # Create DSM 
        inSPD = outSPD
        outDSM = outFiles + "_DSM.img"
        commandline = 'spdinterp -r 100 -c 100 --dsm --height -f ENVI  -b 1 %s %s' % (inSPD, outDSM)
        proc = subprocess.Popen(commandline, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=False)
        proc.wait()
        if verbose > 0:
            printVerbose(proc)
        
        # Classify
        inPmfGrd = outSPD
        outPmfGrd = outFiles + "_g.spd"
        commandline = 'spdpmfgrd %s %s' %(inPmfGrd, outPmfGrd)
        proc = subprocess.Popen(commandline, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=False)
        proc.wait()
        if verbose > 0:
            printVerbose(proc)

        # Create DTM 
        inDTM = outPmfGrd
        outDTM = outFiles + "_DTM.img"
        commandline = 'spdinterp -r 100 -c 100 --dtm --topo -f ENVI -b 1 %s %s' % (inDTM, outDTM)
        proc = subprocess.Popen(commandline, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=False)
        proc.wait()
        if verbose > 0:
            printVerbose(proc)

        # Define Height
        inDefHeight = outPmfGrd
        outDefHeight = outFiles + "_h.spd"
        commandline = 'spddefheight --interp -r 100 -c 100 --overlap 10 -i %s %s' % (inDefHeight, outDefHeight)
        proc = subprocess.Popen(commandline, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=False)
        proc.wait()
        if verbose > 0:
            printVerbose(proc)
        
        # Create CHM 
        inCHM = outDefHeight
        outCHM = outFiles + "_CHM.img"
        commandline = 'spdinterp -r 100 -c 100 --chm --height -f ENVI -b 1 %s %s' % (inCHM, outCHM)
        proc = subprocess.Popen(commandline, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=False)
        proc.wait()
        if verbose > 0:
            printVerbose(proc)

        # Derive Metrics
        if inXML:
            inMetrics = outDefHeight
            outMetrics = outFiles + "_metrics.img"
            commandline = 'spdmetrics -i -f HFA -r 100 -c 100 %s %s %s' %(inXML, inMetrics, outMetrics)
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