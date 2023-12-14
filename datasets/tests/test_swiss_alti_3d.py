from unittest import TestCase

from datasets import SwissAlti3d


class TestSwissAlti3d(TestCase):
    def test_get_urls(self) -> None:
        layer = SwissAlti3d()
        self.assertEqual(len(list(layer.get_urls())), 43_590)
