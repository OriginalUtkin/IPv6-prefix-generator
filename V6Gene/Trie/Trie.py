import attr

from V6Gene.Trie.Node import Node
from V6Gene.Generator.Helper import Helper

from typing import Union, Dict, List


@attr.s
class Trie:
    root_node = attr.ib(default=Node(None, 0), type=Node)
    max_possible_level = attr.ib(default=7, type=int)

    _max_trie_level = attr.ib(default=0, type=int)
    _generated_prefixes = attr.ib(factory=list, type=list)
    _trie_depth = attr.ib(default=0, type=int)
    _prefix_leaf_nodes = attr.ib(factory=dict, type=dict)
    _prefix_nodes = attr.ib(factory=dict, type=dict)
    _level_distribution = attr.ib(factory=dict, type=dict)

    Help = attr.ib(default=None, type=Helper)

    names = ['A', 'B','C','D','E','F','G','H', 'K', 'L', 'M', 'N']
    added=0

    def __attrs_post_init__(self):
        for value in range(64):
            self._prefix_nodes[value] = 0
            self._prefix_leaf_nodes[value] = 0

        for value in range(6):
            self._level_distribution[value] = 0

    @property
    def trie_level(self):
        return self._max_trie_level

    @property
    def level_distribution(self):
        return self._level_distribution

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

    def add_node(self, node_value: str, parent_node: Union[None, Node] = None, allow_generating: bool = True) -> Node:
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
        path = []

        for bit in node_value:

            if current_node.level > self._max_trie_level:
                self._max_trie_level = current_node.level

            if bit == '0':

                # add node to trie as a left child
                if not current_node.left_child:
                    current_node.left_child = Node(bit, current_node.depth + 1)

                if current_node.prefix_flag:
                    path.append(current_node)

                current_node = current_node.left_child

            else:

                # add node to trie as a right child
                if not current_node.right_child:
                    current_node.right_child = Node(bit, current_node.depth + 1)

                if current_node.prefix_flag:
                    path.append(current_node)

                current_node = current_node.right_child

        if path:
            self.recalculate_level(path)

        current_node.prefix_flag = True
        self._prefix_nodes[current_node.depth] += 1

        if not allow_generating:
            current_node.allow_generate = allow_generating

        if current_node.depth > self._trie_depth:
            self._trie_depth = current_node.depth

        return current_node

    def preorder(self, node: Node, action: str) -> None:

        if node:

            if action is "statistic" and node.prefix_flag:

                if not self._level_distribution.get(node.level):
                    self._level_distribution[node.level] = 1

                else:
                    self._level_distribution[node.level] += 1

            if node.left_child and not node.right_child and node.prefix_flag:  # We found a leaf node

                if action is "statistic":

                    if not self._prefix_leaf_nodes.get(node.depth):
                        self._prefix_leaf_nodes[node.depth] = 1

                    else:
                        self._prefix_leaf_nodes[node.depth] += 1

                    node.name = self.names[self.added]
                    self.added += 1

                if action is "generate" and node.allow_generate:
                    self._generate_prefix(node)

            self.preorder(node.left_child, action)
            self.preorder(node.right_child, action)

    # TODO: refactor
    def get_depths(self, level):
        return [key for key in self._prefix_leaf_nodes.keys() if key < level]

    def _generate_prefix(self, node: Node):
        # We have current node depth. Investigate which organisation level is is.
        # After that, check next level and take some prefix from it.
        prefix_depth_level = self.Help.get_organisation_level_by_depth(node.depth)

        # Cannot generate from prefix which has len as 64
        if prefix_depth_level == self.Help.max_organisation_depth():
            print(f"Node has len as 64. Skip {prefix_depth_level}")
            return None

        # No prefixes on following depth level
        if not self.Help.get_dd_plan(prefix_depth_level + 1):
            print(f"Skip depth {prefix_depth_level}")
            return None

        # find out, how many prefixes could be generated from current node
        number_of_prefixes_from_this_node = self.Help.get_gs(prefix_depth_level)
        print(f"Start generate from node {node.name} with {node.depth}. Will be generated {number_of_prefixes_from_this_node} prefix")

        for _ in range(number_of_prefixes_from_this_node):

            # get prefixes length from next organisation depth level which could be generated from current level
            generated_info_keys = self.Help.get_plan_keys(prefix_depth_level + 1)

            # No prefixes
            if not generated_info_keys:
                return None

            prefix_depth = generated_info_keys[0]
            print(f"New prefix will have depth is {prefix_depth}")

            # get number of prefixes
            values = self.Help.get_plan_values(prefix_depth_level+1, prefix_depth)
            new_bits = Helper.generate_new_bits(node.depth, prefix_depth)

            # generate prefix and decrease number of prefixes which should be generated by one
            if values - 1 == 0:
                print(f"!!!!Generate prefix and pop level {prefix_depth}!!!!")
                self.Help.remove_from_plan(prefix_depth_level+1, prefix_depth)

            else:
                print(f"!!!!JUST Generate prefix!!!!!")
                self.Help.decrease_plan_value(prefix_depth_level+1, prefix_depth)

            self.add_node(new_bits, node, False)

    def recalculate_level(self, path: List):

        for i in range(len(path)-1, -1, -1):

            # adding new child to leaf
            if i == len(path) - 1:
                if path[i].level == 0:
                    path[i].level = 1

                else:
                    continue

            # adding new child to node, which already has child
            else:
                if path[i].level < path[i + 1].level + 1:
                    path[i].level += 1
