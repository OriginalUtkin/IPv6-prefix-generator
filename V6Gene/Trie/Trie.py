import attr

from Common.Trie.Node.Node import Node
from V6Gene.Generator.Helper import Helper
from Common.Exceptions.Exceptions import PrefixAlreadyExists, MaximumLevelException
from Common.Abstract.AbstractTrie import AbstractTrie

from typing import Dict, List, Optional
from random import randint


@attr.s
class Trie(AbstractTrie):
    _level_distribution = attr.ib(factory=dict, type=dict)
    _trie_traversal_generated = attr.ib(default=0, type=int)
    _maximum_trie_traversal_generated = attr.ib(default=0, type=int)

    Help = attr.ib(default=None, type=Helper)

    def __attrs_post_init__(self):
        for value in range(65):
            self._prefix_nodes[value] = 0
            self._prefix_leaf_nodes[value] = 0

        for value in range(6):
            self._level_distribution[value] = 0

    @property
    def level_distribution(self) -> int:
        return self._level_distribution

    @property
    def generated_prefixes(self) -> List:
        """Return all generated prefixes.

        :return: list; list which contains all generated prefixes
        """
        return self._generated_prefixes

    @property
    def prefix_leaf_nodes(self) -> Dict:
        """Return all leaf prefixes.
        For set this parameter call a preorder method with :param action as 'statistic'

        :return: dictionary; dict in format {depth: num. leaf node prefixes}
        """
        return self._prefix_leaf_nodes

    @property
    def init_max_level(self) -> int:

        max_level = 0

        for key in self._level_distribution.keys():
            if self._level_distribution[key] != 0 and key > max_level:
                max_level = key

        return max_level

    def set_root_as_prefix(self) -> None:
        """Set prefix flag for root node.

        :return: None
        """
        self.root_node.prefix_flag = True
        self._prefix_nodes[0] += 1

    def add_node(self, node_value: str, parent_node: Optional[Node] = None, creating_phase: bool = True) -> Node:
        """Add new node to binary trie.

        :raises  PrefixAlreadyExists in case if new node already exists in binary trie. Method isn't called in
                    creating phase
        :raises  MaximumLevelException in case if after adding a new node to binary trie level changes and greater than max possible value

        :param node_value: string; string representation of node
        :param parent_node None or Node; node object which represent the parent for added node
        :param creating_phase boolean; signalize phase of generator when node is added while binary trie is initializing

        :return: constructed node object
        """
        if not parent_node:
            current_node = self.root_node
        else:
            current_node = parent_node

        if not creating_phase and AbstractTrie.is_exist(current_node, node_value):
            raise PrefixAlreadyExists

        for curr_len, bit in enumerate(node_value, 1):

            if bit == '0':

                if not current_node.left_child:
                    current_node.left_child = Node(bit, current_node.depth + 1)
                    current_node.left_child.path = current_node

                current_node = current_node.left_child

            else:

                if not current_node.right_child:
                    current_node.right_child = Node(bit, current_node.depth + 1)
                    current_node.right_child.path = current_node

                current_node = current_node.right_child

        try:
            self.calculate_level(current_node)

        except MaximumLevelException:

            if not current_node.right_child and not current_node.left_child:
                AbstractTrie.delete_node_from_trie(current_node)

            raise

        current_node.prefix_flag = True
        self._prefix_nodes[current_node.depth] += 1

        if not creating_phase:
            current_node.allow_generate = False

        if current_node.depth > self._trie_depth:
            self._trie_depth = current_node.depth

        return current_node

    def trie_traversal(self, action: str) -> None:
        """Traversal binary trie and run particular action if leaf node is found

        :param action: name of action which should be start
        :return: None
        """

        if not self.root_node:
            return

        node_path = list()
        node_path.append(self.root_node)

        while node_path:

            node = node_path.pop()

            if node.right_child:
                node_path.append(node.right_child)

            if node.left_child:
                node_path.append(node.left_child)

            if not node.left_child and not node.right_child:
                if action == 'statistic':
                    self.prefix_leaf_nodes[node.depth] += 1
                else:
                    self.generate_prefixes(node)

    def generate_prefixes(self, node: Node) -> None:
        """Generate new prefixes from selected node :param node
        We have current node depth. Investigate which organisation level it is.
        After that, check next level and take some prefix from it.
        :param node: selected node which will be used for generating new prefix nodes
        :return: None
        """

        prefix_depth_level = self.Help.get_organisation_level_by_depth(node.depth)

        # selected prefix has a length 64. This prefix cannot generate any other
        if prefix_depth_level == 4:
            return

        used_strategy = self.Help.generating_strategy[prefix_depth_level]['generating_strategy'][0]

        while used_strategy > 0:

            if self._trie_traversal_generated == self._maximum_trie_traversal_generated:
                break

            all_keys = list(self.Help.distribution_plan[prefix_depth_level + 1]['generated_info'].keys())
            new_prefix_depth = list(self.Help.distribution_plan[prefix_depth_level + 1]['generated_info'].keys())[randint(0, len(all_keys) - 1)]

            number_of_generated_prefixes = self.Help.get_plan_values(prefix_depth_level + 1, new_prefix_depth)

            try:
                new_bits = Helper.generate_new_bits(node.depth, new_prefix_depth)
                self.add_node(new_bits, node, False)

                if number_of_generated_prefixes - 1 == 0:
                    self.Help.remove_from_plan(prefix_depth_level + 1, new_prefix_depth)

                else:
                    self.Help.decrease_plan_value(prefix_depth_level + 1, new_prefix_depth)

                used_strategy -= 1
                self._trie_traversal_generated += 1

            except (PrefixAlreadyExists, MaximumLevelException):
                self._trie_traversal_generated += 1
                used_strategy -= 1
                continue
