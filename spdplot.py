'''
Created on 14/08/2013

@author: roberto
'''

import pylab
import sys, os
import numpy as np

def sortLists(L1, L2):
    """(list, list) -> [list, list]
    Sort two list
    
    >>> L1 = [2,1]
    >>> L2 = [a,b]
    >>> l1, l2 = sortLists(L1,L2)
    >>> print l1, l2
    [1,2], [b,a]
    """
    return (list(t) for t in zip(*sorted(zip(L1, L2))))

def main():
    timesFile = sys.argv[1]
    path = os.path.dirname(timesFile)
    cmd = os.path.basename(timesFile).split('_')[0]
    
    numTempFiles = 0
    
    X = np.loadtxt(timesFile, skiprows=1, usecols=[1,2], delimiter=';')
    #fileName = X[:, 0]
    fileSize = X[:, 0]
    exeTimes = X[:, 1]
    
    totalTime = np.sum(exeTimes)
    totalSize = np.sum(fileSize)
    
    for size in fileSize:
        if size > 50.0:
            numTempFiles +=1
    
    #np.average(exeTimes)
    #np.std(exeTimes)
    
    print totalTime / 60., totalSize / 1024., totalSize*60/totalTime, numTempFiles / float(len(fileSize))
    
    # Sorting by File Size
    fileSize, exeTimes = sortLists(fileSize, exeTimes)
    
    # Plotting a fancy chart
    pylab.figure()
    pylab.plot(fileSize, exeTimes)
    pylab.xlabel('File sizes (Mb)')
    pylab.ylabel('Time (sec)')
    pylab.title('%s run times' %(cmd))
    pylab.show()
    pylab.savefig(path + cmd + '_times.png')


if __name__ == '__main__':
    main()
