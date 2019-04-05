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

    def get_depths(self, level) -> List:
        return [key for key in self._prefix_leaf_nodes.keys() if key < level]

    @staticmethod
    def get_full_path(node: Node, include_current=False) -> List[Node]:
        """Return full prefix nodes path for :param Node current node.

        Method is used for creating prefix path for current :param node. Result list contains all previous prefix nodes.
        Result list could be used for change levels all of this nodes
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

    @staticmethod
    def construct_binary_representation(nodes) -> str:
        """Construct binary representation of prefix using saved nodes.

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
    def delete_node_from_trie(path_from_main_parent: List[Node]) -> None:
        """

        :param path_from_main_parent:
        :return:
        """

        affected_node = path_from_main_parent[-1]

        parent = path_from_main_parent[-2]
        child = affected_node

        while path_from_main_parent:

            if child == affected_node or not child.prefix_flag and not child.left_child and not child.right_child:

                if parent.right_child == child:
                    parent.right_child = None

                else:
                    parent.left_child = None

                path_from_main_parent.pop()

                if len(path_from_main_parent) < 2:
                    break

                child = parent
                parent = path_from_main_parent[-2]

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
                if curr_len == len(node_value) and current_node.left_child:
                    return True

                if curr_len < len(node_value) and not current_node.left_child:
                    return False

                current_node = current_node.left_child

            else:
                # add node to trie as a right child
                if curr_len == len(node_value) and current_node.right_child:
                    return True

                if curr_len < len(node_value) and not current_node.right_child:
                    return False

                current_node = current_node.right_child

        return False
