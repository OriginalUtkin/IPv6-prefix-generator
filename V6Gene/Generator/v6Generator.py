import random
import attr
import ipaddress
import matplotlib.pyplot as plt

from V6Gene.Trie import Trie
from typing import Dict

# 5) Generate prefixes using binary trie
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

    # Result parameters
    _generated_prefixes_list = attr.ib(factory=list, type=list)

    def __attrs_post_init__(self) -> None:
        """Initialize other generator class attributes.

        :return: None
        """
        #  Construct the seed prefix trie
        for prefix in self.input_prefixes:
            self._binary_trie.add_node(self._get_binary_prefix(prefix))

        # Set leaf nodes in binary trie
        self._binary_trie.preorder(self._binary_trie.root_node, "statistic")

        # Calculate number of prefixes that will be generated randomly (without using the seed prefix trie)
        self._randomly_generated_prefixes = int(float(self.prefix_quantity) * self.rgr / 100)

        # Calculate number of prefixes that will be generated by traversing of seed prefix trie
        self._generated_traversing_trie = self.prefix_quantity - self._randomly_generated_prefixes

        # Check if generating based on depth parameter is even possible
        self._check_depth_distribution()

    def start_generating(self):
        print("Generating prefixes. Bghghghghhghg")
        # TODO
        # first phase of generating based on binary trie
        pass

        # TODO
        # second phase of generating - random generating

        # TODO remove redundant prefixes and call second phase if needed
        # control final result

    def _get_binary_prefix(self, prefix_string: str) -> str:
        """

        :param prefix_string:
        :return:
        """
        parsed_address = {'prefix': prefix_string[:prefix_string.find('/')],
                          'length': int(prefix_string[prefix_string.find('/') + 1:])}

        hex_prefix = ipaddress.IPv6Address(parsed_address['prefix'])

        binary_prefix = "".join(format(x, '08b') for x in bytearray(hex_prefix.packed))

        return binary_prefix[:parsed_address['length']]

    # TODO: Remove this code
    def test_trie(self):
        # Create new trie here
        self._binary_trie.preorder(self._binary_trie.root_node, "statistic")
        self._randomly_generated_prefixes = int(float(self.prefix_quantity) * self.rgr / 100)
        self._generated_traversing_trie = self.prefix_quantity - self._randomly_generated_prefixes
        self._check_depth_distribution()

    def _check_depth_distribution(self):
        # Number of new prefixes depends on :param new_dept_distribution
        new_prefixes_num = 0
        current_depth_distribution = self._binary_trie.prefix_nodes

        for depth, prefixes_num in self.depth_distribution.items():
            current_value = current_depth_distribution.get(depth)

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

    def create_depth_distributing_graph(self):
        x = []

        for p_len in self._binary_trie.prefix_nodes.keys():
            x.append(p_len + 1)

        x_pos = x

        prefix_num = list(self._binary_trie.prefix_nodes.values())

        plt.bar(x_pos, prefix_num, align='center')

        plt.xlabel("Prefix length")
        plt.ylabel("Number of prefixes")
        plt.title("Depth distribution before generating")

        plt.xticks(x_pos, x)

        plt.savefig("distributing_before_generating.png")
