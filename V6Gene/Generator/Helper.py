from typing import Dict, List
from Common.Abstract.AbstractHelper import AbstractHelper
import attr


# TODO: Implement AbstractHelper interface
class Helper(AbstractHelper):

    leafs_prefixes = attr.ib(factory=dict, type=dict)

    # Helper structure which contains a number of prefixes on organisation levels for random generating process
    distribution_random_plan = [
        {'interval': [12, 32], 'generated_info': {}},
        {'interval': [32, 48], 'generated_info': {}},
        {'interval': [48, 64], 'generated_info': {}},
        {'interval': [64, 65], 'generated_info': {}}
    ]

    # Generating strategy which contains number of prefixes which will be generated from prefix node in trie traversal generating process
    generating_strategy = [
        {'interval': [12, 32], 'generating_strategy': None},
        {'interval': [32, 48], 'generating_strategy': None},
        {'interval': [48, 64], 'generating_strategy': None},
        {'interval': [64, 65], 'generating_strategy': None}
    ]

    def create_distributing_plan(self) -> None:
        """Initialize distribution plan variable.
        :return: None
        """
        for prefix_depth, prefix_num in self.final_depth_distribution.items():

            new_prefix_num = prefix_num - self.start_depth_distribution.get(prefix_depth)

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
        """Return organisation depth level for particular depth.

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

    def create_distributing_strategy(self, prefix_leaf_nodes: Dict) -> None:
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
            leafs = float(new_prefixes / leafs)

            # number of leaf prefixes the same as number of prefixes on following organisation level
            if leafs == 1:
                self.generating_strategy[i]['generating_strategy'] = [1 for _ in range(int(leafs))]

                continue

            # Just one leaf prefix on previous organisation level
            if leafs == new_prefixes:
                self.generating_strategy[i]['generating_strategy'] = [new_prefixes]

                continue

            if leafs > 1:
                tmp = [int(leafs) for _ in range(int(leafs) - 1)]
                tmp.append(new_prefixes - len(tmp)*int(leafs))
                self.generating_strategy[i]['generating_strategy'] = tmp

                continue

            if leafs < 1:
                self.generating_strategy[i]['generating_strategy'] = [1 for _ in range(new_prefixes)]

                continue
