# -*- coding: UTF-8 -*-
#
# CVS History:
#
# $Id: smhi_safnwc_legends.py,v 1.4 2005/12/13 13:01:02 adybbroe Exp $
#
# $Log: smhi_safnwc_legends.py,v $
# Revision 1.4  2005/12/13 13:01:02  adybbroe
# *** empty log message ***
#
# Revision 1.3  2005/09/07 09:38:00  adybbroe
# *** empty log message ***
#
# Revision 1.2  2005/08/27 19:41:16  adybbroe
# *** empty log message ***
#
#
#
# ****************************************************************************


# ------------------------------------------------------------------
def get_tv_legend():
    legend = []
    legend.append((  0,  0,  0)) # Unprocessed: Black
    legend.append((  0,120,  0)) # Land
    legend.append((  0,  0,215)) # Sea: Blue

    for i in range(3,256):
        legend.append((i,i,i)) # All other pixel values are grey according to IR temp.        
    
    return legend

# ------------------------------------------------------------------
def get_vv_legend():
    legend = []
    legend.append((  0,  0,  0)) # Unprocessed: Black
    legend.append((  0,120,  0)) # Land
    legend.append((  0,  0,215)) # Sea: Blue
    # Cloud type values 5 to 8:
    legend.append((255,150,  0)) # Very low cumuliform
    legend.append((255,100,  0)) # Very low
    legend.append((255,220,  0)) # Low cumuliform
    legend.append((255,180,  0)) # Low

    for i in range(7,256):
        legend.append((i,i,i)) # All other pixel values are grey according to IR temp.        
    
    return legend

# --------------------------------------------------------------------
def get_ctype_vv1():

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
def get_ctype_vv2():

    legend = []
    legend.append((100,100,100)) # NEW Unprocessed: Grey
    legend.append((  0,120,  0)) # Land
    legend.append((  0,  0,  0)) # Sea: Black
    legend.append((  0,120,  0)) # Snow
    legend.append((  0,  0,  0)) # Sea-ice
    
    legend.append((255,150,  0)) # Very low cumuliform
    legend.append((255,100,  0)) # Very low
    legend.append((255,220,  0)) # Low cumuliform
    legend.append((255,180,  0)) # Low

    # Medium and high level clouds grey:
    legend.append((180,180,180)) # Medium cumuliform
    legend.append((180,180,180)) # Medium
    legend.append((180,180,180)) # High cumiliform
    legend.append((180,180,180)) # High
    legend.append((180,180,180)) # Very high cumuliform
    legend.append((180,180,180)) # Very high

    legend.append((60,80,160)) # Semi-transparent thin
    legend.append((80,100,180)) # Semi-transparent medium
    legend.append((180,180,180)) # Semi-transparent thick
    legend.append((180,180,180)) # Semi-transparent above
    legend.append((200,  0,200)) # Broken
    legend.append(( 95, 60, 30)) # NEW Undefined: Brown
    
    return legend

# --------------------------------------------------------------------
