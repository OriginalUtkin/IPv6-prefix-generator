# was developed by Utkin Kirill

import attr

from typing import Dict
from V6Gene.Trie import Trie
from V6Gene.Generator.Helper import Helper
from Common.Converter.Converter import Converter
from Common.Abstract.AbstractTrie import AbstractTrie
from Common.Exceptions.Exceptions import MaximumLevelException, PrefixAlreadyExists


@attr.s
class V6Generator:
    # Helper parameters
    prefix_quantity = attr.ib(type=int)
    rgr = attr.ib(type=float)
    depth_distribution = attr.ib(factory=dict, type=Dict)
    level_distribution = attr.ib(factory=dict, type=Dict)
    input_prefixes = attr.ib(factory=list, type=list)
    Help = attr.ib(default=Helper(), type=Helper)

    # Parameters for generating
    _binary_trie = attr.ib(default=Trie.Trie(), type=Trie)
    _randomly_generated_prefixes = attr.ib(default=0, type=int)
    _generated_traversing_trie = attr.ib(default=0, type=int)

    # Result prefixes
    _generated_prefixes_list = attr.ib(factory=list, type=list)

    def __attrs_post_init__(self) -> None:
        """Initialize other generator class attributes.
        :return: None
        """
        #  Construct the seed prefix trie
        for prefix in self.input_prefixes:
            self._binary_trie.add_node(prefix)

        # Check leaf nodes in binary trie
        self._binary_trie.trie_traversal("statistic")
        # Check if generating based on depth and level parameter is even possible
        self._check_depth_distribution()
        self._check_level_distribution()

        # Initialize helper class
        self.help_init()
        self._binary_trie.Help = self.Help
        self._binary_trie.max_possible_level = self._max_level()

        total_generate = 0
        for i in self.Help.distribution_plan:
            total_generate += sum(i['generated_info'].values())

        # Calculate number of prefixes that will be generated randomly (without using the seed prefix trie)
        if self.rgr != 0:
            self._randomly_generated_prefixes = int(float(total_generate) * self.rgr)

        else:
            self._randomly_generated_prefixes = 0

        # Calculate number of prefixes that will be generated by traversing of seed prefix trie
        self._generated_traversing_trie = total_generate - self._randomly_generated_prefixes

        self._binary_trie._maximum_trie_traversal_generated = self._generated_traversing_trie

    def help_init(self) -> None:
        """
        Initialize all helper structures which will be used during the generating process
        :return: None
        """
        self.Help.start_depth_distribution = self._binary_trie.full_prefix_nodes
        self.Help.final_depth_distribution = self.depth_distribution
        self.Help.leafs_prefixes = self._binary_trie.prefix_leaf_nodes

        self.Help.create_distributing_plan()
        self.Help.create_distributing_strategy(self._binary_trie.prefix_leaf_nodes)

    def get_root(self):
        """
        Return the root node of constructed binary trie
        :return: Node object that represents root node of tire
        """
        return self._binary_trie.root_node

    def start_generating(self):

        if self.rgr != 1:
            self._binary_trie.trie_traversal("generate")

        # second phase of generating - random generating
        if self.rgr != 0:

            # Generate prefixes that couldn't be added to trie by generating process
            self._random_generate(self.Help.distribution_random_plan)

            if self.Help.distribution_plan:
                self._random_generate(self.Help.distribution_plan, True)

        new_prefixes = set(AbstractTrie.get_prefix_nodes(self._binary_trie.root_node))

        output_converter = Converter(new_prefixes)
        converted_prefixes = output_converter.convert_prefixes()

        return converted_prefixes

    def _random_generate(self, distribution_plan: Dict, additional_generate: bool = False) -> None:
        """Randomly generate new prefixes.

        :param distribution_plan: len of prefixes, which should be generated.
        :param additional_generate: signalize if some number of prefixes wasn't generated after first phase.
        :return: None
        """
        IANA = '001'

        for org_level in distribution_plan:
            org_level_plan = org_level['generated_info']

            for prefix_len, prefix_num in org_level_plan.items():
                for count in range(prefix_num):

                    if self._randomly_generated_prefixes == 0 and not additional_generate:
                        return

                    while True:
                        try:
                            # First 4 bits will be IANA part
                            new_bits = Helper.generate_new_bits(3, prefix_len)
                            new_prefix = IANA + new_bits
                            self._binary_trie.add_node(new_prefix, creating_phase=False)

                            self._randomly_generated_prefixes -= 1

                            break

                        except PrefixAlreadyExists:
                            continue

                        except MaximumLevelException:
                            continue

    def _check_depth_distribution(self) -> None:
        """Check input parameter depth distribution.
        Check input parameter and control if generating is even possible

        :return: None
        """
        new_prefixes_num = 0

        initiate_distribution = self.Help.group_by_length(self._binary_trie.full_prefix_nodes)  # dictionary statistic from previous function
        final_distribution = self.Help.group_by_length(self.depth_distribution)

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
                raise ValueError(f"[ERROR] Number of prefixes specified by depth_distribution in interval "
                                 f"{initiate_distribution[i]['interval'][0]} - {initiate_distribution[i]['interval'][1]}"
                                 f" less than 0. Generator cannot allow remove prefixes.\n Please, change"
                                 f" depth_distribution parameter")

            # If exists some leafs nodes on previous depth level -> prefixes will be generated from them
            if self.Help.group_by_length(self._binary_trie.prefix_leaf_nodes)[i-1]['prefixes_num'] > 0:
                continue

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
                raise ValueError(f"[ERROR] Number of prefixes on generated depth can't be less than current number in depth  {depth}. Number of prefixes in seed file is {current_value}, number of prefixes in depth distribution is {prefixes_num}")

        new_prefixes = sum(item['prefixes_num'] for item in final_distribution) - \
                       sum(item['prefixes_num'] for item in initiate_distribution)

        if new_prefixes > self.prefix_quantity:
            raise ValueError("Generated prefixes num is greater than expected")

    def _check_level_distribution(self) -> None:
        if self._binary_trie.trie_level > self._max_level():
            raise ValueError("[ERROR] Generator can't start. Trie contains nodes which already have level greater than allowed maximum level specified by input parameter. Please, change maximum possible level or use another input set")

    def _max_level(self) -> int:
        max_level = 0

        for key in self.level_distribution.keys():
            if self.level_distribution[key] != 0 and key > max_level:
                max_level = key

        return max_level
