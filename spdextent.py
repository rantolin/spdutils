#!/usr/bin/python2.7
# encoding: utf-8
'''
spdextent -- Get the extent of a spd file

@author:     Roberto Antolín

@copyright:  2013 Roberto Antolín. All rights reserved.

@license:    license

@contact:    roberto dot antolin at forestry dot gsi dot gov dot uk
@deffield    updated: Updated
'''

import sys, os
import subprocess
import tempfile

from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter

__all__ = []
__version__ = 0.1
__date__ = '2013-11-05'
__updated__ = '2013-11-05'

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
    proc = subprocess.Popen(cmd, shell=True, \
        stdout=subprocess.PIPE, \
        stderr=subprocess.STDOUT, \
        universal_newlines=False)
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
        parser.add_argument(dest='infile', help='input file', metavar='in', nargs='*')
        parser.add_argument("-V", "--version", action="version", version=program_version_message)
        
        # Process arguments
        args = parser.parse_args()

        inFiles = args.infile
        
        tempDir = tempfile.mkdtemp()

        if os.path.basename(inFiles[0]).split('.')[1] == 'lst':
            fileList = inFiles[0]
        else:
            fList, fileList = tempfile.mkstemp(suffix='.lst', dir=tempDir, text=True)
            fList = open(fileList, 'w')
            for inFile in inFiles:
                fList.write(inFile + '\n')
            fList.close()

        fileExtent, tempfileExtent = tempfile.mkstemp(suffix='.ext', dir=tempDir, text=True)

        extentcommand = 'spddeftiles --extent -i {0} > {1}'.format(fileList, tempfileExtent)
        proc = subprocess.Popen(extentcommand, shell=True, \
            stdout=subprocess.PIPE, stdin=subprocess.PIPE, \
            stderr=subprocess.STDOUT, universal_newlines=False)

        proc.wait()

        fileExtent = open(tempfileExtent, 'r')
        extent = fileExtent.readlines()[-2][34:-2]
        fileExtent.close()
        extent = extent.split(', ')
        xmin = extent[0]
        xmax = extent[1]
        ymin = extent[2]
        ymax = extent[3]

        print '--xmin {0:.2f} --xmax {1:.2f} --ymin {2:.2f} --ymax {3:.2f}' \
            .format(float(xmin), float(xmax), float(ymin), float(ymax))

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
