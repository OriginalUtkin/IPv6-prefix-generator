from V6Gene.Trie import Trie
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
                if prefix_len < 0 or prefix_len > 64:
                    continue

                verified_addresses.append(address)

            # Prune invalid prefixes
            except ipaddress.AddressValueError:
                continue

        # Prune redundant prefixes
        return set(verified_addresses)


def get_binary_prefix(string):
    """

    :param string:
    :return:
    """
    parsed_address = {'prefix': string[:string.find('/')],
                      'length': int(string[string.find('/') + 1:])}

    hex_prefix = ipaddress.IPv6Address(parsed_address['prefix'])

    binary_prefix = "".join(format(x, '08b') for x in bytearray(hex_prefix.packed))

    return binary_prefix[:parsed_address['length']]


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

    parser.add_argument('--rgr', required=True, type=validate_rgr, help="Defines as the ratio of the number of prefixes"
                                                                        " to be generated without regarding to the "
                                                                        "seed prefix file to the number of all prefixes"
                                                                        " to be generated")


    # # TODO : ????
    # parser.add('--level')
    # parser.add('--depth')

    return vars(parser.parse_args())


if __name__ == "__main__":

    parsed_arguments = parse_args()

    if parsed_arguments['input'] and not validate_file(parsed_arguments['input'], 'r'):
        raise argparse.ArgumentError("Input seed file doesn't exist or is not readable")

    if parsed_arguments['output'] and not validate_file(parsed_arguments['output'], 'r+'):
        raise TypeError("Output file doesn't exist or is not writable")

    # Calculate number of prefixes that will be generated randomly (without seed prefix trie)
    randomly_generated = int(float(parsed_arguments['prefix_quantity']) * parsed_arguments['rgr'] / 100)

    # Calculate number of prefixes that will be generated by traversing of seed prefix trie
    spt_generated = parsed_arguments['prefix_quantity'] - randomly_generated

    binary_trie = Trie.Trie()

    input_prefixes = read_seed_file(parsed_arguments['input'])

    #  Construct the seed prefix trie
    for prefix in input_prefixes:
        binary_trie.add_node(get_binary_prefix(prefix))

    binary_trie.preorder(binary_trie.root_node)