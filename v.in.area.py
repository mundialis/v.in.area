#!/usr/bin/env python3
#
############################################################################
#
# MODULE:      v.in.area
# AUTHOR(S):   Anika Weinmann
#
# PURPOSE:     Checks if the input vector map (geometry type is points or
#              polygons) is partly inside a given area
#
# COPYRIGHT:    (C) 2020-2022 by mundialis GmbH & Co. KG and the GRASS Development Team
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#############################################################################
# %module
# % description: Checks if the input vector map (geometry type is points or polygons) is partly located inside a given area.
# % keyword: vector
# % keyword: overlay
# %end

# %option G_OPT_V_INPUT
# % key: map
# % description: Input vector map to check
# %end

# %option G_OPT_V_INPUT
# % key: area
# % description: Input area vector map
# %end

# %option
# % key: type
# % type: string
# % required: no
# % multiple: yes
# % options: point,area,auto
# % label: Feature type of input vector map
# % answer: auto
# %end

# %flag
# % key: e
# % description: Throw error, if input map does not overlap with area
# %end

import atexit
import os
import random
import string
import sys

import grass.script as grass

# initialize global vars
rm_vectors = []


def cleanup():
    grass.message(_("Cleaning up..."))
    nuldev = open(os.devnull, "w")
    for rm_v in rm_vectors:
        grass.run_command(
            "g.remove", flags="f", type="vector", name=rm_v, quiet=True, stderr=nuldev
        )


def test_requiered_data(rastermaps, vectormaps):
    # Test if all required data are there
    for rast in rastermaps:
        if not grass.find_file(name=rast, element="raster")["file"]:
            grass.fatal(_("Raster map <%s> not found" % (rast)))
    for vect in vectormaps:
        if not grass.find_file(name=vect, element="vector")["file"]:
            grass.fatal(_("Vector map <%s> not found" % (vect)))


def main():

    global rm_vectors

    map = options["map"]
    area = options["area"]
    type = options["type"]

    # Test if all required data are there
    test_requiered_data([], [map, area])

    # set type if type is auto
    if type == "auto":
        topo = grass.vector_info_topo(map)
        # areas
        if topo["centroids"] > 0 and topo["lines"] == 0 and topo["points"] == 0:
            type = "area"
        # points
        elif topo["centroids"] == 0 and topo["lines"] == 0 and topo["points"] > 0:
            type = "point"
        # lines
        elif topo["centroids"] == 0 and topo["lines"] > 0 and topo["points"] == 0:
            type = "line"
        else:
            grass.fatal(
                _(
                    "The geometry type of <%s> is not clear (%d areas, %d points, %d lines)"
                    % (map, topo["centroids"], topo["lines"], topo["points"])
                )
            )

    # test overlap
    grass.message(_("Checking overlap ..."))
    tmpname = "tmp_%s" % (
        "".join(random.choice(string.ascii_letters) for i in range(5))
    )
    # test for type = point
    if type == "point":
        new_table = False
        try:
            grass.run_command("v.db.select", map=area, quiet=True)
        except Exception:
            new_table = True
            grass.run_command("v.db.addtable", map=area, quiet=True)
        grass.run_command(
            "v.db.addcolumn", map=map, columns="%s integer" % tmpname, quiet=True
        )
        grass.run_command(
            "v.what.vect",
            map=map,
            column=tmpname,
            query_map=area,
            query_column="cat",
            quiet=True,
        )
        test = grass.parse_command("v.db.select", map=map, columns=tmpname, flags="c")
        grass.run_command(
            "v.db.dropcolumn", map=map, columns="%s" % tmpname, quiet=True
        )
        if new_table:
            grass.run_command("v.db.droptable", map=area, flags="f", quiet=True)
        mind_one_point_inside = False
        for key in test:
            if not key == "":
                mind_one_point_inside = True
        if not mind_one_point_inside:
            if flags["e"]:
                grass.fatal(_("<%s> does not overlap with <%s>" % (map, area)))
            else:
                sys.stdout.write("<%s> does not overlap with <%s>\n" % (map, area))
        else:
            sys.stdout.write("<%s> overlaps with <%s>\n" % (map, area))
    # test for type =  area
    elif type == "area":
        grass.run_command(
            "v.overlay",
            ainput=map,
            binput=area,
            operator="and",
            output=tmpname,
            quiet=True,
        )
        rm_vectors.append(tmpname)
        geoms = grass.vector_info_topo(tmpname)
        if int(geoms["centroids"]) == 0:
            if flags["e"]:
                grass.fatal(_("<%s> does not overlap with <%s>" % (map, area)))
            else:
                sys.stdout.write("<%s> does not overlap with <%s>\n" % (map, area))
        else:
            sys.stdout.write("<%s> overlaps with <%s>\n" % (map, area))
    else:
        grass.fatal(_("Geometry type <%s> is not supported" % type))

    grass.message(_("Check is done"))


if __name__ == "__main__":
    options, flags = grass.parser()
    atexit.register(cleanup)
    main()
