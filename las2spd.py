#!/usr/bin/python2.7
# encoding: utf-8
'''
las2spd -- Translate LAS files into SPD

@author:     Roberto Antolín

@copyright:  2014 Roberto Antolín. All rights reserved.

@license:    license

@contact:    roberto dot antolin at forestry dot gsi dot gov dot uk
@deffield    updated: Updated
'''

import sys, os, shutil
import subprocess
import time

from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter

__all__ = []
__version__ = 0.1
__date__ = '2014-03-08'
__updated__ = '2014-03-08'

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
    # devnull = open(os.devnull, 'wb')
    # stdout = devnull
    # stderr = devnull
    # if verb >= 1:
    #     stdout = subprocess.PIPE
    #     if verb == 2:
    #         stderr = subprocess.STDOUT

    # proc = subprocess.Popen(cmd, shell=True, stdout=stdout, stderr=stderr, universal_newlines=False)
    # if verb >= 1:
    #     for line in iter(proc.stdout.readline, ''):
    #         line = line.replace('\r', '').replace('\n', '')
    #         print line
    #         sys.stdout.flush()
    # else:
    #     proc.communicate()      # Avoid to deadlock using proc.wait()
    #     proc.wait()

    if verb >= 1:
        stderr = subprocess.STDOUT
        if verb == 1:
            stderr = open(os.devnull, 'wb')

        t0 = time.time()
        proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=stderr, universal_newlines=False)
        for line in iter(proc.stdout.readline, ''):
            line = line.replace('\r', '').replace('\n', '')
            print line
            sys.stdout.flush()

        t = time.time() - t0

    else:
        t0 = time.time()
        proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=False)
        proc.communicate()      # Avoid to deadlock using proc.wait()
        proc.wait()
        t = time.time() - t0

    return t


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
        parser.add_argument(dest="infile", help="input file [default: %(default)s]", metavar="in", nargs='+')
        parser.add_argument("-o", "--output", dest='output', help="path to output files [default: %(default)s]", metavar="Path")
        parser.add_argument("-b", "--binsize", help="bin size for SPD file index [Default: %(default)s]", default=10, type=float)
        parser.add_argument("-t", "--temppath", dest='temppath', help="A path were temporary files can be written too [default: %(default)s]", default="/tmp/", metavar="Path")
        parser.add_argument("-x", "--indexfield", help="The location used to index the pulses [default: %(default)s]", default="FIRST_RETURN", choices=["FIRST_RETURN", "LAST_RETURN"])
        parser.add_argument("-v", "--verbose", dest="verbose", action="count", help="set verbosity level [default: %(default)s]", default=0)
        parser.add_argument("-V", "--version", action="version", version=program_version_message)
        parser.add_argument("--input_proj", dest="iproj", help="WKT string representing the projection of the input file [default: %(default)s]", metavar="File")
        parser.add_argument("--output_proj", dest="oproj", help="WKT string representing the projection of the output file [default: %(default)s]", metavar="File")

        # Process arguments
        args = parser.parse_args()

        inFiles = args.infile
        output = args.output
        tempPath = args.temppath
        indexField = args.indexfield
        inProj = args.iproj
        outProj = args.oproj
        binsize = args.binsize
        verbose = args.verbose

        fout = open(os.path.join(output,'las2spd_times.res'), 'w')
        fout.write('NAME SIZE TIME(SEC)\n')

        for inFile in inFiles:
            commands = ['spdtranslate']

            # Projection input and output
            if inProj is not None:
                commands.append('--input_proj')
                commands.append(inProj)
                if outProj is not None:
                    commands.append('--convert_proj')
                    commands.append('--output_proj')
                    commands.append(outProj)

            # How to index SPD files
            commands.append('--indexfield')
            commands.append(indexField)
            # Bin size
            commands.append('--binsize')
            commands.append(str(binsize))
            # LAS in SPD out
            commands.append('--if LASNP --of SPD')

            if not os.path.isfile(inFile):
                print "%s: %s is not a valid file" % (program_name.split('.')[0], inFile)
                print ""
                print parser.print_help()
                return 2

            inputPath, inputName = os.path.split(os.path.realpath(inFile))
            baseName = inputName.split('.')[0]
            inLAS = inFile

            # Files grater than 60Mb will be translated by blocks in --temppath
            size = float(os.path.getsize(inLAS)) / 1048576.  # 1048576 bytes = 1 Mb
            if size > 60.0:
                tempPath = os.path.join(tempPath, os.path.basename(inFile).split('.')[0]) + '/'
                if not os.path.exists(tempPath): os.makedirs(tempPath)
                commands.append('--temppath')
                commands.append(tempPath)

            if output is None:
                outPath = os.path.abspath(inputPath)
            elif not os.path.isdir(output):
                print "%s: %s is not a valid path" % (program_name.split('.')[0], output)
                print ""
                print parser.print_help()
                return 2
            else:
                outPath = os.path.abspath(output)

            outPathName = os.path.join(outPath, baseName)
            print "Processing %s file..." % baseName

            # Translate LAS into SPD
            outSPD = outPathName + '.spd'
            commands.append('-i')
            commands.append(inLAS)
            commands.append('-o')
            commands.append(outSPD)
            commandline = " ".join(commands)
            print commandline
            t = runCommand(verbose, commandline)
            #runCommand(verbose, commands)

            outStr = '{0} {1:.1f} {2:10.6f}\n'.format(baseName, size, t)
            fout.write(outStr)

            shutil.rmtree(tempPath)

            print "[DONE]"

        fout.close()

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
