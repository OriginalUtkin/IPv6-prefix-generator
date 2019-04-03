import attr
import matplotlib.pyplot as plt

from Abstract.AbstractHelper import AbstractHelper
from Abstract.AbstractTrie import AbstractTrie
from IPv6Gene.Trie import Trie
from IPv6Gene.Generator.Helper import Helper
from IPv6Gene.Generator.RandomGenerator import RandomGenerator
from Converter.Converter import Converter
from typing import Dict


@attr.s
class V6Generator:
    # Helper parameters
    prefix_quantity = attr.ib(type=int)
    depth_distribution = attr.ib(factory=dict, type=Dict)
    max_level = attr.ib(default=7, type=int)
    input_prefixes = attr.ib(factory=list, type=list)
    Help = attr.ib(default=Helper(), type=Helper)

    # Parameters for generating
    _binary_trie = attr.ib(default=Trie.Trie(), type=Trie)
    _generated_traversing_trie = attr.ib(default=0, type=int)

    # Result prefixes
    _generated_prefixes_list = attr.ib(factory=list, type=list)

    def __attrs_post_init__(self) -> None:
        """Initialize other generator class attributes.
        :return: None
        """
        self._binary_trie.Help = self.Help

        #  Construct the seed prefix trie
        print("---[GENERATING BINARY TRIE PROCESS]: Start ----")

        for prefix in self.input_prefixes:
            self._binary_trie.add_node(prefix)

        print("---[GENERATING BINARY TRIE PROCESS]: Binary trie was generated ----")

        # Check if generating based on depth and level parameter is even possible
        self._check_depth_distribution()
        self._check_level_distribution()

        # Initialize helper class
        self.help_init()

        self._binary_trie.max_possible_level = self.max_level

        # Create output graphs
        # self.create_depth_distributing_graph("depth_distributing_before_generating.svg")

    def help_init(self):
        self.Help.start_depth_distribution = self._binary_trie.full_prefix_nodes
        self.Help.final_depth_distribution = self.depth_distribution
        self.Help.create_distributing_plan()

    def start_generating(self):

        # Generate new RIR nodes and add them to binary trie
        print("---[GENERATING NEW PREFIXES RANDOMLY]: Start ----")
        Randomizer = RandomGenerator(self._binary_trie, distribution_plan=Helper.distribution_random_plan)
        Randomizer.random_generate()
        print("---[GENERATING NEW PREFIXES RANDOMLY]: Done ----")

        print("---[GENERATING NEW PREFIXES TRAVERSING TRIE]: Start ----")
        self._binary_trie.generate_prefixes()
        print("---[GENERATING NEW PREFIXES TRAVERSING TRIE]: Done ----")

        new_prefixes = set(AbstractTrie.get_prefix_nodes(self._binary_trie.root_node))

        output_converter = Converter(new_prefixes)
        converted_prefixes = output_converter.convert_prefixes()

        return converted_prefixes

        # self.create_depth_distributing_graph("depth_distributing_after_generating.svg")

    def create_depth_distributing_graph(self, graph_name) -> None:
        """Create inputs and outputs graphs using current state of binary trie.

        :param graph_name: string; name of graph
        :return: None
        """
        x = []

        for p_len in self._binary_trie.prefix_nodes.keys():
            x.append(p_len)

        prefix_num = list(self._binary_trie.prefix_nodes.values())
        plt.figure(figsize=(15, 15))
        plt.bar(x, prefix_num, align='center', alpha=1,)

        plt.xlabel("Prefix length")
        plt.ylabel("Number of prefixes")
        plt.title("Depth distribution before generating", fontweight='bold')

        plt.xticks([i for i in range(max(x)+1)])
        plt.yticks([i for i in range(100)])

        plt.savefig('graphs/' + graph_name, format='svg', dpi=1200)

    def _check_depth_distribution(self) -> None:
        """Check input parameter depth distribution.
        Check input parameter and control if generating is even possible

        :return: None
        """
        initiate_distribution = AbstractHelper.group_by_length(self._binary_trie.full_prefix_nodes)  # dictionary statistic from previous function
        final_distribution = AbstractHelper.group_by_length(self.depth_distribution)

        for i in range(len(initiate_distribution)):

            start = initiate_distribution[i]['prefixes_num']
            end = final_distribution[i]['prefixes_num']

            # Calculate how many prefixes should be generated on current i level
            new_prefixes_num = end - start

            # no changes; Deep check is necessary here
            if new_prefixes_num == 0:
                continue

            # deleting prefixes
            if new_prefixes_num < 0:
                raise ValueError(f"Cannot delete prefixes from {i} level")

        for depth, prefixes_num in self.depth_distribution.items():
            current_value = self._binary_trie.prefix_nodes.get(depth)

            if prefixes_num < 0:
                raise ValueError("Number of prefixes can't be less than zero")

            if depth < 0:
                raise ValueError("Level value can't be less than zero")

            if current_value is None:  # depth doesn't exist in trie
                # Set number of prefixes on this depth as 0
                current_value = 0

            # input distribution contains less prefixes than already are in trie on the same depth
            if prefixes_num - current_value < 0:
                raise ValueError("Number of prefixes on generated depth can't be less than current number")

        new_prefixes = sum(item['prefixes_num'] for item in final_distribution) - \
                       sum(item['prefixes_num'] for item in initiate_distribution)

        if new_prefixes > self.prefix_quantity:
            raise ValueError("Generated prefixes num is greater than expected")

    def _check_level_distribution(self):
        if self._binary_trie.trie_level > self.max_level:
            raise ValueError("Current max trie level more than max lvl from level distribution parameter")
