#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2009.

# SMHI,
# Folkborgsvägen 1,
# Norrköping, 
# Sweden

# Author(s):
 
#   Martin Raspaud <martin.raspaud@smhi.se>
#   Adam Dybbroe <adam.dybbroe@smhi.se>

# This file is part of the MPPP.

# MPPP is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# MPPP is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with MPPP.  If not, see <http://www.gnu.org/licenses/>.

"""This module handles coverage objects. Such objects are used to
transform area projected data by changing either the area or the
projection or both. A typical usage is to transform one large area in
satellite projection to an area of interest in polar projection for
example.
"""

import os
import numpy

import logging

import _pyhl
import _satproj
import area

COMPRESS_LVL = 6

LOG = logging.getLogger('pp.satellite')

# !!! This class is already defined in satproj somehow, would be nice to
# extend it (inherit) instead of creating it from scratch...

class SatProjCov(object):
    """This is the class that defines coverage objects. They contain the
    mapping information necessary for projection purposes. For efficiency
    reasons, generated coverages are saved to disk for later reuse.
    """
    # Coverage data
    coverage = None

    colidx = None
    rowidx = None

    # Input area
    in_area_id = None

    # Output area
    out_area_id = None


    is_hr = False

    def __init__(self, snapshot, 
                 out_area_id = None, resolution = None):
        self.coverage = None
        self.colidx = None
        self.rowidx = None
        self.in_area_id = snapshot.area
        self.out_area_id = out_area_id
        self.resolution = resolution

        if resolution is None:
            raise ValueError("The resolution must be an integer!")

        self._filename = ("%s/%s_coverage_%s.%s.%d.hdf"
                          %("/tmp",
                            snapshot.satname,
                            self.in_area_id, 
                            self.out_area_id,
                            self.resolution))


        if((self.in_area_id is None) or (self.out_area_id is None)):
            raise RuntimeError("Input/output area not defined.")
        
        LOG.info("Getting coverage for %s onto %s."
                 %(self.in_area_id, self.out_area_id))

        if not os.path.exists(self._filename):
            LOG.info("Generate coverage and store in file %s..."
                     %(self._filename))

            lat, lon = snapshot.get_lat_lon(resolution)

            area_obj = area.area(out_area_id)
            coverage_data = _satproj.create_coverage(area_obj, lon, lat, 1)

            self.colidx = numpy.array(coverage_data.colidx, numpy.int16)
            self.rowidx = numpy.array(coverage_data.rowidx, numpy.int16)
            self.coverage = numpy.array(coverage_data.coverage, numpy.int8)
            self.write()

        else:
            LOG.info("Read the coverage from file %s..."
                     %(self._filename))
            self.read()
        
    def write(self):
        """Write coverage to a file for later usage.
        """

        struct = _pyhl.nodelist()
        
        node = _pyhl.node(_pyhl.GROUP_ID, "/info")
        struct.addNode(node)

        node = _pyhl.node(_pyhl.ATTRIBUTE_ID, "/info/description")
        node.setScalarValue(-1,
                             "Coverage from area %s on to area %s"
                             %(self.in_area_id,
                               self.out_area_id),
                             "string",-1)
        struct.addNode(node)
        
        shape = [self.coverage.shape[0], self.coverage.shape[1]]
        node = _pyhl.node(_pyhl.DATASET_ID, "/coverage")
        node.setArrayValue(1, shape, self.coverage, "uchar", -1)
        struct.addNode(node)

        node = _pyhl.node(_pyhl.DATASET_ID, "/rowidx")
        node.setArrayValue(1, shape, self.rowidx, "ushort", -1)
        struct.addNode(node)

        node = _pyhl.node(_pyhl.DATASET_ID, "/colidx")
        node.setArrayValue(1, shape, self.colidx, "ushort", -1)
        struct.addNode(node)
        
        struct.write(self._filename, COMPRESS_LVL)
        
    

    def read(self):
        """Read a previously saved coverage file and load it into the current
        instance.
        """

        struct = _pyhl.read_nodelist(self._filename)
        
        struct.selectNode("/info/description")
        struct.selectNode("/coverage")
        struct.selectNode("/rowidx")
        struct.selectNode("/colidx")
        struct.fetch()
        
        info = {}
        desc = struct.getNode("/info/description")
        info["description"] = desc.data()
        
        cov = struct.getNode("/coverage")
        coverage = cov.data()
        row = struct.getNode("/rowidx")
        rowidx = row.data()
        col = struct.getNode("/colidx")
        colidx = col.data()
        
        self.coverage = coverage.astype('b')
        self.rowidx = rowidx.astype('h')
        self.colidx = colidx.astype('h')
            
    def project_array(self, arr):
        """Project the masked array *a* along the current coverage.
        """
        if (arr is None):
            return None

        no_data = -99999
        
        if(isinstance(arr, numpy.ma.core.MaskedArray)):
            amask = numpy.ones(arr.shape)
            amask[arr.mask] = 0
            a_filled = arr.filled(no_data)
        else:
            amask = None
            a_filled = arr

        pmask = None

        # This is kinda dirty, but necessary until _satproj supports masked
        # arrays.

        res = _satproj.project(self.coverage,
                               self.rowidx,
                               self.colidx,
                               a_filled,
                               int(no_data))
        if(amask is not None):
            pmask = _satproj.project(self.coverage,
                                     self.rowidx,
                                     self.colidx,
                                     amask,
                                     0)

        if pmask is None:
            return res
        else:
            return numpy.ma.array(res, mask = (pmask == 0))


