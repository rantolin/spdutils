# -*- coding: utf-8 -*-
#!/usr/bin/python

'''
Created on 13/08/2013

@author: roberto DOT antolin AT forestry DOT gis.gov.uk
'''

import glob, os, subprocess
import time

def main():
    path = '/home/roberto/Documents/trabajo/Thermolidar/data/Aberfoyle_2012/Classified_500m_tiles/'
    tmp = '/tmp/'
    fout = open(path + 'spdtranslate_times.txt', 'w')
    fout.write('NAME SIZE TIME(SEC)\n')
    exeTime = []
    fileSize = []
    
    for las in glob.glob(path + 'las/QE*.las'):
        size = float(os.path.getsize(las)) / 1048576.  # 1048576 bytes = 1 Mb
        fileSize.append(size)
        fileName = os.path.basename(las).split('.')[0]
        cmd = 'spdtranslate --if LAS --of SPD -o %s.spd -i %s -x FIRST_RETURN' % (path + 'spd/' + fileName, las) 
        if size > 50.0:
            cmd += ' --temppath %s' %(tmp) 
        
        cmd += ' 2> /dev/null'
        t0 = time.time()
        proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
        proc.wait()
        t = time.time() - t0
        exeTime.append(t)
        outStr = '%s %.1f %.1f\n' % (fileName, size, t)
        fout.write(outStr)

if __name__ == '__main__':
    main()
