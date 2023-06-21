from unittest import TestCase

from elevation import ElevationSwitzerland


class TestElevationSwitzerland(TestCase):
    def test_get_urls(self) -> None:
        layer = ElevationSwitzerland()
        self.assertEqual(len(list(layer.get_urls())), 43_590)
