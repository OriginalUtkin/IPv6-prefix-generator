import attr
import random

from Common.Trie.Node.Node import Node
from Common.Abstract.AbstractHelper import AbstractHelper
from Common.Abstract.AbstractTrie import AbstractTrie
from IPv6Gene.Generator.Helper import Helper
from Common.Exceptions.Exceptions import PrefixAlreadyExists, MaximumLevelException, CannotGenerateDueMaximumLevel

from typing import Optional


@attr.s
class Trie(AbstractTrie):
    """
    Class that represents binary trie for improved version of generator
    """
    Help = attr.ib(default=None, type=Helper)
    nodes = {
        1: [], 2: [], 3: [], 4: [],
    }

    def __attrs_post_init__(self) -> None:
        for value in range(65):
            self._prefix_nodes[value] = 0
            self._prefix_leaf_nodes[value] = 0

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

        current_node.generated = not creating_phase

        if current_node.depth > self._trie_depth:
            self._trie_depth = current_node.depth

        org_level = self.Help.get_organisation_level_by_depth(current_node.depth)

        if org_level == 0 and creating_phase:
            return current_node

        self.nodes[org_level].append(current_node)

        return current_node

    def generate_prefixes(self, node: Node = None) -> None:
        """Generate new prefixes using constructed binary trie.

        1)Going through distribution plan which was created in initialization phase and get single organisation level.

        2)Try to generate prefixes to the following organisation level.

        3)If generating isn't possible from the currently selected node due to :exception MaximumLevelException, this
        node will be added to set of already used nodes.

        4)In case that all nodes were used and generating process from all of them isn't possible due to :exception
        MaximumLevelException, end script with the error message.

        5) Otherwise, append new node to the particular organisation level in nodes variable and allow generating from
        it.

        If last organisation level is selected (EU), lists with LIR and ISP nodes are used for generating.

        If :exception PrefixAlreadyExist is occured, generator try generate new node

        :return: None
        """

        for plan_entry in self.Help.distribution_plan:

            used_nodes = set()
            parent_node_level = self.Help.get_organisation_level_by_depth(plan_entry['interval'][0]) - 1

            if parent_node_level == 3:
                self.nodes[3] += self.nodes[2]

            if len(plan_entry["generated_info"]) == 0:
                continue

            print(
                f"[GENERATING PROCESS]: Currently prefixes is being generated on interval:{plan_entry.get('interval')}"
            )

            while plan_entry["generated_info"]:
                new_prefix_len = list(plan_entry["generated_info"].keys())[0]

                if not len(self.nodes[parent_node_level]):
                    raise ValueError("New prefixes cannot be generated because there is no prefix nodes on the "
                                     "previous organisation level. Please, change depth_distribution")
                attempts = 0
                node_added = False

                node_index = random.randint(0, len(self.nodes[parent_node_level]) - 1)

                while node_index in used_nodes:
                    node_index = random.randint(0, len(self.nodes[parent_node_level]) - 1)

                while attempts < 5:

                    try:

                        # new_bits = self.Help.generate_new_bits(self.nodes[parent_node_level][node_index].depth, new_prefix_len)
                        new_bits =AbstractHelper.generate_new_bits(self.nodes[parent_node_level][node_index].depth, new_prefix_len)
                        self.add_node(new_bits, parent_node=self.nodes[parent_node_level][node_index], creating_phase=False)
                        node_added = True

                        break

                    except PrefixAlreadyExists:
                        break

                    except MaximumLevelException:
                        attempts += 1

                        if attempts >= 5:
                            used_nodes.add(node_index)
                            break

                        if len(used_nodes) == len(self.nodes[parent_node_level]):
                            raise CannotGenerateDueMaximumLevel("Cannot generate prefix from any prefix in trie "
                                                                "(level always is great than maximum possible level)")
                        continue

                if node_added:
                    # decide if organisation level should be removed from distributing plan
                    if plan_entry["generated_info"][new_prefix_len] - 1 == 0:
                        del self.Help.distribution_plan[parent_node_level+1]["generated_info"][new_prefix_len]

                    else:
                        curr_values = self.Help.distribution_plan[parent_node_level+1]["generated_info"][new_prefix_len]
                        self.Help.distribution_plan[parent_node_level + 1]["generated_info"][new_prefix_len] = curr_values - 1
