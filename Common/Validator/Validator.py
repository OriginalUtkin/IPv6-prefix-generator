import argparse
import ipaddress

from Common.Abstract.AbstractHelper import AbstractHelper
from typing import List


class InputArgumentsValidator:

    @staticmethod
    def validate_file(path, modifier) -> bool:
        """
        Check if file exists and it is readable (for input file) and writable (for output)
        :param path: path to the dataset or prefix set file
        :param modifier: additional flag which used for check if file is readable or writable
        :return: true in case that file could be used (according to modifier). False otherwise
        """
        try:
            with open(path, modifier):
                return True

        except IOError:
            return False

    @staticmethod
    def validate_prefix_quantity(value) -> int:
        """
        Validate quantity of prefixes is set by prefix_quantity input argument
        :raises ArgumentTypeError in case if value of argument is not correct
        :param value converted from string to integer number of prefixes for generating
        """

        try:
            value = int(value)

            if value < 0:
                raise argparse.ArgumentTypeError("Prefix quantity isn't represented by positive number")

        except ValueError:
            raise

        return value

    @staticmethod
    def parse_depth_distribution(value):
        """

        :param value:
        :return:
        """
        parsed = value.split(',')
        result = {key: 0 for key in range(65)}

        for value in parsed:
            separated_value = value.split(':')

            if int(separated_value[0]) > 64:
                raise argparse.ArgumentError("Value of depth cannot be greater than 64")

            result[int(separated_value[0])] = int(separated_value[1])

        return result

    @staticmethod
    def parse_level_distribution(value) -> int:
        """
        Get the string which represents level distribution and find the maximum value of level
        :param value: string representation of level distribution
        :raises ValueError in case if level value couldn't be use
        :return: integer value, maximum level of prefix in trie structure
        """
        max_level = int(value)

        if max_level < 0:
            raise ValueError("Value of maximum possible level cannot be less than 0")

        return max_level

    @staticmethod
    def parse_depth_distribution_file(path):
        """
        Parse input file with depth distribution
        :param path: path to the file with distribution
        :return: dictionary with depth distribution prefixes
        """
        try:
            with open(path) as file:
                file_data = file.read()

                return InputArgumentsValidator.parse_depth_distribution(file_data)

        except Exception:
            raise

    @staticmethod
    def read_seed_file(seed_file) -> List[str]:
        """
        Read input prefix seed file. During the reading check if prefix is valid (has a prefix len greater than 12
        (via allocation policy) and less than 64 (via allocation policy)). After that convert prefix to binary form (use
        string for end representation of binary form) and save converted prefix to set.
        :param seed_file: sed file with prefixes
        :return: filtered list with all prefixes in string format sorted by length
        """
        verified_addresses = set()

        with open(seed_file, 'r') as fp:
            # read file line by line
            for line in fp:
                address = line.rstrip('\n')

                # separate line to list which contains address and prefix length
                separated_line = address.split('/')

                try:
                    _ = ipaddress.IPv6Address(separated_line[0])
                    prefix_len = int(separated_line[1])

                    # prefix value belongs to the interval <0, 64>
                    if prefix_len < 12 or prefix_len > 64:
                        continue

                    verified_addresses.add(AbstractHelper.get_binary_prefix(address))

                # Prune invalid prefixes
                except ipaddress.AddressValueError:
                    continue

            # Prune redundant prefixes
            return sorted(verified_addresses, key=len)