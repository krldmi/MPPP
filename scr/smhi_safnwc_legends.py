# -*- coding: UTF-8 -*-
#
# CVS History:
#
# $Id: smhi_safnwc_legends.py,v 1.1 2005/08/27 19:21:13 adybbroe Exp $
#
# $Log: smhi_safnwc_legends.py,v $
# Revision 1.1  2005/08/27 19:21:13  adybbroe
# Initial revision
#
#
#
# ****************************************************************************


# --------------------------------------------------------------------
def get_ctype_vv():

    legend = []
    legend.append((100,100,100)) # NEW Unprocessed: Grey
    legend.append((  0,120,  0))
    legend.append((  0,  0,  0)) # Sea: Black
    legend.append((250,190,250)) # Snow
    legend.append((220,160,220)) # Sea-ice
    
    legend.append((255,150,  0)) # Very low cumuliform
    legend.append((255,100,  0)) # Very low
    legend.append((255,220,  0)) # Low cumuliform
    legend.append((255,180,  0)) # Low

    # Medium and high level clouds grey:
    legend.append((150,150,150)) # Medium cumuliform
    legend.append((150,150,150)) # Medium
    legend.append((180,180,180)) # High cumiliform
    legend.append((180,180,180)) # High
    legend.append((210,210,210)) # Very high cumuliform
    legend.append((210,210,210)) # Very high

    legend.append((60,80,160)) # Semi-transparent thin
    legend.append((80,100,180)) # Semi-transparent medium
    legend.append((100,130,200)) # Semi-transparent thick
    legend.append((120,160,210)) # Semi-transparent above
    legend.append((200,  0,200)) # Broken
    legend.append(( 95, 60, 30)) # NEW Undefined: Brown
    
    return legend

# --------------------------------------------------------------------
