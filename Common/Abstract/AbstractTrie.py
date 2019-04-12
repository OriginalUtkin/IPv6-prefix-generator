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

            if (child == affected_node) or (not child.prefix_flag and not child.left_child and not child.right_child):

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

    def check_middle_node_level(self, root: Node) -> None:
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
        new_current_prefix_level = max_child_level + 1

        # check if current node level less than maximum possible level
        if new_current_prefix_level > self.max_possible_level:
            raise MaximumLevelException

        # if new node has less level than possible, check level for all parents level for his parent
        full_prefix_path = AbstractTrie.get_full_path(root, include_current=False)
        full_prefix_path.reverse()

        # if recalculate is possible, recalculate level for all parents
        if self.is_possible_recalculate_parent_level(full_prefix_path, new_current_prefix_level):

            for i in range(len(full_prefix_path)):
                self.recalculate_parent_level(full_prefix_path[i], new_current_prefix_level + i + 1)
        else:
            raise MaximumLevelException

        # change level of current prefix to new one
        root.level = new_current_prefix_level

        # add new prefix node to path for all child nodes
        for i in range(len(first_childs)):
            first_childs[i].path = root

    def recalculate_parent_level(self, node: Node, new_level_value: int) -> None:
        """Recalculate level for all parent nodes.

        :param node: parent node which level should be recalculated
        :param new_level_value: new level value
        :return: None
        """
        if node.level < new_level_value:
            node.level = new_level_value

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



