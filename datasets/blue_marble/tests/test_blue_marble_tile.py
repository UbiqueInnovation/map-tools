from unittest import TestCase

from numpy.ma.testutils import assert_equal

from datasets.blue_marble import BlueMarble
from tiles import Wgs84Coordinate


class TestBlueMarbleTile(TestCase):
    def test_bounds(self) -> None:
        tiles = {tile.identifier: tile for tile in BlueMarble.tiles()}

        assert_equal(Wgs84Coordinate(lat=90, lon=-180), tiles["A1"].upper_left)
        assert_equal(Wgs84Coordinate(lat=90, lon=-90), tiles["B1"].upper_left)
        assert_equal(Wgs84Coordinate(lat=90, lon=0), tiles["C1"].upper_left)
        assert_equal(Wgs84Coordinate(lat=90, lon=90), tiles["D1"].upper_left)
        assert_equal(Wgs84Coordinate(lat=0, lon=-180), tiles["A2"].upper_left)
        assert_equal(Wgs84Coordinate(lat=0, lon=-90), tiles["B2"].upper_left)
        assert_equal(Wgs84Coordinate(lat=0, lon=0), tiles["C2"].upper_left)
        assert_equal(Wgs84Coordinate(lat=0, lon=90), tiles["D2"].upper_left)

        assert_equal(Wgs84Coordinate(lat=0, lon=-90), tiles["A1"].lower_right)
        assert_equal(Wgs84Coordinate(lat=0, lon=0), tiles["B1"].lower_right)
        assert_equal(Wgs84Coordinate(lat=0, lon=90), tiles["C1"].lower_right)
        assert_equal(Wgs84Coordinate(lat=0, lon=180), tiles["D1"].lower_right)
        assert_equal(Wgs84Coordinate(lat=-90, lon=-90), tiles["A2"].lower_right)
        assert_equal(Wgs84Coordinate(lat=-90, lon=0), tiles["B2"].lower_right)
        assert_equal(Wgs84Coordinate(lat=-90, lon=90), tiles["C2"].lower_right)
        assert_equal(Wgs84Coordinate(lat=-90, lon=180), tiles["D2"].lower_right)
