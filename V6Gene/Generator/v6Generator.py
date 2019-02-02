import random
import attr
import ipaddress
import matplotlib.pyplot as plt

from V6Gene.Trie import Trie
from typing import Dict

# 6) Generate random prefixes


@attr.s
class V6Generator:
    # Helper parameters
    prefix_quantity = attr.ib(type=int)
    rgr = attr.ib(type=float)
    depth_distribution = attr.ib(factory=dict, type=Dict)
    input_prefixes = attr.ib(factory=list, type=list)

    # Parameters for generating
    _binary_trie = attr.ib(default=Trie.Trie(), type=Trie)
    _randomly_generated_prefixes = attr.ib(default=0, type=int)
    _generated_traversing_trie = attr.ib(default=0, type=int)

    _distribution_plan = [
        {'interval': [11, 31], 'generated_info': {}},
        {'interval': [31, 47], 'generated_info': {}},
        {'interval': [47, 63], 'generated_info': {}},
        {'interval': [63, 64], 'generated_info': {}}
    ]

    # Result prefixes
    _generated_prefixes_list = attr.ib(factory=list, type=list)

    def __attrs_post_init__(self) -> None:
        """Initialize other generator class attributes.

        :return: None
        """
        #  Construct the seed prefix trie
        for prefix in self.input_prefixes:
            self._binary_trie.add_node(V6Generator.get_binary_prefix(prefix))

        # Set leaf nodes in binary trie
        self._binary_trie.preorder(self._binary_trie.root_node, "statistic")

        # Calculate number of prefixes that will be generated randomly (without using the seed prefix trie)
        self._randomly_generated_prefixes = int(float(self.prefix_quantity) * self.rgr / 100)

        # # Calculate number of prefixes that will be generated by traversing of seed prefix trie
        self._generated_traversing_trie = self.prefix_quantity - self._randomly_generated_prefixes

        # Check if generating based on depth parameter is even possible
        self._check_depth_distribution()

        # Create a distributing plan
        self._create_distributing_plan()
        self._binary_trie.distribution_plan = self._distribution_plan

        # Create output graphs
        self.create_depth_distributing_graph("depth_distributing_before_generating.svg")

    def __str__(self) -> str:
        """Represent class as string.

        :return: string; String representation of V6Gene class with info
        """
        return f"\nRGR: {self.rgr}\n"\
               f"Prefix quantity: {self.prefix_quantity}\n"\
               f"Will be generated randomly: {self._randomly_generated_prefixes}\n"\
               f"Will be generated by traversal trie: {self._generated_traversing_trie}\n"

    def start_generating(self):
        # TODO
        # first phase of generating based on binary trie. Add this node to final result
        print(f"Prefix nodes : {self._binary_trie.full_prefix_nodes}")
        print(f"Leaf nodes   : {self._binary_trie.prefix_leaf_nodes}")
        print(f"Trie generaiting: {self._generated_traversing_trie}")
        print(f"Random generaiting: {self._randomly_generated_prefixes}")



        self._binary_trie.preorder(self._binary_trie.root_node, "generate")
        print(f"After generating {self._binary_trie.prefix_nodes}")

        # TODO
        # second phase of generating - random generating

        # TODO remove redundant prefixes and call second phase if necessary
        # check final result

        self.create_depth_distributing_graph("depth_distributing_after_generating.svg")

    @staticmethod
    def get_binary_prefix(prefix_string: str) -> str:
        """

        :param prefix_string:
        :return:
        """
        parsed_address = {'prefix': prefix_string[:prefix_string.find('/')],
                          'length': int(prefix_string[prefix_string.find('/') + 1:])}

        hex_prefix = ipaddress.IPv6Address(parsed_address['prefix'])

        binary_prefix = "".join(format(x, '08b') for x in bytearray(hex_prefix.packed))

        return binary_prefix[:parsed_address['length']]

    def random_generate(self, number_of_prefixes):

        IANA = '0010'

        for counter in range(number_of_prefixes):
            # Generate other bits for LIR
            generated_part = random.getrandbits(28)
            binary_repr = IANA + format(generated_part, '0' + str(28) + 'b')

            print(f'New prefix is {self.binary_to_hex(binary_repr)} with len {len(binary_repr)}')
            # TODO : Generate other prefixes for ISP and EU after LIR

    def binary_to_hex(self, binary_representation):
        # TODO: In progress
        tt = [hex(int(binary_representation[i:i+4], 2))[-1] for i in range(0, len(binary_representation), 4)]
        hex_rep = "".join(tt)

        return hex_rep

    def create_depth_distributing_graph(self, graph_name):
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
        plt.yticks([i for i in range(50)])

        plt.savefig('graphs/' + graph_name, format='svg', dpi=1200)

    def _check_depth_distribution(self):
        # Number of new prefixes depends on :param new_dept_distribution
        new_prefixes_num = 0

        initiate_distribution = self._group_by_length(self._binary_trie.full_prefix_nodes)  # dictionary statistic from previous function
        final_distribution = self._group_by_length(self.depth_distribution)

        print(f"START_DISTRIBUTION: {initiate_distribution};\n "
              f"END DISTRIBUTION: {final_distribution}")

        print(self._group_by_length(self._binary_trie.prefix_leaf_nodes))

        for i in range(len(initiate_distribution)):
            try:
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

                # If req. for generating exists, need to check if leaf prefixes on previous level are enough for
                # generating new prefixes
                # number of prefix leafs on previous organisation level
                prefix_leafs = self._group_by_length(self._binary_trie.prefix_leaf_nodes)
                prev_organisation_lvl = prefix_leafs[i - 1]['prefixes_num']

                # If not enough -> error
                if prev_organisation_lvl - new_prefixes_num < 0:
                    raise ValueError(f"There are't enough leaf prefixes on {i - 1} level for generating")

            except IndexError:
                pass
                #  RIR level
                # check if there is some request for generating
                # if so -> Error probably. We can't generating prefixes here?

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
                raise ValueError("Number of prefixes on generated depth can't be less than current ")

            # no leaf nodes for generating new prefixes for current depth
            if prefixes_num - current_value > 0 and not self._binary_trie.get_depths(depth):
                raise ValueError(f"There is no leaf prefixes in trie for generate new prefixes on {depth} depth")

            # calculate number of prefixes which should be generated for current depth
            new_prefixes_num += prefixes_num - current_value

        if new_prefixes_num > self.prefix_quantity:
            raise ValueError("Generated prefixes num is greater than expected")

    def _group_by_length(self, distribution):

        statistic = [
            {'interval': [11, 31], 'prefixes_num': 0},
            {'interval': [31, 47], 'prefixes_num': 0},
            {'interval': [47, 63], 'prefixes_num': 0},
            {'interval': [63, 64], 'prefixes_num': 0}
        ]

        for i in range(len(statistic)):

            prefixes_in_depth = 0

            for j in range(statistic[i]['interval'][0], statistic[i]['interval'][1]):
                prefixes_in_depth += distribution.get(j, 0)

            statistic[i]['prefixes_num'] = prefixes_in_depth

        return statistic

    def _create_distributing_plan(self):
        """Initialize distribution plan variable.

        :return:
        """
        for key, value in self.depth_distribution.items():

            prefix_num = value - self._binary_trie.prefix_nodes.get(key, 0)

            if prefix_num == 0:
                continue
            else:
                for i in range(len(self._distribution_plan)):
                    if self._distribution_plan[i]['interval'][0] <= key < self._distribution_plan[i]['interval'][1]:
                        self._distribution_plan[i]['generated_info'][key] = prefix_num
