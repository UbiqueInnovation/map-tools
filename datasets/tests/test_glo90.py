from unittest import TestCase

from datasets import Glo90


class TestGlo30(TestCase):
    def test_get_urls(self) -> None:
        layer = Glo90()
        self.assertEqual(len(list(layer.get_urls())), 26_475)
