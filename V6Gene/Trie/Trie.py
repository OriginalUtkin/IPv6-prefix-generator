import attr
import random

from V6Gene.Trie.Node import Node
from typing import Union, Dict, List


@attr.s
class Trie:

    root_node = attr.ib(default=Node(None, 0), type=Node)
    _generated_prefixes = attr.ib(factory=list, type=list)
    _trie_depth = attr.ib(default=0, type=int)
    _prefix_leaf_nodes = attr.ib(factory=dict, type=dict)
    _prefix_nodes = attr.ib(factory=dict, type=dict)

    distribution_plan = attr.ib(factory=dict, type=dict)

    _intervals = {0: [11, 31], 1: [31, 47], 2: [47, 63], 3: [63, 64]}

    def __attrs_post_init__(self):
        for value in range(64):
            self._prefix_nodes[value] = 0
            self._prefix_leaf_nodes[value] = 0

    @property
    def generated_prefixes(self) -> List:
        """Return all generated prefixes.

        :return: list; list which contains all generated prefixes
        """
        return self._generated_prefixes

    @property
    def trie_depth(self) -> int:
        """Return trie depth.

        :return: int; trie depth
        """
        return self._trie_depth

    @property
    def prefix_leaf_nodes(self) -> Dict:
        """Return all leaf prefixes.
        For set this parameter call a preorder method with :param action as 'statistic'

        :return: dictionary; dict in format {depth: num. leaf node prefixes}
        """
        return self._prefix_leaf_nodes

    @property
    def prefix_nodes(self) -> Dict:
        """Return all prefix nodes by level.
        Automatically updated when new node are added into trie. Return depth values where num. of prefix nodes are
        greater than zero

        :return: dictionary; dict in format {depth: num. prefixes nodes}
        """
        return {key: value for key, value in self._prefix_nodes.items() if value > 0}

    @property
    def full_prefix_nodes(self):
        return self._prefix_nodes

    def set_root_as_prefix(self) -> None:
        """Set prefix flag for root node.

        :return: None
        """
        self.root_node.prefix_flag = True
        self._prefix_nodes[0] += 1

    def add_node(self, node_value: str, parent_node: Union[None, Node] = None, allow_generating: bool = True) -> None:
        """

        :param node_value: string; string representation of node
        :param parent_node None or Node; node object which represent the parent for added node
        :param allow_generating boolean; allow generating new nodes from added node
        :return: None
        """
        if not parent_node:
            current_node = self.root_node
        else:
            current_node = parent_node

        for bit in node_value:

            if bit == '0':

                # add node to trie as a left child
                if not current_node.left_child:
                    current_node.left_child = Node(bit, current_node.depth + 1)

                current_node = current_node.left_child

            else:

                # add node to trie as a right child
                if not current_node.right_child:
                    current_node.right_child = Node(bit, current_node.depth + 1)

                current_node = current_node.right_child

        # Added node is a prefix node
        current_node.prefix_flag = True
        self._prefix_nodes[current_node.depth] += 1

        if not allow_generating:
            current_node.allow_generate = allow_generating

        # Set a trie depth
        if current_node.depth > self._trie_depth:
            self._trie_depth = current_node.depth

    def _get_organisation_depth_level(self, prefix_depth: int):
        for i in range(len(self._intervals)):
            if self._intervals[i][0] <= prefix_depth < self._intervals[i][1]:
                return i


    def preorder(self, node: Node, action: str) -> None:

        if node:
            # print(node.node_value)

            if node and not node.left_child and not node.right_child and node.prefix_flag:  # We found a leaf node

                if action is "statistic":

                    if not self._prefix_leaf_nodes.get(node.depth):
                        self._prefix_leaf_nodes[node.depth] = 1

                    else:
                        self._prefix_leaf_nodes[node.depth] += 1

                if action is "generate" and node.allow_generate:
                    self._generate_prefix(node)

            self.preorder(node.left_child, action)
            self.preorder(node.right_child, action)

    # TODO: refactor
    def get_depths(self, level):
        return [key for key in self._prefix_leaf_nodes.keys() if key < level]

    def _generate_new_bits(self, current_prefix_depth: int, new_prefix_depth: int) -> str:
        """

        :param current_prefix_depth:
        :param new_prefix_depth:
        :return:
        """
        generate_num = new_prefix_depth - current_prefix_depth

        generated_sequence = random.getrandbits(generate_num)

        binary_rep = ("{0:b}".format(generated_sequence))

        if len(binary_rep) < generate_num:
            additional_bits = generate_num - len(binary_rep)

            for i in range(additional_bits):
                binary_rep = '0' + binary_rep

        return binary_rep

    def _generate_prefix(self, node: Node):
        """

        :param node:
        :return:
        """

        # We have current node depth. Investigate which organisation level is is.
        # After that, check next level and take some prefix from it.
        prefix_depth_level = self._get_organisation_depth_level(node.depth)

        # get prefixes length from next organisation depth level which could be generated from current level
        generated_info_keys = list(self.distribution_plan[prefix_depth_level + 1]['generated_info'].keys())

        print(node.name, node.node_value)

        # No prefixes on following level
        if not generated_info_keys:
            return None

        for new_depth in generated_info_keys:
                new_prefixes_num = self.distribution_plan[prefix_depth_level + 1]['generated_info'][new_depth]
                for _ in range(new_prefixes_num):
                    new_bits = self._generate_new_bits(node.depth, new_depth)
                    new_prefixes_counter = self.distribution_plan[prefix_depth_level + 1]['generated_info'][new_depth]

                    # No new prefixes are needed on particular depth -> pop this depth
                    if new_prefixes_counter - 1 == 0:
                        self.distribution_plan[prefix_depth_level + 1]['generated_info'].pop(new_depth)

                    else:
                        self.distribution_plan[prefix_depth_level + 1]['generated_info'][new_depth] = new_prefixes_counter - 1

                    self.add_node(new_bits, node, False)
