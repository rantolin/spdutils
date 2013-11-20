#!/usr/bin/python2.7
# encoding: utf-8
'''
allin1 -- ThermoLiDAR whole workflow

allin1 intends to be a script interface that computes in a single call, the most common LiDAR products from DTM to
CHM, including height metrics. It is based on the workflow chart that appears in Bunting et al. (2013).
allin1 performs a default analysis and lacks for many the capabilities that are included in the single spdtools. The
main reason is to not overwhelm the user with options and parameters. Exceptions are made for single options as for
the binsize and metrics (in coming version)

As point out in the spdlib tutorials (http://http://www.spdlib.org/), default values for --blockcols and --blockrows
are both set to 50. Default interpolation is made by the Natural Neighbor method which masks outputs in order to
avoid interpolation in empty zones. Currently, the default raster output format is the GTiff format. Ground is classify
by means of the progressive morphology algorithm: spdpmfgrd. Point heights from ground are obtained by performing an
interpolation during the execution of spddefheight by the --interp option and an --overlap value equal to 10.

Multiple inputs are supported.
Output parameter ask for a path into which output files will be recorded. Only valid folder paths are permitted.
Output file names are compossed by a basename -base on the input name- plus a suffix which describes it.
Binsize is the resolution in which raster output will be created.
XML expects the file containing metrics. So far, only a metric at a time is supported (spdmetrics issues).
LAS options treats input files as LAS format LiDAR files.
Different


@author:     Roberto Antolín

@copyright:  2013 Roberto Antolín. All rights reserved.

@license:    license

@contact:    roberto dot antolin at forestry dot gsi dot gov dot uk
@deffield    updated: Updated
'''

import sys, os
import subprocess

from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter

__all__ = []
__version__ = 0.1
__date__ = '2013-10-07'
__updated__ = '2013-10-11'

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


def runCommand(verb, cmd):
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=False)
    if verb == 2:
        for line in iter(proc.stdout.readline, ''):
            line = line.replace('\r', '').replace('\n', '')
            print line
            sys.stdout.flush()
    elif verb == 1:
        print cmd
        proc.wait()
    else:
        proc.wait()


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
        parser.add_argument(dest="infile", help="input file", metavar="in", nargs='+')
        parser.add_argument("-o", "--output", dest='output', help="path to output files [Default: %(default)s]", metavar="Path")
        parser.add_argument("-t", "--temppath", dest="temppath", help="path to temporal folder [Default: %(default)s]", metavar="TEMPPATH")
        parser.add_argument("-m", "--xml", help="metrix XML file")
        parser.add_argument("-b", "--binsize", help="Bin size for SPD file index [Default: %(default)d]", default=10, type=int)
        parser.add_argument("-r", "--resolution", help="Pixel size for output image [Default: %(default)3.1f]. \
            Note 0 will use the native SPD file bin size", default=1.0, type=float)
        parser.add_argument("-u", "--upd", action="store_true", help="input file is a UPD file (unsorted SPD)")
        parser.add_argument("-L", "--las", action="store_true", help="input file is a LAS file")
        parser.add_argument("-v", "--verbose", dest="verbose", action="count", help="set verbosity level [Default: %(default)s]", default=0)
        parser.add_argument("-V", "--version", action="version", version=program_version_message)
        
        # Process arguments
        args = parser.parse_args()

        inFiles = args.infile
        output = args.output
        temp = args.temppath
        inXML = args.xml
        binsize = args.binsize
        res = args.resolution
        upd = args.upd
        las = args.las
        verbose = args.verbose

        if output is None:
            print "{0}: Please, supply a valid path".format(program_name.split('.')[0])
            print ""
            print parser.print_help()
            return 2
        if not os.path.exists(output): os.mkdir(output)

        outPath = os.path.relpath(output)
        dtmPath = os.path.join(outPath,"DTM")
        dsmPath = os.path.join(outPath,"DSM")
        chmPath = os.path.join(outPath,"CHM")
        if not os.path.exists(dtmPath): os.mkdir(dtmPath)
        if not os.path.exists(dsmPath): os.mkdir(dsmPath)
        if not os.path.exists(chmPath): os.mkdir(chmPath)

        for inFile in inFiles:
            inputPath, inputName = os.path.split(os.path.realpath(inFile))
            baseName = inputName.split('.')[0]
            inSPD = inFile

            outPathName = os.path.join(outPath, baseName) + "_{0}m".format(binsize)
            print "Processing file {0} ...".format(baseName)

            if las:
                inLAS = inSPD
                outSPD = outPathName + ".spd"
                inSPD = outSPD
                commandline = 'spdtranslate --if LAS --of SPD -x LAST_RETURN -b {0} -i {1} -o {2}'.format(binsize, inLAS, outSPD)
                if temp is not None: commandline += '--temppath {0}'.format(temp)
                runCommand(verbose, commandline)

            elif upd:
                inUPD = inSPD
                outSPD = outPathName + ".spd"
                inSPD = outSPD
                commandline = 'spdtranslate --if SPD --of SPD -x LAST_RETURN -b {0} -i {1} -o {2}'.format(binsize, inUPD, outSPD)
                if temp is not None: commandline += ' --temppath {0}'.format(temp)
                runCommand(verbose, commandline)

            # Create DSM
            outDSM = os.path.join(dsmPath, baseName) + "_DSM.tif"
            commandline = 'spdinterp -r 50 -c 50 --dsm --topo -f GTiff --in NATURAL_NEIGHBOR -b {0} -i {1} -o {2}'.format(res, inSPD, outDSM)
            runCommand(verbose, commandline)

            # Classify Ground
            inGrd = inSPD
            outGrd = outPathName + "_pmfgrd.spd"
            commandline = 'spdpmfgrd -i {0} -o {1} --grd 1 -b 1'.format(inGrd, outGrd)
            runCommand(verbose, commandline)

            inGrd = outGrd
            outGrd = outPathName + "_mccgrd.spd"
            commandline = 'spdmccgrd -i {0} -o {1} --class 3 -b 1'.format(inGrd, outGrd)
            runCommand(verbose, commandline)

            # Create DTM
            inDTM = outGrd
            outDTM = os.path.join(dtmPath, baseName) + "_DTM.tif"
            commandline = 'spdinterp -r 50 -c 50 --dtm --topo -f GTiff --in NATURAL_NEIGHBOR -b {0} -i {1} -o {2}'.format(res, inDTM, outDTM)
            runCommand(verbose, commandline)

            # Define Height
            inDefHeight = outGrd
            outDefHeight = outPathName + "_height.spd"
            commandline = 'spddefheight --interp -r 50 -c 50 --overlap 10 -i {0} -o {1}'.format(inDefHeight, outDefHeight)
            runCommand(verbose, commandline)

            # Create CHM
            inCHM = outDefHeight
            outCHM = os.path.join(chmPath, baseName) + "_CHM.tif"
            commandline = 'spdinterp -r 50 -c 50 --dsm --height -f GTiff -b {0} -i {1} -o {2}'.format(res, inCHM, outCHM)
            runCommand(verbose, commandline)

            # Derive Metrics
            if inXML:
                inMetrics = outDefHeight
                outMetrics = outPathName + "_metrics.tif"
                commandline = 'spdmetrics --image -f GTiff -r 50 -c 50 -m {0} -i {1} -o {2}'.format(inXML, inMetrics, outMetrics)
                runCommand(verbose, commandline)

            os.remove(inGrd)        # pmfgrd.spd
            os.remove(outGrd)       # mccgrd.spd
            # os.remove(outSPD)       # basename

            print "[DONE]"

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
