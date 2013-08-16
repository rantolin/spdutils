# -*- coding: utf-8 -*-
#!/usr/bin/python

'''
Created on 13/08/2013

@author: roberto DOT antolin AT forestry DOT gis.gov.uk
'''

import glob, os, subprocess

def main():
    spdCmdPath = '/home/roberto/src/spdlib/'
    for spdCmd in glob.glob(spdCmdPath + 'spd*'):
        tool = os.path.basename(spdCmd)
        if tool != 'spdtsample':
            cmd = '%s --help' %tool
            #print cmd
            proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.STDOUT).stdout
            description = proc.readlines()[-2].split(':')[0].lstrip()
            print '%r: %r' %(description, tool)
            if description == tool:
                print 'HOLA!!'
                description = proc.readlines()[-3].split(':')[0]
            print '-**%s**: %s' %(tool, description)

if __name__ == '__main__':
    main()
