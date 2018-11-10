from Trie import Node


class Trie:

    def __init__(self):
        self.root_node = Node.Node(None, 0)
        self.trie_depth = 0
        self.leaf_nodes = 0

    def add_node(self, node_value):
        """

        :param node_value:
        :return:
        """
        current_node = self.root_node

        for bit in node_value:

            if bit == '0':

                # add node to trie
                if not current_node.left:
                    current_node.left = Node.Node(bit, current_node.depth + 1)

                current_node = current_node.left

            else:

                # add node to trie
                if not current_node.right:
                    current_node.right = Node.Node(bit, current_node.depth + 1)

                current_node = current_node.right

        current_node.prefix_node = True

        # Set a trie depth
        if current_node.depth > self.trie_depth:
            self.trie_depth = current_node.depth

        # Check if current node is leaf node
        if not current_node.right and not current_node.left:
            current_node.prefix_leaf = True
        else:
            current_node.prefix_leaf = False

    def preorder(self, root):
        if root:
            if not root.node_value:
                print("None " + str(root.depth))
            else:
                print("Value: " + root.node_value + " depth:" + str(root.depth))

            print(self.preorder(root.left))
            print(self.preorder(root.right))

    # def set_leaf(self):
    #
    #     stack = list()
    #     stack.append(self.root_node)
    #
    #     while stack:
    #
    #         current_node = stack.pop()
    #         # print(current_node.node_value)
    #
    #         if current_node.right:
    #             stack.append(current_node.right)
    #
    #         if current_node.left:
    #             stack.append(current_node.left)
    #
    #         if current_node.prefix_leaf:
    #             self.leaf_nodes += 1
    #         # if not current_node.left and not current_node.right:
    #         #     current_node.prefix_leaf = True
    #         #     self.leaf_nodes += 1
    #             # the node is a lead node -> generate prefix

    def __str__(self):
        return f"Trie depth: {self.trie_depth}\n" \
               f"Number of prefix leafs: {self.leaf_nodes} "
