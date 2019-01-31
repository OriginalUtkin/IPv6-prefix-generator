from V6Gene.Trie.Node import Node
import random
import attr
from typing import Union, Dict, List


@attr.s
class Trie:

    root_node = attr.ib(default=Node(None, 0), type=Node)
    _generated_prefixes = attr.ib(factory=list, type=list)
    _trie_depth = attr.ib(default=0, type=int)
    _prefix_leaf_nodes = attr.ib(factory=dict, type=dict)
    _prefix_nodes = attr.ib(factory=dict, type=dict)

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

    def add_node(self, node_value: str, parent_node: Union[None, Node] = None) -> None:
        """

        :param node_value: string; string representation of node
        :param parent_node None or Node; node object which represent the parent for added node
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

        # Set a trie depth
        if current_node.depth > self._trie_depth:
            self._trie_depth = current_node.depth

    def preorder(self, node: Node, action: str) -> None:

        if node:
            # print(node.node_value)

            if node and not node.left_child and not node.right_child and node.prefix_flag:  # We found a leaf node

                if action is "statistic":
                    if not self._prefix_leaf_nodes.get(node.depth):
                        self._prefix_leaf_nodes[node.depth] = 1

                    else:
                        self._prefix_leaf_nodes[node.depth] += 1

                if action is "generate":
                    self._generate_prefix(node)

            self.preorder(node.left_child, action)
            self.preorder(node.right_child, action)


    # TODO: refactor
    def get_depths(self, level):
        return [key for key in self._prefix_leaf_nodes.keys() if key < level]

    # TODO: Just for testing propose. Simulate generating a prefixes with other rules
    def _generate_prefix_tmp(self, node):
        pass



    def _generate_prefix(self, node: Node) -> None:
        """

        :param node:
        :return:
        """

        # Allocation of IPv6 address space rules: RIR to LIR, LIR to ISP, ISP to EU
        allocation_rules = {'RIR': [[12, 31], 20], 'LIR': [[32, 47], 16], 'ISP': [[48, 63], 16]}  # TODO: don't generate for other levels except RIR to LIR

        print(f'Generator function start')

        for key, value in allocation_rules.items():
            if value[0][0] <= node.depth <= value[0][1]:
                # specified number of bits which will be generated for current prefix depends on depth of node
                generate_num = value[1] - (node.depth - value[0][0])
                generated_sequence = random.getrandbits(generate_num)
                binary_repr = format(generated_sequence, '0' + str(generated_sequence) + 'b')
                self.add_node(binary_repr, node)
            else:
                continue
