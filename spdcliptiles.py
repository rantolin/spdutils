#!/usr/bin/python2.7
# encoding: utf-8
'''
spdcliptiles -- Clip tiles generated with SPDlib

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


__all__ = []
__version__ = 0.1
__date__ = '2014-04-08'
__updated__ = '2014-04-22'

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

Clips tiles within the input path to their nominal extent 
according to the definition given by SPD xml files. Output 
tiles are recorded in the output path.

Files must be named as rowXXcolXX.spd, otherwise it will not work. 

Core extent is available with the '-c' argument.
''' % (program_shortdesc, str(__date__))

    try:
        # Setup argument parser


        parser = ArgumentParser(description=program_license, formatter_class=RawDescriptionHelpFormatter)
        parser.add_argument("-x", "--xml", dest="xmlfile", help="XML file where containing the tiles definition", metavar="XML", required=True)
        parser.add_argument("-i", "--input", help="path to input tiles", metavar="PATH", required=True)
        parser.add_argument("-o", "--output", help="path to output files", metavar="PATH", required=True)
        parser.add_argument("-c", "--core", help='Clip tiles to their core extent', action='store_true')
        parser.add_argument("-p", "--proj", help='Projection information in GDAL format [default: %(default)s]', default='EPSG:27700')
        parser.add_argument("-f", "--format", help='Format of the input tiles [default: %(default)s]', default='tif')
        # parser.add_argument("-s", "--string", help='String format for tiles name [default: %(default)s]', default='500m_rowXXcolXX_10m_pmfgrd_mccgrd_height')
        parser.add_argument("-V", "--version", action="version", version=program_version_message)

        # Process arguments
        args = parser.parse_args()

        xmlFile = args.xmlfile
        inDir = args.input
        outDir = args.output
        core = args.core
        proj = args.proj
        format = args.format

        tree = ET.parse(xmlFile)
        root = tree.getroot()

        if core:
            coreString = 'core'
        else:
            coreString = ''

        for child in root:
            row = int(child.attrib['row'])
            col = int(child.attrib['col'])
            finput = inDir + 'row{0}col{1}.{2}'.format(row, col, format)
            if os.path.isfile(finput):
                foutput = outDir + 'row{0}col{1}.{2}'.format(row, col, format)
                print "Processing {}...".format(foutput)
                xmin = int(child.attrib[coreString+'xmin'])-1   # Extend 1m the boundaries of the core tile
                xmax = int(child.attrib[coreString+'xmax'])+1
                ymin = int(child.attrib[coreString+'ymin'])-1
                ymax = int(child.attrib[coreString+'ymax'])+1
                gdal = 'gdal_translate -projwin {0} {1} {2} {3} {4} {5} -a_srs {6}'.format(xmin, ymax, xmax, ymin, finput, foutput, proj)
                proc = subprocess.Popen(gdal, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=False)
                proc.wait()
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
