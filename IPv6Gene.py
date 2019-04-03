from IPv6Gene.Generator.v6Generator import V6Generator
from  Abstract.AbstractHelper import AbstractHelper
import argparse
import ipaddress


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
    """

    :param value:
    :return:
    """
    parsed = value.split(',')
    result = {key: 0 for key in range(65)}

    for value in parsed:
        separated_value = value.split(':')

        if int(separated_value[0]) > 64:
            raise ValueError("Value of depth cannot be greater than 64")

        result[int(separated_value[0])] = int(separated_value[1])

    return result


def parse_level_distribution(value):
    """

    :param value:
    :return:
    """
    max_level = int(value)

    if max_level < 0:
        raise ValueError("Value of maximum possible level cannot be less than 0")

    return max_level


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
                if prefix_len < 1 or prefix_len > 64:
                    continue

                verified_addresses.add(AbstractHelper.get_binary_prefix(address))

            # Prune invalid prefixes
            except ipaddress.AddressValueError:
                continue

        # Prune redundant prefixes

        return sorted(verified_addresses, key=len)


def parse_args():
    """
    Prepare argparse object for working with input arguments
    :return: dictionary which has a following format -> input_argument_name: argument_value
    """

    parser = argparse.ArgumentParser(description="Arguments parser for IPv6 prefix generator")

    parser.add_argument('--input', required=True, help="Defines a path to input file, which contains seed prefixes for "
                                                       "building binary trie")

    parser.add_argument('--output', help="Defines a path to output file for printing generated prefixes")

    parser.add_argument('--prefix_quantity', required=True, type=validate_prefix_quantity, help="Defines number of "
                                                                                                "prefixes to generate. "
                                                                                                "Defined by integer "
                                                                                                "positive value")

    parser.add_argument('--depth_distribution', type=parse_depth_distribution, help="Defines a distribution by depth")

    parser.add_argument('--max_level', required=True, type=parse_level_distribution, help="Defines maximum possible by "
                                                                                          "level")

    parser.add_argument('--depth_distribution_path', type=parse_depth_distribution_file, help="Path to the file which "
                                                                                              "contains depth "
                                                                                              "distribution data")

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
        raise argparse.ArgumentError("Input seed file doesn't exist or is not readable")

    if parsed_arguments['output'] and not validate_file(parsed_arguments['output'], 'r+'):
        raise TypeError("Output file doesn't exist or is not writable")

    input_prefixes = read_seed_file(parsed_arguments['input'])

    print(f"[INFO] Number of seed prefixes {len(set(input_prefixes))}")

    generator = V6Generator(
        prefix_quantity=parsed_arguments['prefix_quantity'],
        depth_distribution=depth_distribution,
        max_level=parsed_arguments['max_level'],
        input_prefixes=input_prefixes
    )
    print(f"Start binary trie level is {generator._binary_trie.trie_level}")

    new_prefixes = generator.start_generating()

    for prefix in new_prefixes:
        print(prefix)

    print(f"Number of prefixes after generating {len(new_prefixes)}")
    print(f"Result binary trie level is {generator._binary_trie.trie_level}")

    if parsed_arguments['output']:
        with open(parsed_arguments['output'], 'a') as file:
            for prefix in new_prefixes:
                file.write(prefix + '\n')
