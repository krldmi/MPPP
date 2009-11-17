#### for mppp

PYTHONPATH=${PYTHONPATH}:/local_disk/usr/test/etc
export PYTHONPATH

#### for acpg

PYTHONPATH=${PYTHONPATH}:/local_disk/usr/dists/ACPG/lib:/local_disk/usr/dists/ACPG/scr:/local_disk/usr/dists/ACPG/cfg
export PYTHONPATH

SM_REGION_CONFIGURATION_FILE=/local_disk/usr/dists/ACPG/cfg/region_config.cfg
export SM_REGION_CONFIGURATION_FILE

LD_LIBRARY_PATH=/local_disk/usr/dists/v0.7.7/lib:$LD_LIBRARY_PATH

#### for ahamap

# ahamap needs region definition and area lib, but this is already loaded above.

#SM_REGION_CONFIGURATION_FILE=/local_disk/usr/dists/ACPG/cfg/region_config.cfg
#export SM_REGION_CONFIGURATION_FILE

#PYTHONPATH=${PYTHONPATH}:/local_disk/usr/dists/ACPG/lib

PYTHONPATH=$PYTHONPATH:/data/proj/safworks/opt/fc10/AHAMAP/1_55/lib
export PYTHONPATH
