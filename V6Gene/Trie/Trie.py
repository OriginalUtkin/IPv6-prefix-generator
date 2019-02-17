import attr

from V6Gene.Trie.Node import Node
from V6Gene.Generator.Helper import Helper
from V6Gene.Exceptions.Exceptions import PrefixAlreadyExists, MaximumLevelException

from typing import Dict, List, Optional


@attr.s
class Trie:
    root_node = attr.ib(default=Node(None, 0), type=Node)
    max_possible_level = attr.ib(default=7, type=int)

    _init_max_level = attr.ib(default=0, type=int)
    _max_trie_level = attr.ib(default=0, type=int)
    _generated_prefixes = attr.ib(factory=list, type=list)
    _trie_depth = attr.ib(default=0, type=int)
    _prefix_leaf_nodes = attr.ib(factory=dict, type=dict)
    _prefix_nodes = attr.ib(factory=dict, type=dict)
    _level_distribution = attr.ib(factory=dict, type=dict)

    Help = attr.ib(default=None, type=Helper)

    def __attrs_post_init__(self):
        for value in range(65):
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

    @property
    def init_max_level(self):
        return max(self._level_distribution, key=int)

    def set_root_as_prefix(self) -> None:
        """Set prefix flag for root node.

        :return: None
        """
        self.root_node.prefix_flag = True
        self._prefix_nodes[0] += 1

    def add_node(self, node_value: str, parent_node: Optional[Node] = None, allow_generating: bool = True) -> Node:
        """Add new node to binary trie.

        :exception  PrefixAlreadyExists in case if new node already exists in binary trie
        :exception  MaximumLevelException in case if after adding a new node to binary trie level changes and greater than max possible value

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

        for curr_len, bit in enumerate(node_value, 1):

            if current_node.level > self._max_trie_level:
                self._max_trie_level = current_node.level

            if bit == '0':
                # add node to trie as a left child
                if curr_len == len(node_value) and current_node.left_child:
                    raise PrefixAlreadyExists("Value already exists in binary trie")

                if not current_node.left_child:
                    current_node.left_child = Node(bit, current_node.depth + 1)

                if current_node.prefix_flag:
                    path.append(current_node)

                current_node = current_node.left_child

            else:
                # add node to trie as a right child
                if curr_len == len(node_value) and current_node.right_child:
                    raise PrefixAlreadyExists("Value already exists in binary trie")

                if not current_node.right_child:
                    current_node.right_child = Node(bit, current_node.depth + 1)

                if current_node.prefix_flag:
                    path.append(current_node)

                current_node = current_node.right_child

        if path:
            current_node.path = path[-1]

            try:
                if not allow_generating:
                    self.recalculate_level(current_node.path, phase='Generating')

                else:
                    self.recalculate_level(current_node)

            except MaximumLevelException:
                # TODO: delete pointer to new child
                raise

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
        
            while True:
                try:
                    new_bits = Helper.generate_new_bits(node.depth, prefix_depth)
                    self.add_node(new_bits, node, False)
                    break

                except (PrefixAlreadyExists, MaximumLevelException):
                    continue

            # generate prefix and decrease number of prefixes which should be generated by one
            if values - 1 == 0:
                print(f"!!!!Generate prefix and pop level {prefix_depth}!!!!")
                self.Help.remove_from_plan(prefix_depth_level+1, prefix_depth)

            else:
                print(f"!!!!JUST Generate prefix!!!!!")
                self.Help.decrease_plan_value(prefix_depth_level+1, prefix_depth)

    def get_full_path(self, node: Node, include_current=False):
        full_path = []

        if include_current:
            full_path.append(node)

        curr = node.path

        while curr:
            full_path.append(curr)
            curr = curr.path

        return full_path[::-1]

    def recalculate_level(self, node: Node, phase='Creating'):
        """Recalculate level all parent and sub-parent prefixes after adding new leaf prefix to binary trie.
        Separated into two phases:
        1) Creating phase- means creating binary trie using seed prefix file. At this moment, no info about max possible
        level for trie. levels are calculated and automatically applied for all nodes in :param path

        2)Generating phase - trie has info about max possible level from input parameter level_distribution. In this
        case, all nodes levels are stored in temporary structure. At first, need to check if after adding new node to
        binary trie all prefixes in :param path structure have level less or equal to max_possible_level. If so, new
        node can be added to binary trie. Else function will raise exception

        :param node: Node; added node to trie
        :param phase: string; currently generator phase
        :return: None
        """

        if phase is 'Creating':
            full_path = self.get_full_path(node)
            print("Recalculating while creating")

            self.recalculating_process(full_path)

        if phase is 'Generating':
            full_path = self.get_full_path(node, include_current=True)
            print("Recalculating while generating")

            tmp_path = [i.level for i in full_path]
            self.recalculating_process_tmp(tmp_path)

            max_level = max(tmp_path, key=int)
            if max_level > self.max_possible_level:
                raise MaximumLevelException("Level after generate new prefix is greater than max possible trie level")

            self.recalculating_process(full_path)

    def recalculating_process(self, path):
        # TODO: change function logic for using it in generating phase
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

    def recalculating_process_tmp(self, path):
        # TODO: change function logic for using it in generating phase
        for i in range(len(path)-1, -1, -1):

            # adding new child to leaf
            if i == len(path) - 1:
                if path[i] == 0:
                    path[i] = 1

                else:
                    continue

            # adding new child to node, which already has child
            else:
                if path[i] < path[i + 1] + 1:
                    path[i] += 1

    def print_path(self, s):
        return ''.join([i.node_value for i in s if i.node_value])

    def path(self, node: Node):
        all_path = []
        if node is None:
            return

        s = []
        s.append(node)

        tmp = node.left_child

        while s:
            while tmp:
                s.append(tmp)
                tmp = tmp.left_child

            top = s[-1]
            if top.prefix_flag:
                all_path.append(self.print_path(s))

            if not top.is_visited:
                top.is_visited = True
                tmp = top.right_child

                if tmp is None and top.right_child is None and top.left_child is None:
                    all_path.append(self.print_path(s))
                    s.pop()
            else:
                s.pop()

        return all_path
