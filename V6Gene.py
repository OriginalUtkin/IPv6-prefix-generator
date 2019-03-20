from V6Gene.Generator.v6Generator import V6Generator

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

    parsed = value.split(',')
    result = {key: 0 for key in range(6)}

    for value in parsed:
        separated_value = value.split(':')
        result[int(separated_value[0])] = int(separated_value[1])

    return result


def validate_rgr(value):
    """

    :param value:
    :return:
    """

    try:
        value = float(value)

        if value < 0:
            raise argparse.ArgumentTypeError("RGR value should be a non-negative value")

        if value > 100:
            raise argparse.ArgumentTypeError("RGR value can't be greater than 100")

        if math.isnan(value) or math.isinf(value):
            raise argparse.ArgumentTypeError("RGR value is NaN or Inf value")

    except ValueError:
        raise

    if value < 1:
        value *= 100

    return value


def parse_depth_distribution_file(path):
    """

    :param path:
    :return:
    """
    with open(path) as file:
        file_data = file.read()

        return parse_depth_distribution(file_data)


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

    parser.add_argument('--input', required=True, help="Defines a path to input file, which contains seed file with prefixes for "
                                                       "building binary trie")

    parser.add_argument('--output', help="Defines a path to output file for printing generated prefixes")

    parser.add_argument('--prefix_quantity', required=True, type=validate_prefix_quantity, help="Defines number of prefixes to "
                                                                                                "generate. Integer positive value")

    parser.add_argument('--rgr', required=True, type=validate_rgr, help="Defines as the ratio of the number of prefixes"
                                                                        " to be generated without regarding to the "
                                                                        "seed prefix file to the number of all prefixes"
                                                                        " to be generated")

    parser.add_argument('--depth_distribution', type=parse_depth_distribution, help="Defines a distribution by depth")

    parser.add_argument('--level_distribution', required=True, type=parse_level_distribution, help="Defines distribution by level")

    parser.add_argument('--depth_distribution_path', type=parse_depth_distribution_file, help="Depth to the depth distribution parameter file which contains data ")

    return vars(parser.parse_args())


if __name__ == "__main__":

    parsed_arguments = parse_args()

    if not parsed_arguments.get("depth_distribution_path", None) and not parsed_arguments.get("depth_distribution", None):
        raise argparse.ArgumentError("Argument depth distribution or depth distribution path is required")

    if parsed_arguments.get("depth_distribution_path", None) and parsed_arguments.get("depth_distribution", None):
        raise argparse.ArgumentError("Arguments depth_distribution_path and depth_distribution couldn't be combined")

    depth_distribution = parsed_arguments.get("depth_distribution_path") if \
        parsed_arguments.get("depth_distribution_path", None) else \
        parsed_arguments.get("depth_distribution")

    if parsed_arguments['input'] and not validate_file(parsed_arguments['input'], 'r'):
        print(parsed_arguments['input'])
        raise argparse.ArgumentError("Input seed file doesn't exist or is not readable")

    if parsed_arguments['output'] and not validate_file(parsed_arguments['output'], 'r+'):
        raise TypeError("Output file doesn't exist or is not writable")

    input_prefixes = read_seed_file(parsed_arguments['input'])

    generator = V6Generator(
        prefix_quantity=parsed_arguments['prefix_quantity'],
        rgr=parsed_arguments['rgr'],
        depth_distribution=depth_distribution,
        level_distribution=parsed_arguments['level_distribution'],
        input_prefixes=input_prefixes
    )

    new_prefixes = generator.start_generating()
