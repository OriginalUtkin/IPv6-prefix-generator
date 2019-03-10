from V6Gene.Trie import Trie
from V6Gene import get_binary_prefix
import unittest


class TrieTest(unittest.TestCase):

    def test_trie_depth(self):

        prefix = "2407:8800:1::/35"

        binary_trie = Trie.Trie()
        binary_trie.add_node(get_binary_prefix(prefix))

        self.assertEqual(binary_trie.trie_depth, 35)

        prefix = "2001:1234:5678:1234:5678:ABCD:EF12:1234/64"
        binary_trie.add_node(get_binary_prefix(prefix))

        self.assertEqual(binary_trie.trie_depth, 64)

    def test_trie_properties(self):

        binary_trie = Trie.Trie()

        # Add right part of binary trie
        binary_trie.add_node('11')
        binary_trie.add_node('1110')
        binary_trie.add_node('1111')
        binary_trie.add_node('110000')
        binary_trie.add_node('110001')

        # Add left part of binary trie
        binary_trie.add_node('0')
        binary_trie.add_node('001')
        binary_trie.add_node('010')
        binary_trie.add_node('011')

        # Number of prefix nodes
        self.assertEqual(binary_trie.prefix_nodes, 9)

        # Max depth of binary trie
        self.assertEqual(binary_trie.trie_depth, 6)
