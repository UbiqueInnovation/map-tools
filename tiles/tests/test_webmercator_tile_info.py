from unittest import TestCase

from tiles import WebmercatorTileInfo


class TestWebmercatorTileInfo(TestCase):
    def assertTupleAlmostEqual(
        self, first: tuple, second: tuple, places=None, msg=None, delta=None
    ):
        self.assertAlmostEqual(len(first), len(second))
        for a, b in zip(first, second):
            self.assertAlmostEqual(a, b, places, msg, delta)

    def test_size(self) -> None:
        self.assertTupleAlmostEqual(
            WebmercatorTileInfo(zoom=6, x=33, y=22).size, (626_172, 626_172), delta=0.5
        )

    def test_bounds(self) -> None:
        self.assertTupleAlmostEqual(
            WebmercatorTileInfo(zoom=0, x=0, y=0).min_coordinate,
            (-20_037_508, -20_037_508),
            delta=0.5,
        )
        self.assertTupleAlmostEqual(
            WebmercatorTileInfo(zoom=6, x=33, y=22).min_coordinate,
            (626172, 5635549),
            delta=0.5,
        )
        self.assertTupleAlmostEqual(
            WebmercatorTileInfo(zoom=6, x=33, y=22).max_coordinate,
            (1252344, 6261721),
            delta=0.5,
        )
        self.assertTupleAlmostEqual(
            WebmercatorTileInfo(zoom=10, x=536, y=358).min_coordinate,
            (939258, 5987771),
            delta=0.5,
        )
        self.assertTupleAlmostEqual(
            WebmercatorTileInfo(zoom=10, x=536, y=358).max_coordinate,
            (978394, 6026907),
            delta=0.5,
        )

    def test_corners(self) -> None:
        self.assertTupleAlmostEqual(
            WebmercatorTileInfo(zoom=0, x=0, y=0).top_left,
            (-20_037_508, 20_037_508),
            delta=0.5,
        )

        self.assertTupleAlmostEqual(
            WebmercatorTileInfo(zoom=0, x=0, y=0).bottom_right,
            (20_037_508, -20_037_508),
            delta=0.5,
        )
        self.assertTupleEqual(
            WebmercatorTileInfo(zoom=6, x=33, y=22).top_left,
            WebmercatorTileInfo(zoom=7, x=66, y=44).top_left,
        )

    def test_children(self) -> None:
        self.assertSetEqual(
            WebmercatorTileInfo(x=0, y=0, zoom=0).children,
            {
                WebmercatorTileInfo(x=0, y=0, zoom=1),
                WebmercatorTileInfo(x=0, y=1, zoom=1),
                WebmercatorTileInfo(x=1, y=0, zoom=1),
                WebmercatorTileInfo(x=1, y=1, zoom=1),
            },
        )

        self.assertSetEqual(
            WebmercatorTileInfo(zoom=6, x=33, y=22).children,
            {
                WebmercatorTileInfo(zoom=7, x=66, y=44),
                WebmercatorTileInfo(zoom=7, x=67, y=44),
                WebmercatorTileInfo(zoom=7, x=66, y=45),
                WebmercatorTileInfo(zoom=7, x=67, y=45),
            },
        )

    def test_descendants(self) -> None:
        root = WebmercatorTileInfo(x=0, y=0, zoom=0)
        self.assertSetEqual(set(root.descendants(max_zoom=0)), {root})
        self.assertSetEqual(
            set(root.descendants(max_zoom=1)), {root}.union(root.children)
        )

    def test_path(self) -> None:
        self.assertEqual(WebmercatorTileInfo(zoom=3, x=2, y=1).path, "3/2/1")
