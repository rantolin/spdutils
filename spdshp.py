#!/usr/bin/python2.7
# encoding: utf-8
'''
spdshp -- Create a shape file from a tiling definition 

@author:     Roberto Antolín

@copyright:  2013 Roberto Antolín. All rights reserved.

@license:    license

@contact:    roberto dot antolin at forestry dot gsi dot gov dot uk
@deffield    updated: Updated
'''
import shapefile as shp
import xml.etree.ElementTree as ET
import sys, os, subprocess, shutil

from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter

__all__ = []
__version__ = 0.1
__date__ = '2013-11-20'
__updated__ = '2013-11-20'

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
        parser.add_argument(dest='infile', help='input file', metavar='in')
        parser.add_argument(dest='outfile', help='output file', metavar='out')
        parser.add_argument('-p', '--projection', dest='projection', metavar='WKT', help='Create the projection information [Default: %(default)s]')
        parser.add_argument("-V", "--version", action="version", version=program_version_message)

        args = parser.parse_args()
        infile = args.infile
        outfile = args.outfile
        projection = args.projection

        tree = ET.parse(infile)
        root = tree.getroot()
        count = 0
        w = shp.Writer(shp.POLYGON)
        w.field('FIRST_FLD','C','40')
        # w.record('First','Polygon')
        # w.field('SECOND_FLD','C','40')
        for child in root:
        	count += 1
        	xmax = float(child.attrib['corexmax'])
        	ymax = float(child.attrib['coreymax'])
        	xmin = float(child.attrib['corexmin'])
        	ymin = float(child.attrib['coreymin'])
        	w.poly(parts=[[[xmin,ymin],[xmax,ymin],[xmax,ymax],[xmin,ymax],[xmin,ymin]]])
        	w.record(str(count))

        w.save(outfile)
        if projection is not None: # create the PRJ file
        	shutil.copyfile(projection, "{0}.prj".format(outfile))
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
