#!/usr/bin/env python3
#
############################################################################
#
# MODULE:      v.in.area test
# AUTHOR(S):   Anika Weinmann
#
# PURPOSE:     Tests v.in.area inputs.
#              Uses NC full sample data set.
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

import os

from grass.gunittest.case import TestCase
from grass.gunittest.main import test
from grass.gunittest.gmodules import SimpleModule


class TestVInArea(TestCase):
    area_file = "data/area.geojson"
    polygon_in = "data/polygon_in.geojson"
    polygon_out = "data/polygon_out.geojson"
    points_in = "data/points_in.geojson"
    points_out = "data/points_out.geojson"
    line = "data/line.geojson"
    pid_str = str(os.getpid())
    area = "area_test_%s" % pid_str
    vectormap = "vector_test_%s" % pid_str
    region = "region_%s" % pid_str

    @classmethod
    def setUpClass(self):
        """Ensures expected computational region and generated data"""
        # import general area
        self.runModule("v.import", input=self.area_file, output=self.area)
        # set temp region
        self.runModule("g.region", save=self.region)
        # set region to area
        self.runModule("g.region", vector=self.area)

    @classmethod
    def tearDownClass(self):
        """Remove the temporary region and generated data"""
        self.runModule("g.remove", type="vector", name=self.area, flags="f")
        self.runModule("g.region", region=self.region)
        self.runModule("g.remove", type="region", name=self.region, flags="f")

    def tearDown(self):
        """Remove the outputs created
        This is executed after each test run.
        """
        self.runModule("g.remove", type="vector", name=self.vectormap, flags="f")

    def test_polygon_is_in_area(self):
        """Test if polygon is in area"""
        self.runModule("v.import", input=self.polygon_in, output=self.vectormap)

        v_in_area_out = SimpleModule("v.in.area", area=self.area, map=self.vectormap)
        self.assertModule(v_in_area_out)
        # test that error output is not empty
        stdout = v_in_area_out.outputs.stdout
        self.assertTrue(stdout)
        # test that the right map is mentioned in the error message
        self.assertEquals(
            "<%s> overlaps with <%s>\n" % (self.vectormap, self.area), stdout
        )

    def test_polygon_is_in_area_type(self):
        """Test if polygon is in area"""
        self.runModule("v.import", input=self.polygon_in, output=self.vectormap)

        v_in_area_out = SimpleModule(
            "v.in.area", area=self.area, map=self.vectormap, type="area"
        )
        self.assertModule(v_in_area_out)
        # test that error output is not empty
        stdout = v_in_area_out.outputs.stdout
        self.assertTrue(stdout)
        # test that the right map is mentioned in the error message
        self.assertEquals(
            "<%s> overlaps with <%s>\n" % (self.vectormap, self.area), stdout
        )

    def test_polygon_is_not_in_area_error(self):
        """Test if polygon is not in area with thrown error"""
        self.runModule("v.import", input=self.polygon_out, output=self.vectormap)

        v_in_area_error = SimpleModule(
            "v.in.area", area=self.area, map=self.vectormap, flags="e"
        )
        self.assertModuleFail(v_in_area_error)
        # test that error output is not empty
        stderr = v_in_area_error.outputs.stderr
        self.assertTrue(stderr)
        # test that the right map is mentioned in the error message
        self.assertIn(self.area, stderr)
        self.assertIn(self.vectormap, stderr)

    def test_polygon_is_not_in_area(self):
        """Test if polygon is not in area"""
        self.runModule("v.import", input=self.polygon_out, output=self.vectormap)

        v_in_area_out = SimpleModule("v.in.area", area=self.area, map=self.vectormap)
        self.assertModule(v_in_area_out)
        # test that error output is not empty
        stdout = v_in_area_out.outputs.stdout
        self.assertTrue(stdout)
        # test that the right map is mentioned in the error message
        self.assertEquals(
            "<%s> does not overlap with <%s>\n" % (self.vectormap, self.area), stdout
        )

    def test_points_are_in_area(self):
        """Test if points are in area"""
        self.runModule("v.import", input=self.points_in, output=self.vectormap)

        v_in_area_out = SimpleModule("v.in.area", area=self.area, map=self.vectormap)
        self.assertModule(v_in_area_out)
        # test that error output is not empty
        stdout = v_in_area_out.outputs.stdout
        self.assertTrue(stdout)
        # test that the right map is mentioned in the error message
        self.assertIn("<%s> overlaps with <%s>\n" % (self.vectormap, self.area), stdout)

    def test_points_are_in_area_type(self):
        """Test if points are in area"""
        self.runModule("v.import", input=self.points_in, output=self.vectormap)

        v_in_area_out = SimpleModule(
            "v.in.area", area=self.area, map=self.vectormap, type="point"
        )
        self.assertModule(v_in_area_out)
        # test that error output is not empty
        stdout = v_in_area_out.outputs.stdout
        self.assertTrue(stdout)
        # test that the right map is mentioned in the error message
        self.assertIn("<%s> overlaps with <%s>\n" % (self.vectormap, self.area), stdout)

    def test_points_are_not_in_area_error(self):
        """Test if points are not in area with thrown error"""
        self.runModule("v.import", input=self.points_out, output=self.vectormap)

        v_in_area_error = SimpleModule(
            "v.in.area", area=self.area, map=self.vectormap, flags="e"
        )
        self.assertModuleFail(v_in_area_error)
        # test that error output is not empty
        stderr = v_in_area_error.outputs.stderr
        self.assertTrue(stderr)
        # test that the right map is mentioned in the error message
        self.assertIn(self.area, stderr)
        self.assertIn(self.vectormap, stderr)

    def test_points_are_not_in_area(self):
        """Test if points are not in area"""
        self.runModule("v.import", input=self.points_out, output=self.vectormap)

        v_in_area_out = SimpleModule("v.in.area", area=self.area, map=self.vectormap)
        self.assertModule(v_in_area_out)
        # test that error output is not empty
        stdout = v_in_area_out.outputs.stdout
        self.assertTrue(stdout)
        # test that the right map is mentioned in the error message
        self.assertIn(
            "<%s> does not overlap with <%s>\n" % (self.vectormap, self.area), stdout
        )

    def test_line_error(self):
        """Test if line fails"""
        self.runModule("v.import", input=self.line, output=self.vectormap)

        v_in_area_error = SimpleModule(
            "v.in.area", area=self.area, map=self.vectormap, flags="e"
        )
        self.assertModuleFail(v_in_area_error)
        # test that error output is not empty
        stderr = v_in_area_error.outputs.stderr
        self.assertTrue(stderr)
        # test that the right map is mentioned in the error message
        self.assertIn("Geometry type <line> is not supported", stderr)


if __name__ == "__main__":
    test()
