#!/usr/bin/python2.7
# encoding: utf-8
'''
help2rst -- 

@author:     Roberto Antolín

@copyright:  2013 Roberto Antolín. All rights reserved.

@license:    license

@contact:    roberto dot antolin at forestry dot gsi dot gov dot uk
@deffield    updated: Updated
'''

import sys, os
import subprocess
import re

from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter

__all__ = []
__version__ = 0.1
__date__ = '2013-12-06'
__updated__ = '2013-12-12'

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


def printH1(h1):
    return '*'*len(h1) + '\n' + h1.upper() + '\n' + '*'*len(h1) + '\n'


def printH2(h2):
    return h2 + '\n' + '='*len(h2) + '\n'


def printH3(h3):
    return h3 + '\n' + '-'*len(h3) + '\n'


def writeFile(inputName, proc):
    baseName = inputName.split('.')[0]
    f = open(os.path.join('.', baseName + '.rst'), 'w')

    line = ''
    f.write(printH1(inputName))

    for nextLine in iter(proc.stdout.readline, ''):
        nextLine = nextLine.replace('\r', '').replace('\n', '')
        if nextLine == '' or nextLine.find('-- OR --') >= 0:
            line = line.replace('--, ', '')
            line = re.sub(',\ +\-\-', ', --', line)
            line = re.sub('  +', '  ', line)
            line = line.replace('  |', '|')
            if line.startswith('  '):
                line = line[2:]
            if line.startswith(' USAGE:'):
                f.write('\n')
                f.write(printH2(line[1:-2]))
            elif line.startswith(' Where:'):
                f.write('\n')
                f.write(printH3(line[1:-2]))
            elif line.startswith('<string>'):
                line = line.replace('<string>', '``<string>``\n  ')
                f.write('\n')
                f.write(line)
            elif line.find(inputName) >= 0:
                if line.endswith(inputName):
                    line = line.replace(inputName, '**{0}**'.format(inputName))
                    f.write('\n')
                    f.write(printH2('NAME'))
                    f.write(line)
                elif line.find('Copyright') >= 0:
                    f.write(line + '\n')
                else:
                    f.write('``{0}``'.format(line[line.find(inputName):]) + '\n')
            else:
                f.write(line + '\n')
            if nextLine.find('-- OR --') >= 0: 
                f.write('\n'+'**-- or --**'+'\n')
            line=''
        else:
            line = line + ' ' + nextLine

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
        parser = ArgumentParser(description=program_license, \
            formatter_class=RawDescriptionHelpFormatter)
        parser.add_argument(dest="infile", help="input file", metavar="in", nargs='+')
        parser.add_argument("-L", "--latex", action="store_true", help="Transform into LaTeX")
        parser.add_argument("-H", "--html", action="store_true", help="Transform into html")
        parser.add_argument("-O", "--odt", action="store_true", help="Transform into odt")
        parser.add_argument("-M", "--man", action="store_true", help="Transform into man pages")
        parser.add_argument("-v", "--verbose", dest="verbose", action="count", help="set verbosity \
            level [Default: %(default)s]", default=0)
        parser.add_argument("-V", "--version", action="version", version=program_version_message)

        # Process arguments
        args = parser.parse_args()

        inFiles = args.infile
        latex = args.latex
        html = args.html
        odt = args.odt
        man = args.man

        for inFile in inFiles:
            inputPath, inputName = os.path.split(os.path.realpath(inFile))
            inSPD = inFile
            baseName = inputName.split('.')[0]
            cmd = '{0} --help'.format(inFile) 
            proc = subprocess.Popen(cmd, shell=True, \
                stdout=subprocess.PIPE, \
                stderr=subprocess.STDOUT, \
                universal_newlines=False)

            writeFile(inputName, proc)
            sys.stdout.flush()

            if html:
                htmlCmd = 'rst2html {0}.rst {0}.html'.format(baseName)
                subprocess.Popen(htmlCmd, shell=True)
            if latex:
                latexCmd = 'rst2latex {0}.rst {0}.tex'.format(baseName)
                subprocess.Popen(latexCmd, shell=True)
            if odt:
                odtCmd = 'rst2odt {0}.rst {0}.doc'.format(baseName)
                subprocess.Popen(odtCmd, shell=True)
            if man:
                manCmd = 'rst2man {0}.rst {0}.man'.format(baseName)
                subprocess.Popen(manCmd, shell=True)

            # TODO:
            # Identify help output strings in order to rearrange output

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
