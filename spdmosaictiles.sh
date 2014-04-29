#!/bin/sh
# spdmosaictiles -- Mosaic tiles

# @author:     Roberto Antolín
# @contact:    roberto dot antolin at forestry dot gsi dot gov dot uk
# @deffield    updated: Updated
# @copyright:  2014 Roberto Antolín. All rights reserved.
# @license:    license
# Distributed on an "AS IS" basis without warranties
# or conditions of any kind, either express or implied.


# USAGE
# spdmosaictiles.sh tiles_definition.xml

# Mosaics tiles in the current directory.

# spdmosaictiles uses spdcliptiles to create new tiles clipped according to the 
# tiles definition givin in the xml file. The new tiles are store in a new folder 
# called 'coretiles'. spdmosaictiles then mosaics the tiles within coretiles by 
# means of spdtileimg. Files must be named as rowXXcolXX, otherwise it will 
# not work. 



XML=$1

mkdir coretiles
spdcliptiles.py -x $XML -i ./ -o coretiles/
ls -1 *.tif > files.lst
spdtileimg -m -i files.lst -t $XML -o mosaic.tif --ignore-row-col -f GTiff