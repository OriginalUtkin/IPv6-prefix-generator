from IPv6Gene.Generator.v6Generator import V6Generator
import argparse
import ipaddress
import math


def validate_file(path, modifier):
    """
    Check if file exists and it is readable (for input file) and writable (for output)
    :param path:
    :param modifier:
    :return:
    """
    try:
        with open(path, modifier):
            return True

    except IOError:
        return False


def validate_prefix_quantity(value):
    """
    :param value
    """

    try:
        value = int(value)

        if value < 0:
            raise argparse.ArgumentTypeError("Prefix quantity isn't represented by positive number")

    except ValueError:
        raise

    return value


def parse_depth_distribution(value):
    parsed = value.split(',')
    result = {key: 0 for key in range(65)}

    for value in parsed:
        separated_value = value.split(':')

        if int(separated_value[0]) > 64:
            raise ValueError("Value of depth cannot be greater than 64")

        result[int(separated_value[0])] = int(separated_value[1])

    return result


def parse_level_distribution(value):

    max_level = int(value)

    if max_level < 0:
        raise ValueError("Value of maximum possible level cannot be less than 0")

    return max_level


def read_seed_file(seed_file):
    """

    :param seed_file:
    :return:
    """
    verified_addresses = list()

    with open(seed_file, 'r') as fp:

        for line in fp:
            address = line.rstrip('\n')

            # separate line to list which contains address and prefix length
            separated_line = address.split('/')

            try:
                _ = ipaddress.IPv6Address(separated_line[0])
                prefix_len = int(separated_line[1])

                # prefix value belongs to the interval <0, 64>
                if prefix_len < 1 or prefix_len > 64:
                    continue

                verified_addresses.append(address)

            # Prune invalid prefixes
            except ipaddress.AddressValueError:
                continue

        # Prune redundant prefixes
        return set(verified_addresses)


def parse_args():
    """
    Prepare argparse object for working with input arguments
    :return: dictionary which has a following format -> input_argument_name: argument_value
    """

    parser = argparse.ArgumentParser(description="Arguments parser for IPv6 prefix generator")

    parser.add_argument('--input', required=True, help="Defines a path to input file, which contains seed prefixes for "
                                                       "building binary trie")

    parser.add_argument('--output', help="Defines a path to output file for printing generated prefixes")

    parser.add_argument('--prefix_quantity', required=True, type=validate_prefix_quantity, help="Defines number of prefixes to "
                                                                                                "generate. Integer positive value")

    parser.add_argument('--depth_distribution', required=True, type=parse_depth_distribution, help="Defines a distribution by depth")

    parser.add_argument('--max_level', required=True, type=parse_level_distribution, help="Defines maximum possible by level")

    return vars(parser.parse_args())


if __name__ == "__main__":

    parsed_arguments = parse_args()

    if parsed_arguments['input'] and not validate_file(parsed_arguments['input'], 'r'):
        raise argparse.ArgumentError("Input seed file doesn't exist or is not readable")

    if parsed_arguments['output'] and not validate_file(parsed_arguments['output'], 'r+'):
        raise TypeError("Output file doesn't exist or is not writable")

    input_prefixes = read_seed_file(parsed_arguments['input'])

    generator = V6Generator(
        prefix_quantity=parsed_arguments['prefix_quantity'],
        depth_distribution=parsed_arguments['depth_distribution'],
        max_level=parsed_arguments['max_level'],
        input_prefixes=input_prefixes
    )

    new_prefixes = generator.start_generating()
