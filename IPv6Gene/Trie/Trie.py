import attr
import random

from Abstract.Node import Node
from Abstract.AbstractHelper import AbstractHelper
from Abstract.AbstractTrie import AbstractTrie
from IPv6Gene.Generator.Helper import Helper
from Exceptions.Exceptions import PrefixAlreadyExists, MaximumLevelException, CannotGenerateDueMaximumLevel

from typing import Optional


@attr.s
class Trie(AbstractTrie):
    """
    Class that represents binary trie for improved version of generator
    """
    Help = attr.ib(default=None, type=Helper)
    tmp_var = 0
    nodes = {
        0: [], 1: [], 2: [], 3: [],
    }

    def __attrs_post_init__(self) -> None:
        for value in range(65):
            self._prefix_nodes[value] = 0
            self._prefix_leaf_nodes[value] = 0

    def add_node(self, node_value: str, parent_node: Optional[Node] = None, creating_phase: bool = True) -> Node:
        """Add new node to binary trie.

        :exception  PrefixAlreadyExists in case if new node already exists in binary trie. Method isn't called in
                    creating phase
        :exception  MaximumLevelException in case if after adding a new node to binary trie level changes and greater than max possible value

        :param node_value: string; string representation of node
        :param parent_node None or Node; node object which represent the parent for added node
        :param creating_phase boolean; signalize phase of generator when node is added while binary trie is initializing
        :return: None
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

        if current_node.depth > self._trie_depth:
            self._trie_depth = current_node.depth

        org_level = self.Help.get_organisation_level_by_depth(current_node.depth)

        if not org_level and creating_phase:
            return current_node

        self.nodes[org_level].append(current_node)

        return current_node

    def generate_prefixes(self) -> None:
        """Generate new prefixes.

        1)Going through distribution plan which was created in initialization phase and get single organisation level.

        2)Try to generate prefixes to the following organisation level.

        3)If generating isn't possible from the currently selected node due to :exception MaximumLevelException, this
        node will be added to set of already used nodes.

        4)In case that all nodes were used and generating process from all of them isn't possible due to :exception
        MaximumLevelException, end script with the following error message.

        5) Otherwise, append new node to the particular organisation level in nodes variable and allow generating from
        it.

        If last organisation level is selected (EU), lists with LIR and ISP nodes are used for generating.

        If :exception PrefixAlreadyExist is occured, generator try generate new node

        :return: None
        """

        for plan_entry in self.Help.distribution_plan:
            print(f"[GENERATING PROCESS]: Currently prefixes is being generated on interval:{plan_entry.get('interval')}")

            used_nodes = set()

            if len(plan_entry["generated_info"]) == 0:
                continue

            while plan_entry["generated_info"]:
                while True:

                    new_prefix_len = list(plan_entry["generated_info"].keys())[0]

                    org_level = self.Help.get_organisation_level_by_depth(new_prefix_len) - 1

                    if org_level + 1 == 3:
                        self.nodes[2] += self.nodes[1]

                    node_index = random.randint(0, len(self.nodes[org_level]) - 1)

                    try:

                        new_bits = AbstractHelper.generate_new_bits(self.nodes[org_level][node_index].depth, new_prefix_len)
                        self.add_node(new_bits, parent_node=self.nodes[org_level][node_index], creating_phase=False)
                        used_nodes.clear()
                        break

                    except PrefixAlreadyExists:
                        continue

                    except MaximumLevelException:

                        used_nodes.add(node_index)

                        if len(used_nodes) == len(self.nodes[org_level]):
                            raise CannotGenerateDueMaximumLevel("Cannot generate prefix from any prefix in trie "
                                                                "(level always is great than maximum possible level)")

                        continue

                # decide if organisation level should be removed from distributing plan
                if plan_entry["generated_info"][new_prefix_len] - 1 == 0:
                    del self.Help.distribution_plan[org_level+1]["generated_info"][new_prefix_len]

                else:
                    curr_values = self.Help.distribution_plan[org_level+1]["generated_info"][new_prefix_len]
                    self.Help.distribution_plan[org_level + 1]["generated_info"][new_prefix_len] = curr_values - 1
