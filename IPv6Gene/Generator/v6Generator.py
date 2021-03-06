# was developed by Utkin Kirill

import attr

from Common.Abstract.AbstractHelper import AbstractHelper
from Common.Abstract.AbstractTrie import AbstractTrie
from IPv6Gene.Trie import Trie
from IPv6Gene.Generator.Helper import Helper
from IPv6Gene.Generator.RandomGenerator import RandomGenerator
from Common.Converter.Converter import Converter
from typing import Dict, List


@attr.s
class V6Generator:
    # Helper parameters
    prefix_quantity = attr.ib(type=int)
    depth_distribution = attr.ib(factory=dict, type=Dict)
    max_level = attr.ib(default=7, type=int)
    input_prefixes = attr.ib(factory=list, type=list)
    Help = attr.ib(default=Helper(), type=Helper)
    stats = attr.ib(default=False, type=bool)

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
        if self.stats:
            print("[GENERATOR]: Construct binary trie")

        for prefix in self.input_prefixes:
            self._binary_trie.add_node(prefix)

        if self.stats:
            print("[GENERATOR]: Binary trie was successfully constructed")

        # Check if generating based on depth and level parameter is even possible
        self._check_depth_distribution()
        self._check_level_distribution()

        # Initialize helper class
        self.help_init()

        self._binary_trie.stats = self.stats
        self._binary_trie.max_possible_level = self.max_level

    def get_binary_trie_prefixes_num(self) -> int:
        """Get current number of prefix nodes in binary trie.

        :return: int, number of prefixes nodes in trie
        """
        return sum(self._binary_trie.full_prefix_nodes.values())

    def get_binary_trie_level(self) -> int:
        """Get current level of binary trie.

        :return: int, current binary trie level
        """
        return self._binary_trie.trie_level

    def get_binary_trie_depth(self) -> int:
        """Get maximum depth of binary trie.

        :return: int, current binary trie maximum depth
        """
        return self._binary_trie.trie_depth

    def help_init(self) -> None:
        """Init helper structure for generating process.

        :return: None
        """
        self.Help.start_depth_distribution = self._binary_trie.full_prefix_nodes
        self.Help.final_depth_distribution = self.depth_distribution
        self.Help.create_distributing_plan()

    def get_root(self):
        return self._binary_trie.root_node

    def start_generating(self) -> List[str]:
        """Start generating process.

        :return: list with generated prefixes
        """

        # Generate new RIR nodes and add them to binary trie
        if Helper.distribution_random_plan:
            if self.stats:
                print("[RANDOM GENERATING]: Start generating prefixes randomly")

            Randomizer = RandomGenerator(self._binary_trie, self.Help, distribution_plan=Helper.distribution_random_plan, stats=self.stats)
            Randomizer.random_generate()

            if self.stats:
                print("[RANDOM GENERATING]: Random generating phase successfully done")
        else:
            if self.stats:
                print("[RANDOM GENERATING]: Random generating phase is skipped. Only RIR prefixes that have "
                      "a length in interval 12  - 31 could be generated randomly")

        if self.stats:
            print("[TRIE TRAVERSING GENERATING]: Start generating prefixes using constructed trie")

        self._binary_trie.generate_prefixes()

        if self.stats:
            print("[TRIE TRAVERSING GENERATING]: Traversing trie generating phase successfully done")

        new_prefixes = set(AbstractTrie.get_prefix_nodes(self._binary_trie.root_node))

        output_converter = Converter(new_prefixes)
        converted_prefixes = output_converter.convert_prefixes()

        return converted_prefixes

    def _check_depth_distribution(self) -> None:
        """Check input parameter depth distribution.
        Check input parameter and control if generating is even possible

        :raises ValueError exception in case when depth distribution parameter has invalid format
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

            if i == 0 and new_prefixes_num > 0:
                raise ValueError("[ERROR] New prefixes cannot be generated with length which less than 12")

            # deleting prefixes
            if new_prefixes_num < 0:
                raise ValueError(f"[ERROR] Number of prefixes specified by depth_distribution in interval "
                                 f"{initiate_distribution[i]['interval'][0]} - {initiate_distribution[i]['interval'][1]}"
                                 f" less than 0. Generator cannot allow remove prefixes.\n Please, change"
                                 f" depth_distribution parameter")

        for depth, prefixes_num in self.depth_distribution.items():
            current_value = self._binary_trie.prefix_nodes.get(depth)

            if prefixes_num < 0:
                raise ValueError(f"[ERROR] Number of prefixes can't be less than zero. Check depth distribution "
                                 f"argument for depth {depth}")

            if depth < 0:
                raise ValueError(f"[ERROR] Depth, specified in seed prefix file or depth distribution file, cannot be less than zero. Please, "
                                 f"change this negative value in depth_distribution parameter on depth {depth}")

            if current_value is None:  # depth doesn't exist in trie
                # Set number of prefixes on this depth as 0
                current_value = 0

            # input distribution contains less prefixes than already are in trie on the same depth
            if prefixes_num - current_value < 0:
                raise ValueError(f"[ERROR] Number of prefixes specified by depth_distribution in depth {depth} "
                                 f" less than number of prefixes in seed prefix file with the same prefix length"
                                 f". Generator cannot allow remove prefixes.\n Please, change "
                                 f"depth_distribution parameter")
        final_sum = 0
        init_sum = 0

        for prefixes in range(len(initiate_distribution)):
            final_sum += final_distribution[prefixes]['prefixes_num']
            init_sum += initiate_distribution[prefixes]['prefixes_num']

        if (len(self.input_prefixes) + (final_sum - len(self.input_prefixes))) - self.prefix_quantity != 0:
            raise ValueError(f"[ERROR] Number of prefixes defined by --prefix_quantity is different than number of "
                f"prefixes specified by --depth_distribution.\nNumber of prefixes specified by depth distribution parameter is: {final_sum}\n"
                f"Number of prefixes specified by prefix_quantity {self.prefix_quantity} \nPlease, change number of prefixes in depth distribution or change prefix_quantity parameter")

    def _check_level_distribution(self) -> None:
        """Check if level constructed binary trie is less or equals specified level by input argument.

        :raises ValueError exception in case if constructed binary trie has a bigger level than specified level by input parameter

        :return: None
        """
        if self._binary_trie.trie_level > self.max_level:
            raise ValueError("[ERROR] Generator can't start. Trie contains nodes which already have level greater than allowed maximum level specified by input parameter. Please, change maximum possible level or use another input set.")
