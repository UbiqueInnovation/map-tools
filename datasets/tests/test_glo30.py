from unittest import TestCase

from datasets import Glo30


class TestGlo30(TestCase):
    def test_get_urls(self) -> None:
        layer = Glo30()
        self.assertEqual(len(list(layer.get_urls())), 26_450)
