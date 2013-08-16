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
    fout = open(path + 'spdpmfgrd_times.txt', 'w')
    fout.write('NAME SIZE TIME(SEC)\n')
    execTime = []
    fileSize = []
    
    for spd in glob.glob(path + 'spd/QE*.spd'):
        size = float(os.path.getsize(spd)) / 1048576.  # 1048576 bytes = 1 Mb
        fileSize.append(size)
        fileName = os.path.basename(spd).split('.')[0]
        cmd = 'spdpmfgrd -o %s_filter.spd -i %s' % (path + 'filter_pmf/' + fileName, spd) 
        t0 = time.time()
        print cmd
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.STDOUT)
        p.wait()
        t = time.time() - t0
        execTime.append(t)
        outStr = '%s %.1f %.1f\n' % (fileName, size, t)
        fout.write(outStr)
    
    fout.close()
    
if __name__ == '__main__':
    main()
