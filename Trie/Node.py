class Node:

    def __init__(self, node_value, node_depth):
        """

        :param node_value:
        """
        self.node_value = node_value
        self.depth = node_depth

        # Node's child
        self.left = None
        self.right = None

        # Node's characteristics
        self.prefix_node = False

        self.level = 0
