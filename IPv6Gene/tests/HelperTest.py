import V6Gene.main
import argparse
import unittest


class TrieTest(unittest.TestCase):

    def test_validate_prefix_quantity_negative(self):
        with self.assertRaises(argparse.ArgumentTypeError):
            V6Gene.main.validate_prefix_quantity(-1)

    def test_validate_prefix_quantity_not_number(self):
        with self.assertRaises(ValueError):
            V6Gene.main.validate_prefix_quantity("check it")

    def test_validate_rgr_negative(self):
        with self.assertRaises(argparse.ArgumentTypeError):
            V6Gene.main.validate_rgr(-1)

    def test_validate_rgr_greater(self):
        with self.assertRaises(argparse.ArgumentTypeError):
            V6Gene.main.validate_rgr(101)

    def test_validate_rgr_not_number(self):
        with self.assertRaises(ValueError):
            V6Gene.main.validate_rgr("check it")

    def test_validate_input_arguments_type(self):
        self.assertTrue(isinstance(V6Gene.main.validate_rgr(.2), float))
        self.assertEqual(V6Gene.main.validate_rgr(.2), 20)

        self.assertTrue(isinstance(V6Gene.main.validate_prefix_quantity(10), int))

    def test_binary_prefix(self):
        self.assertEqual(V6Gene.main.get_binary_prefix('2a03:b200::/29'), '00101010000000111011001000000')
