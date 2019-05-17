# was developed by Utkin Kirill

import attr

from typing import List, Dict, Optional
from Common.Trie.Node.Node import Node
from Common.Exceptions.Exceptions import MaximumLevelException


@attr.s
class AbstractTrie:
    root_node = attr.ib(default=Node(None, 0), type=Node)
    max_possible_level = attr.ib(default=7, type=int)

    _max_trie_level = attr.ib(default=0, type=int)
    _generated_prefixes = attr.ib(factory=list, type=list)
    _trie_depth = attr.ib(default=0, type=int)
    _prefix_leaf_nodes = attr.ib(factory=dict, type=dict)
    _prefix_nodes = attr.ib(factory=dict, type=dict)

    @property
    def trie_level(self) -> int:
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
    def full_prefix_nodes(self) -> Dict:
        return self._prefix_nodes

    def add_node(self, node_value: str, parent_node: Optional[Node] = None, creating_phase: bool = True) -> Node:
        raise NotImplementedError

    def generate_prefixes(self, node: Node) -> None:
        raise NotImplementedError

    def get_depths(self, level) -> List:
        return [key for key in self._prefix_leaf_nodes.keys() if key < level]

    def calculate_level(self, node: Node) -> None:
        """
        Recalculate level of prefix node if it is needed
        :param node: pointer to the prefix node object which was added to binary trie
        :raises MaximumLevelException: indicate if new added node has a level greater than maximum possible level
        :return: None
        """
        full_path = AbstractTrie.get_just_prefix_path(node)
        new_level = 0

        if node.left_child or node.right_child:
            node_level = self.get_maximum_child_level(node)

            if node_level + 1 > self.max_possible_level:
                raise MaximumLevelException

            new_level = node_level + 1

        if not self.is_possible_recalculate_parent_level(full_path, new_level):
            raise MaximumLevelException

        if node.left_child or node.right_child:
            node.level = new_level + 1

        if self.is_recalculate_level(prefix_path=full_path, new_level=new_level):
            self.recalculate_level(full_path, new_level)

        if node.level > self.trie_level:
            self._max_trie_level = node.level

    def is_possible_recalculate_parent_level(self, parents_nodes: List[Node], new_level_value) -> bool:
        """Check if parent nodes level could be recalculated and new prefix could be added.
        :param parents_nodes: list of parent nodes
        :param new_level_value: level of child node
        :return: True in case that new level is possible, False otherwise
        """
        for counter in range(len(parents_nodes)):

            if parents_nodes[counter].level < new_level_value + counter + 1:
                if new_level_value + counter + 1 > self.max_possible_level:
                    return False

        return True

    def is_recalculate_level(self, prefix_path: List[Node], new_level) -> bool:
        """Check if recalculation process is required.

        :param prefix_path: list with all parent prefix nodes
        :param new_level: new value of level
        :return: true is case if recalculating is required, false otherwise
        """
        for counter in range(len(prefix_path)):
            if prefix_path[counter].level < counter + new_level + 1:
                    return True

        return False

    def recalculate_level(self, prefix_path, new_level) -> None:
        """
        Provide algorithm for recalculating level of nodes in path for selected node
        :param prefix_path: path that contains all prefix nodes
        :param new_level: level value of inserted node
        :raises MaximumLevelException in case if recalculating isn't possible. This is just a additional check
        :return: None
        """
        for counter in range(len(prefix_path)):

            if prefix_path[counter].level < new_level + counter + 1:
                prefix_path[counter].level = new_level + counter + 1

            if prefix_path[counter].level > self.trie_level:
                self._max_trie_level = prefix_path[counter].level

    @staticmethod
    def get_just_prefix_path(node: Node) -> List[Node]:
        """Return full prefix nodes path for :param Node current node.

        Method is used for creating prefix path for current :param node. Result list contains all previous prefix nodes.
        Result list could be used for change levels all of this nodes
        :param node: Node; node object from binary trie
        :param include_current: boolean; Signalize if current node will be added to full prefix nodes path.
        :return: list; list with all previous (and current if include flag is set as True) prefix nodes for :param node
        """
        full_path = list()
        current_node = node

        while current_node.path:

            if current_node.prefix_flag:
                full_path.append(current_node)

            current_node = current_node.path

        return full_path

    @staticmethod
    def get_path_to_previous_prefix(node: Node) -> List[Node]:
        """
        Get all nodes before the inserted node :param node
        :param node: last node in the path
        :return: list of all nodes in the path from the :param node
        """
        full_path = list()
        current_node = node

        while current_node.path:
            full_path.append(current_node)
            current_node = current_node.path

            if current_node.prefix_flag:
                full_path.append(current_node)
                break

        return full_path

    def get_maximum_child_level(self, root: Node) -> Optional[int]:
        """Get maximum level of all child prefix nodes.

        :param root: node which contain child nodes
        :return: value of maximum level
        """
        if not root:
            return

        selected_root = True

        nodeStack = []
        nodeStack.append(root)
        first_childs = list()

        while nodeStack:

            node = nodeStack.pop()

            if not selected_root and node.prefix_flag:
                first_childs.append(node)

            if not node.prefix_flag or selected_root:
                selected_root = False

                if node.right_child is not None:
                    nodeStack.append(node.right_child)

                if node.left_child is not None:
                    nodeStack.append(node.left_child)

        max_child_level = max(node.level for node in first_childs)
        return max_child_level

    @staticmethod
    def construct_binary_representation(nodes) -> str:
        """Construct binary representation of prefix using saved nodes.

        :param nodes: list of nodes that represents the path from root node to prefix node
        :param nodes: list of nodes that represents the path from root node to prefix node
        :return: string which represents binary representation of prefix in trie
        """
        return ''.join([node.node_value for node in nodes if node.node_value])

    @staticmethod
    def get_prefix_nodes(node: Node) -> Optional[list]:
        """Get trie prefix nodes in binary form.

        :param node: start node in binary trie
        :return: list of node's values if node exists. None otherwise
        """
        prefix_nodes = []

        if node is None:
            return

        current_path = list()
        current_path.append(node)

        current_child = node.left_child

        while current_path:
            while current_child:
                current_path.append(current_child)
                current_child = current_child.left_child

            top = current_path[-1]

            if top.prefix_flag:
                prefix_nodes.append(AbstractTrie.construct_binary_representation(current_path))

            if not top.is_visited:
                top.is_visited = True
                current_child = top.right_child

                if current_child is None and top.right_child is None and top.left_child is None:
                    prefix_nodes.append(AbstractTrie.construct_binary_representation(current_path))
                    current_path.pop()
            else:
                current_path.pop()

        return prefix_nodes

    @staticmethod
    def delete_node_from_trie(node: Node) -> None:
        """Delete node and all unused internal nodes.
        :param node: pointer to the node which should be removed from binary trie
        :return: None
        """
        path = AbstractTrie.get_path_to_previous_prefix(node)
        child = path[0]

        for count in range(len(path)):
            if (child is node) or (not child.prefix_flag and not child.left_child and not child.right_child):
                parent = path[count + 1]

                if parent.right_child == child:
                    parent.right_child = None

                else:
                    parent.left_child = None

                child = parent

                continue

            break


    @staticmethod
    def is_exist(parent_node: Node, node_value: str) -> bool:
        """Check if current value is already exists in binary trie.
        :param parent_node: parent node for added value
        :param node_value: str representation of node
        :return: False if node not exists in binary trie, True otherwise
        """
        current_node = parent_node

        for curr_len, bit in enumerate(node_value, 1):

            if bit == '0':
                # add node to trie as a left child
                if curr_len == len(node_value) and current_node.left_child and current_node.left_child.prefix_flag:
                    return True

                if curr_len < len(node_value) and not current_node.left_child:
                    return False

                current_node = current_node.left_child

            else:
                # add node to trie as a right child
                if curr_len == len(node_value) and current_node.right_child and current_node.right_child.prefix_flag:
                    return True

                if curr_len < len(node_value) and not current_node.right_child:
                    return False

                current_node = current_node.right_child

        return False

    @staticmethod
    def level_stats(node) -> Optional[Dict]:
        """Return level statistic for nodes in trie structure

        :param node: pointer to the root node or node which is root for the particular sub-trie
        :return: information about how many nodes have particular value of level
        """
        if not node:
            return

        node_path = list()
        levels = {key: 0 for key in range(7)}
        node_path.append(node)

        while node_path:

            node = node_path.pop()

            if node.prefix_flag:
                levels[node.level] += 1

            if node.right_child:
                node_path.append(node.right_child)

            if node.left_child:
                node_path.append(node.left_child)

        return levels


