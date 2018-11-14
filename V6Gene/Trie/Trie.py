from V6Gene.Trie import Node
import random


class Trie:

    def __init__(self):
        self.root_node = Node.Node(None, 0)
        self.trie_depth = 0
        self.prefix_nodes = 0

    def add_node(self, node_value, parent_node=None):
        """

        :param node_value:
        :param parent_node
        :return:
        """
        if not parent_node:
            current_node = self.root_node
        else:
            current_node = parent_node

        for bit in node_value:

            if bit == '0':

                # add node to trie as a left child
                if not current_node.left:
                    current_node.left = Node.Node(bit, current_node.depth + 1)

                current_node = current_node.left

            else:

                # add node to trie as a right child
                if not current_node.right:
                    current_node.right = Node.Node(bit, current_node.depth + 1)

                current_node = current_node.right

        # Added node is a prefix node
        current_node.prefix_node = True
        self.prefix_nodes += 1

        # Set a trie depth
        if current_node.depth > self.trie_depth:
            self.trie_depth = current_node.depth

    def preorder(self, root):

        if root:
            print(root.node_value)

            if not root.left and not root.right:
                print(f'Leaf node has depth {root.depth}')
                self._generate_prefix(root)

            self.preorder(root.left)
            self.preorder(root.right)

    def _generate_prefix(self, node):
        """

        :param node:
        :return:
        """

        # Allocation of IPv6 address space rules: RIR to LIR, LIR to ISP, ISP to EU
        tt = {'RIR': [12, 20], 'LIR': [32, 16], 'ISP': [48, 16]}

        print(f'Generator function start')

        for key, value in tt.items():

            if value[0] - node.depth == 0:
                print(f'generating len is {value[1]}')
                generated_value = random.getrandbits(value[1])
                binary_repr = format(generated_value, '0' + str(value[1]) + 'b')
                self.add_node(binary_repr, node)
            else:
                continue

    # function to print all path from root
    # to leaf in binary tree
    def printPaths(self, root):
        # list to store path
        path = []
        self.printPathsRec(root, path, 0)


    def printPathsRec(self, root, path, pathLen):

        # Base condition - if binary tree is
        # empty return
        if root is None:
            return

        # add current root's data into
        # path_ar list

        # if length of list is gre
        if (len(path) > pathLen):
            path[pathLen] = root.node_value
        else:
            path.append(root.node_value)

            # increment pathLen by 1
        pathLen = pathLen + 1

        if root.left is None and root.right is None:

            # leaf node then print the list
            self.printArray(path, pathLen)
        else:
            # try for left and right subtree
            self.printPathsRec(root.left, path, pathLen)
            self.printPathsRec(root.right, path, pathLen)

    # Helper function to print list in which
    # root-to-leaf path is stored
    def printArray(self,ints, len):

        for i in ints[0: len]:
            print(i,end="")
        print()



    def __str__(self):
        return f"Trie depth: {self.trie_depth}\n" \
               f"Number of prefix nodes: {self.prefix_nodes} "
