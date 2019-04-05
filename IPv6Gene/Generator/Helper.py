from Common.Abstract.AbstractHelper import AbstractHelper


class Helper(AbstractHelper):

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

                if org_lvl == 1:
                    self.distribution_random_plan[0]['generated_info'][prefix_depth] = new_prefix_num

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

