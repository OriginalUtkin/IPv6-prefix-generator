import attr

from Common.Trie.Node.Node import Node
from V6Gene.Generator.Helper import Helper
from Common.Exceptions.Exceptions import PrefixAlreadyExists, MaximumLevelException
from Common.Abstract.AbstractTrie import AbstractTrie

from typing import Dict, List, Optional


@attr.s
class Trie(AbstractTrie):
    _level_distribution = attr.ib(factory=dict, type=dict)

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
    def init_max_level(self):

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

        path = []
        path_from_parent_node = list()

        if not creating_phase and AbstractTrie.is_exist(current_node, node_value):
            raise PrefixAlreadyExists

        for curr_len, bit in enumerate(node_value, 1):

            if bit == '0':

                if not current_node.left_child:
                    current_node.left_child = Node(bit, current_node.depth + 1)

                if current_node.prefix_flag:
                    path.append(current_node)

                if not creating_phase:
                    path_from_parent_node.append(current_node)

                current_node = current_node.left_child

            else:

                if not current_node.right_child:
                    current_node.right_child = Node(bit, current_node.depth + 1)

                if current_node.prefix_flag:
                    path.append(current_node)

                if not creating_phase:
                    path_from_parent_node.append(current_node)

                current_node = current_node.right_child

        if path:
            current_node.path = path[-1]

        full_prefix_path = AbstractTrie.get_full_path(current_node, include_current=True)

        if len(full_prefix_path) - 1 > full_prefix_path[0].level:
            if len(full_prefix_path) > self.max_possible_level and not creating_phase:
                AbstractTrie.delete_node_from_trie(path_from_parent_node)
                raise MaximumLevelException

            for prefix_index in range(len(full_prefix_path)):
                full_prefix_path[prefix_index].level = len(full_prefix_path) - 1 - prefix_index

        if self._max_trie_level < len(full_prefix_path) - 1:
            self._max_trie_level = len(full_prefix_path) - 1
            print(self._max_trie_level)

        current_node.prefix_flag = True
        self._prefix_nodes[current_node.depth] += 1

        current_node.generated = creating_phase

        if not creating_phase:
            current_node.allow_generate = creating_phase

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

            if not node.left_child and not node.right_child and node.prefix_flag:  # We found a leaf node

                if action is "statistic":

                    if not self._prefix_leaf_nodes.get(node.depth):
                        self._prefix_leaf_nodes[node.depth] = 1

                    else:
                        self._prefix_leaf_nodes[node.depth] += 1

                if action is "generate" and node.allow_generate:
                    self._generate_prefix(node)

            self.preorder(node.left_child, action)
            self.preorder(node.right_child, action)

    def _generate_prefix(self, node: Node):
        # We have current node depth. Investigate which organisation level is is.
        # After that, check next level and take some prefix from it.
        prefix_depth_level = self.Help.get_organisation_level_by_depth(node.depth)

        # Cannot generate from prefix which has len as 64
        if prefix_depth_level == self.Help.max_organisation_depth():
            return None

        # No prefixes on following depth level
        if not self.Help.get_dd_plan(prefix_depth_level + 1):
            return None

        # find out, how many prefixes could be generated from current node
        number_of_prefixes_from_this_node = self.Help.get_gs(prefix_depth_level)

        for _ in range(number_of_prefixes_from_this_node):

            # get prefixes length from next organisation depth level which could be generated from current level
            generated_info_keys = self.Help.get_plan_keys(prefix_depth_level + 1)

            # No prefixes
            if not generated_info_keys:
                return None

            prefix_depth = generated_info_keys[0]

            # get number of prefixes
            values = self.Help.get_plan_values(prefix_depth_level+1, prefix_depth)

            while True:
                try:
                    new_bits = Helper.generate_new_bits(node.depth, prefix_depth)
                    self.add_node(new_bits, node, False)
                    break

                except (PrefixAlreadyExists, MaximumLevelException):
                    continue

            # generate prefix and decrease number of prefixes which should be generated by one
            if values - 1 == 0:
                self.Help.remove_from_plan(prefix_depth_level+1, prefix_depth)

            else:
                self.Help.decrease_plan_value(prefix_depth_level+1, prefix_depth)