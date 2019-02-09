from typing import Dict, List
import attr
import random
import ipaddress


class Helper:

    start_depth_distribution = attr.ib(factory=dict, type=dict)
    final_depth_distribution = attr.ib(factory=dict, type=dict)
    leafs_prefixes = attr.ib(factory=dict, type=dict)

    _intervals = {0: [11, 31], 1: [31, 47], 2: [47, 63], 3: [63, 64]}

    distribution_plan = [
        {'interval': [11, 31], 'generated_info': {}},
        {'interval': [31, 47], 'generated_info': {}},
        {'interval': [47, 63], 'generated_info': {}},
        {'interval': [63, 64], 'generated_info': {}}
    ]

    distribution_random_plan = [
        {'interval': [11, 31], 'prefixes_num': {}},
        {'interval': [31, 47], 'prefixes_num': {}},
        {'interval': [47, 63], 'prefixes_num': {}},
        {'interval': [63, 64], 'prefixes_num': {}}
    ]

    generating_strategy = [
        {'interval': [11, 31], 'generating_strategy': None},
        {'interval': [31, 47], 'generating_strategy': None},
        {'interval': [47, 63], 'generating_strategy': None},
        {'interval': [63, 64], 'generating_strategy': None}
    ]

    def create_distributing_plan(self):
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
                    leafs_distribution = self.group_by_length(self.leafs_prefixes)

                    if leafs_distribution[org_lvl - 1]['prefixes_num'] != 0:
                        self.distribution_plan[org_lvl]['generated_info'][prefix_depth] = new_prefix_num

                    else:
                        self.distribution_random_plan[org_lvl]['generated_info'] = new_prefix_num

    def get_organisation_level_by_depth(self, node_depth: int) -> int:
        """Return organisation depth level for particular depth

        :param node_depth: integer; depth of current node
        :return: integer which represents a organisation depth level
        """
        for i in range(len(self._intervals)):
            if self._intervals[i][0] <= node_depth < self._intervals[i][1]:
                return i

    def max_organisation_depth(self) -> int:
        return len(self._intervals) - 1

    def get_dd_plan(self, prefix_depth_level: int) -> Dict:
        return self.distribution_plan[prefix_depth_level]['generated_info']

    def get_gs(self, prefix_depth_level: int) -> int:
        """Remove and return a generation strategy for :param prefix_depth_level.

        :param prefix_depth_level: integer; organisation depth of prefix
        :return: integer; number of prefixes which should be generated from current prefix
        """
        return self.generating_strategy[prefix_depth_level]['generating_strategy'].pop(0)

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

    def create_distributing_strategy(self, prefix_leaf_nodes: Dict):
        """Initialize distributing strategy for all organisation levels.

        :param prefix_leaf_nodes: Dictionary; dictionary in format {depth: number of leaf nodes}
        :return: None
        """

        leaf_prefixes = self.group_by_length(prefix_leaf_nodes)

        for i in range(len(self.distribution_plan)):

            # cannot generate from leaf nodes with len eq 64
            if i == len(self.distribution_plan) - 1:
                break

            # nothing to to
            if not self.distribution_plan[i+1]['generated_info']:
                continue

            new_prefixes = 0
            leafs = leaf_prefixes[i]['prefixes_num']

            for prefixes_num in self.distribution_plan[i+1]['generated_info'].values():
                new_prefixes += prefixes_num

            # calculate how many prefixes will be generated from nodes on this level
            test = float(new_prefixes / leafs)

            # number of leaf prefixes the same as number of prefixes on following organisation level
            if test == 1:
                print("case 1")
                self.generating_strategy[i]['generating_strategy'] = [1 for _ in range(leafs)]

                continue

            # Just one leaf prefix on previous organisation level
            if test == new_prefixes:
                print("case 2")
                self.generating_strategy[i]['generating_strategy'] = [new_prefixes]

                continue

            if test > 1:
                print("case 3")
                tmp = [int(test) for _ in range(leafs - 1)]
                tmp.append(new_prefixes - len(tmp)*int(test))
                self.generating_strategy[i]['generating_strategy'] = tmp

                continue

            if test < 1:
                print("case 4")
                self.generating_strategy[i]['generating_strategy'] = [1 for _ in range(new_prefixes)]

                continue

    def group_by_length(self, distribution: Dict) -> List:

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

    @staticmethod
    def generate_new_bits(current_prefix_depth: int, new_prefix_depth: int) -> str:
        """

        :param current_prefix_depth:
        :param new_prefix_depth:
        :return:
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
        """
        :param prefix_string:
        :return:
        """
        parsed_address = {'prefix': prefix_string[:prefix_string.find('/')],
                          'length': int(prefix_string[prefix_string.find('/') + 1:])}

        hex_prefix = ipaddress.IPv6Address(parsed_address['prefix'])

        binary_prefix = "".join(format(x, '08b') for x in bytearray(hex_prefix.packed))

        return binary_prefix[:parsed_address['length']]
