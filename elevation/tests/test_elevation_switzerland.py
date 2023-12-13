from unittest import TestCase

from elevation import SwissAlti3d


class TestElevationSwitzerland(TestCase):
    def test_get_urls(self) -> None:
        layer = SwissAlti3d()
        self.assertEqual(len(list(layer.get_urls())), 43_590)
