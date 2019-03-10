from typing import Dict, List
import attr
import random
import ipaddress


class Helper:

    start_depth_distribution = attr.ib(factory=dict, type=dict)
    final_depth_distribution = attr.ib(factory=dict, type=dict)

    _intervals = {0: [12, 32], 1: [32, 48], 2: [48, 64], 3: [64, 65]}

    # Helper structure which contains a number of prefixes on organisation levels for trie traversal generating process
    distribution_plan = [
        {'interval': [12, 32], 'generated_info': {}},
        {'interval': [32, 48], 'generated_info': {}},
        {'interval': [48, 64], 'generated_info': {}},
        {'interval': [64, 65], 'generated_info': {}}
    ]

    # Helper structure which contains a number of prefixes on organisation levels for random generating process
    distribution_random_plan = [
        {'interval': [12, 32], 'generated_info': {}},
    ]

    def create_distributing_plan(self) -> None:
        """Initialize distribution plan variable.
        :return: None
        """
        for prefix_depth, prefix_num in self.final_depth_distribution.items():

            new_prefix_num = prefix_num - self.start_depth_distribution.get(prefix_depth, 0)

            # the number of prefixes the same as at the start
            if new_prefix_num == 0:
                continue

            else:
                org_lvl = self.get_organisation_level_by_depth(prefix_depth)

                if org_lvl == 0:
                    self.distribution_random_plan[org_lvl]['generated_info'][prefix_depth] = new_prefix_num

                else:
                    self.distribution_plan[org_lvl]['generated_info'][prefix_depth] = new_prefix_num

    def get_organisation_level_by_depth(self, node_depth: int) -> int:
        """Return organisation depth level for particular depth.

        :param node_depth: integer; depth of current node
        :return: integer which represents a organisation depth level
        """
        for i in range(len(self._intervals)):
            if self._intervals[i][0] <= node_depth < self._intervals[i][1]:
                return i

    def max_organisation_depth(self) -> int:
        return len(self._intervals) - 1

    def get_plan_keys(self, prefix_depth_level: int) -> List:
        return list(self.distribution_plan[prefix_depth_level]['generated_info'].keys())

    def get_plan_values(self, prefix_depth_level: int, prefix_depth: int) -> int:
        return self.distribution_plan[prefix_depth_level]['generated_info'][prefix_depth]

    def remove_from_plan(self, prefix_depth_level: int, prefix_depth: int) -> None:
        """Remove :param prefix_depth from distribution_plan for particular :param prefix_depth_level

        :param prefix_depth_level: integer; number of organisation depth level of prefix
        :param prefix_depth: integer; prefix len
        :return: None
        """
        self.distribution_plan[prefix_depth_level]['generated_info'].pop(prefix_depth)

    def decrease_plan_value(self, prefix_depth_level, prefix_depth):
        self.distribution_plan[prefix_depth_level]['generated_info'][prefix_depth] -= 1

    def group_by_length(self, distribution: Dict) -> List:

        statistic = [
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
