from Common.Abstract.AbstractHelper import AbstractHelper


class Helper(AbstractHelper):

    # Helper structure which contains a number of prefixes on organisation levels for random generating process
    distribution_random_plan = [
        {'interval': [12, 32], 'generated_info': {}},
    ]

    bit_distribution = {1: 0,
                        2: 0,
                        3: 23900,
                        4: 0,
                        5: 8771,
                        6: 9851,
                        7: 13154,
                        8: 0,
                        9: 0,
                        10: 2,
                        11: 1512,
                        12: 215,
                        13: 185,
                        14: 6606,
                        15: 6893,
                        16: 11351,
                        17: 6247,
                        18: 7293,
                        19: 6949,
                        20: 7972,
                        21: 9587,
                        22: 10837,
                        23: 9310,
                        24: 10185,
                        25: 8107,
                        26: 8925,
                        27: 7524,
                        28: 7415,
                        29: 6711,
                        30: 3475,
                        31: 2235,
                        32: 2983,
                        33: 4031,
                        34: 3489,
                        35: 4373,
                        36: 3897,
                        37: 2492,
                        38: 2639,
                        39: 3063,
                        40: 3145,
                        41: 2345,
                        42: 2909,
                        43: 3401,
                        44: 4061,
                        45: 3394,
                        46: 4010,
                        47: 3736,
                        48: 4138,
                        49: 91,
                        50: 58,
                        51: 132,
                        52: 176,
                        53: 96,
                        54: 137,
                        55: 161,
                        56: 289,
                        57: 62,
                        58: 100,
                        59: 136,
                        60: 166,
                        61: 175,
                        62: 244,
                        63: 288,
                        64: 322
                        }

    current_bit_distribution = { 1:0,
                                 2:0,
                                 3:499,
                                 4:0,
                                 5:0,
                                 6:0,
                                 7:0,
                                 8:0,
                                 9:0,
                                 10:0,
                                 11:0,
                                 12:0,
                                 13:0,
                                 14:0,
                                 15:0,
                                 16:499,
                                 17:1,
                                 18:71,
                                 19:3,
                                 20:109,
                                 21:234,
                                 22:243,
                                 23:237,
                                 24:222,
                                 25:232,
                                 26:232,
                                 27:239,
                                 28:236,
                                 29:228,
                                 30:7,
                                 31:18,
                                 32:15,
                                 33:10,
                                 34:8,
                                 35:9,
                                 36:5,
                                 37:6,
                                 38:6,
                                 39:8,
                                 40:7,
                                 41:4,
                                 42:3,
                                 43:7,
                                 44:9,
                                 45:11,
                                 46:5,
                                 47:7,
                                 48:9,
                                 49:0,
                                 50:0,
                                 51:0,
                                 52:0,
                                 53:0,
                                 54:0,
                                 55:0,
                                 56:0,
                                 57:0,
                                 58:0,
                                 59:0,
                                 60:0,
                                 61:0,
                                 62:0,
                                 63:0,
                                 64:0
                                }

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

    def generate_new_bits(self, current_prefix_depth: int, new_prefix_depth: int) -> str:

        generated_bits = AbstractHelper.generate_new_bits(current_prefix_depth, new_prefix_depth)
        bit_vector = {key: None for key in range(current_prefix_depth+1, new_prefix_depth+1)}

        for key, value in zip(bit_vector.keys(), generated_bits):
            bit_vector[key] = value

        for key, value in bit_vector.items():
            if value == '1' and self.current_bit_distribution[key] + 1 > self.bit_distribution[key]:
                bit_vector[key] = '0'
            else:
                if value == '1':
                    self.current_bit_distribution[key] += 1

        return "".join(bit_vector.values())

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

