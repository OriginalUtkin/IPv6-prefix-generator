from typing import Dict, List
import attr


class Helper:

    start_depth_distribution = attr.ib(factory=dict, type=dict)
    final_depth_distribution = attr.ib(factory=dict, type=dict)

    _intervals = {0: [11, 31], 1: [31, 47], 2: [47, 63], 3: [63, 64]}

    distribution_plan = [
        {'interval': [11, 31], 'generated_info': {}},
        {'interval': [31, 47], 'generated_info': {}},
        {'interval': [47, 63], 'generated_info': {}},
        {'interval': [63, 64], 'generated_info': {}}
    ]

    generating_strategy = [
        {'interval': [11, 31], 'generating_strategy': None},
        {'interval': [31, 47], 'generating_strategy': None},
        {'interval': [47, 63], 'generating_strategy': None},
        {'interval': [63, 64], 'generating_strategy': None}
    ]

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

    def create_distributing_plan(self):
        """Initialize distribution plan variable.
        :return: None
        """
        for key, value in self.final_depth_distribution.items():

            prefix_num = value - self.start_depth_distribution.get(key, 0)

            if prefix_num == 0:
                continue
            else:
                for i in range(len(self.distribution_plan)):
                    if self.distribution_plan[i]['interval'][0] <= key < self.distribution_plan[i]['interval'][1]:
                        self.distribution_plan[i]['generated_info'][key] = prefix_num

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
