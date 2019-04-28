import attr
import random
import ipaddress

from typing import List, Dict
from ..Converter.Converter import Converter
from ipaddress import IPv6Address


@attr.s
class AbstractHelper:

    start_depth_distribution = attr.ib(factory=dict, type=dict)
    final_depth_distribution = attr.ib(factory=dict, type=dict)

    _intervals = {0: [0, 12], 1: [12, 32], 2: [32, 48], 3: [48, 64], 4: [64, 65]}

    # Helper structure which contains a number of prefixes on organisation levels for trie traversal generating process
    distribution_plan = [
        {'interval': [0, 12], 'generated_info': {}},
        {'interval': [12, 32], 'generated_info': {}},
        {'interval': [32, 48], 'generated_info': {}},
        {'interval': [48, 64], 'generated_info': {}},
        {'interval': [64, 65], 'generated_info': {}}
    ]

    def create_distributing_plan(self) -> None:
        """Abstract method which should be implemented by subclasses.
        Calculate distribution plan for generator.

        :return: None
        """
        raise NotImplementedError

    @staticmethod
    def group_by_length(distribution: Dict) -> List[Dict]:

        statistic = [
            {'interval': [0, 12], 'prefixes_num': 0},
            {'interval': [12, 32], 'prefixes_num': 0},
            {'interval': [32, 48], 'prefixes_num': 0},
            {'interval': [48, 64], 'prefixes_num': 0},
            {'interval': [64, 65], 'prefixes_num': 0}
        ]

        for i in range(len(statistic)):

            prefixes_in_depth = 0

            for j in range(statistic[i]['interval'][0], statistic[i]['interval'][1]):
                prefixes_in_depth += distribution.get(j, 0)

            statistic[i]['prefixes_num'] = prefixes_in_depth

        return statistic

    @staticmethod
    def generate_new_bits(current_prefix_depth: int, new_prefix_depth: int) -> str:
        """Generate new random bits for current prefix.

        :param current_prefix_depth: integer; current prefix len in trie
        :param new_prefix_depth: integer; new prefix len which is needed
        :return: string; new generated bits (0 and 1) in string form
        """
        generate_num = new_prefix_depth - current_prefix_depth

        generated_sequence = random.getrandbits(generate_num)

        binary_rep = ("{0:b}".format(generated_sequence))

        if len(binary_rep) < generate_num:
            additional_bits = generate_num - len(binary_rep)

            for i in range(additional_bits):
                binary_rep = '0' + binary_rep

        return binary_rep

    @staticmethod
    def get_binary_prefix(prefix_string: str) -> str:
        """Convert hexadecimal prefix representation to binary representation.

        :param prefix_string: string; string contains hexadecimal representation of prefix
        :return: string; binary representation of current prefix without additional 0 at the end
        """
        parsed_address = {'prefix': prefix_string[:prefix_string.find('/')],
                          'length': int(prefix_string[prefix_string.find('/') + 1:])}

        hex_prefix = ipaddress.IPv6Address(parsed_address['prefix'])

        binary_prefix = "".join(format(x, '08b') for x in bytearray(hex_prefix.packed))

        return binary_prefix[:parsed_address['length']]

    @staticmethod
    def get_bit_position(bit_value: str, prefixes: List):
        result = {key: 0 for key in range(0, 64)}

        for prefix in prefixes:
            positions = [pos for pos, char in enumerate(prefix) if char == bit_value]
            for position in positions:
                result[position] += 1

        convert_to_percent = {key: 0 for key in range(0, 64)}

        for i in range(len(convert_to_percent)):
            number_of_prefixes = result[i]
            convert_to_percent[i] = number_of_prefixes / len(prefixes) * 100

        return convert_to_percent

