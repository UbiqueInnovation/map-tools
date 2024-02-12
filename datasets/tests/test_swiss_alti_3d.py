from unittest import TestCase

from datasets import SwissAlti3d


class TestSwissAlti3d(TestCase):
    def test_get_low_res_urls(self) -> None:
        layer = SwissAlti3d()
        self.assertEqual(len(list(layer.get_urls())), 43_628)

    def test_get_high_res_urls(self) -> None:
        layer = SwissAlti3d(high_res=True)
        self.assertEqual(len(list(layer.get_urls())), 43_628)
