from unittest import TestCase

from tiles import Wgs84TileInfo, Wgs84Coordinate


class TestWgs84TileInfo(TestCase):
    def assertTupleAlmostEqual(
        self, first: tuple, second: tuple, places=None, msg=None, delta=None
    ):
        self.assertAlmostEqual(len(first), len(second))
        for a, b in zip(first, second):
            self.assertAlmostEqual(a, b, places, msg, delta)

    def test_size(self) -> None:
        self.assertEqual(
            (5.625, 2.8125),
            Wgs84TileInfo(zoom=6, x=33, y=22).size,
        )

    def test_bounds(self) -> None:
        root_tile = Wgs84TileInfo(zoom=0, x=0, y=0)
        self.assertEqual(
            Wgs84Coordinate(lat=90, lon=-180),
            root_tile.top_left,
        )
        self.assertEqual(
            Wgs84Coordinate(lat=-90, lon=180),
            root_tile.bottom_right,
        )
        self.assertEqual(
            Wgs84Coordinate(lat=-90, lon=-180),
            root_tile.min_coordinate,
        )
        self.assertEqual(
            Wgs84Coordinate(lat=90, lon=180),
            root_tile.max_coordinate,
        )

        self.assertEqual(
            (Wgs84Coordinate(lat=90, lon=-180), Wgs84Coordinate(lat=0, lon=0)),
            Wgs84TileInfo(zoom=1, x=0, y=0).bounds,
        )
        self.assertEqual(
            (Wgs84Coordinate(lat=0, lon=-180), Wgs84Coordinate(lat=-90, lon=0)),
            Wgs84TileInfo(zoom=1, x=0, y=1).bounds,
        )
        self.assertEqual(
            (Wgs84Coordinate(lat=90, lon=0), Wgs84Coordinate(lat=0, lon=180)),
            Wgs84TileInfo(zoom=1, x=1, y=0).bounds,
        )
        self.assertEqual(
            (Wgs84Coordinate(lat=0, lon=0), Wgs84Coordinate(lat=-90, lon=180)),
            Wgs84TileInfo(zoom=1, x=1, y=1).bounds,
        )

    def test_children(self) -> None:
        self.assertSetEqual(
            Wgs84TileInfo(x=0, y=0, zoom=0).children,
            {
                Wgs84TileInfo(x=0, y=0, zoom=1),
                Wgs84TileInfo(x=0, y=1, zoom=1),
                Wgs84TileInfo(x=1, y=0, zoom=1),
                Wgs84TileInfo(x=1, y=1, zoom=1),
            },
        )

        self.assertSetEqual(
            Wgs84TileInfo(zoom=6, x=33, y=22).children,
            {
                Wgs84TileInfo(zoom=7, x=66, y=44),
                Wgs84TileInfo(zoom=7, x=67, y=44),
                Wgs84TileInfo(zoom=7, x=66, y=45),
                Wgs84TileInfo(zoom=7, x=67, y=45),
            },
        )

    def test_descendants(self) -> None:
        root = Wgs84TileInfo(x=0, y=0, zoom=0)
        self.assertSetEqual(set(root.descendants(max_zoom=0)), {root})
        self.assertSetEqual(
            set(root.descendants(max_zoom=1)), {root}.union(root.children)
        )

    def test_ancestors(self) -> None:
        switzerland = Wgs84TileInfo(zoom=6, x=33, y=22)
        self.assertEqual(Wgs84TileInfo(zoom=5, x=16, y=11), switzerland.parent)
        ancestors = set(switzerland.ancestors())
        self.assertEqual(len(ancestors), 7)

    def test_path(self) -> None:
        self.assertEqual(Wgs84TileInfo(zoom=3, x=2, y=1).path, "3/2/1")
