import attr
import random

from IPv6Gene.Trie.Node import Node
from IPv6Gene.Generator.Helper import Helper
from IPv6Gene.Exceptions.Exceptions import PrefixAlreadyExists, MaximumLevelException, CannotGenerateDueMaximumLevel

from typing import Dict, List, Optional


@attr.s
class Trie:
    root_node = attr.ib(default=Node(None, 0), type=Node)
    max_possible_level = attr.ib(default=7, type=int)

    _max_trie_level = attr.ib(default=0, type=int)
    _generated_prefixes = attr.ib(factory=list, type=list)
    _trie_depth = attr.ib(default=0, type=int)
    _prefix_leaf_nodes = attr.ib(factory=dict, type=dict)
    _prefix_nodes = attr.ib(factory=dict, type=dict)

    Help = attr.ib(default=None, type=Helper)

    nodes = {
        0: [], 1: [], 2: [], 3: []
    }

    def __attrs_post_init__(self):
        for value in range(65):
            self._prefix_nodes[value] = 0
            self._prefix_leaf_nodes[value] = 0

    @property
    def trie_level(self):
        return self._max_trie_level

    @property
    def trie_depth(self) -> int:
        """Return trie depth.

        :return: int; trie depth
        """
        return self._trie_depth

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

    def calculate_maximum_trie_lvl(self):
        max_level = 0

        for _, nodes_list in self.nodes.items():
            for node in nodes_list:
                if node.level > max_level: max_level = node.level

        return max_level

    def add_node(self, node_value: str, parent_node: Optional[Node] = None, creating: bool = True) -> Node:
        """Add new node to binary trie.

        :exception  PrefixAlreadyExists in case if new node already exists in binary trie
        :exception  MaximumLevelException in case if after adding a new node to binary trie level changes and greater than max possible value

        :param node_value: string; string representation of node
        :param parent_node None or Node; node object which represent the parent for added node
        :param creating boolean; signalize phase of generator when node is added
        :return: None
        """
        if not parent_node:
            current_node = self.root_node
        else:
            current_node = parent_node

        path = []

        for curr_len, bit in enumerate(node_value, 1):

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
                if not creating:
                    self.recalculate_level(current_node.path, phase='Generating')

                else:
                    self.recalculate_level(current_node)

            except MaximumLevelException:
                raise

        current_node.prefix_flag = True
        self._prefix_nodes[current_node.depth] += 1

        if not creating:
            current_node.generated = creating

        if current_node.depth > self._trie_depth:
            self._trie_depth = current_node.depth

        org_level = self.Help.get_organisation_level_by_depth(current_node.depth)
        self.nodes[org_level].append(current_node)
        self._max_trie_level = self.calculate_maximum_trie_lvl()

        return current_node

    def get_depths(self, level):
        return [key for key in self._prefix_leaf_nodes.keys() if key < level]

    def generate_prefixes(self) -> None:
        """Generate all required prefixes.

        :return: None
        """
        for plan_entry in self.Help.distribution_plan:
            used_nodes = set()

            if len(plan_entry["generated_info"]) == 0:
                continue

            while plan_entry["generated_info"]:
                while True:
                    new_prefix_len = list(plan_entry["generated_info"].keys())[0]

                    print(f"Generaiting {new_prefix_len}")

                    org_level = self.Help.get_organisation_level_by_depth(new_prefix_len) - 1

                    if org_level + 1 == 3:
                        self.nodes[2] += self.nodes[1]

                    node_index = random.randint(0, len(self.nodes[org_level]) - 1)

                    try:

                        new_bits = self.Help.generate_new_bits(self.nodes[org_level][node_index].depth, new_prefix_len)
                        self.add_node(new_bits, parent_node=self.nodes[org_level][node_index], creating=False)
                        used_nodes.clear()

                        break

                    except PrefixAlreadyExists:
                        continue

                    except MaximumLevelException:
                        used_nodes.add(node_index)
                        print(len(used_nodes))

                        if len(used_nodes) == len(self.nodes[org_level]):
                            raise CannotGenerateDueMaximumLevel("Cannot generate prefix from any prefix in trie "
                                                                "(level always is great than maximum possible level)")

                        continue

                if plan_entry["generated_info"][new_prefix_len] - 1 == 0:
                    print("Generate and pop element")
                    del self.Help.distribution_plan[org_level+1]["generated_info"][new_prefix_len]

                else:
                    print("Generate and decrease number of elements")
                    curr_values = self.Help.distribution_plan[org_level+1]["generated_info"][new_prefix_len]
                    self.Help.distribution_plan[org_level + 1]["generated_info"][new_prefix_len] = curr_values - 1

    def get_full_path(self, node: Node, include_current=False) -> List:
        """Return full prefix nodes path for current node.

        Method is used for creating prefix path for current :param node and recalculate level for previous nodes.
        :param node: Node; node object from binary trie
        :param include_current: boolean; Signalize if current node will be added to full prefix nodes path.
        :return: list; list with all previous (and current if include flag is set as True) prefix nodes for :param node
        """
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
                full_path[-1].left_child = None
                full_path[-1].righ_child = None

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
