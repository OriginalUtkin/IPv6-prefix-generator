from V6Gene.Trie import Trie
import argparse
import ipaddress
import math


def validate_file(path, modifier):
    """
    Check if file path exists and is readable and writable
    :param path:
    :param modifier:
    :return:
    """
    try:
        with open(path, modifier):
            return True

    except IOError:
        return False


def validate_int(value):
    """
    :param value
    """

    try:
        amount = int(value)

        if amount < 0:
            raise argparse.ArgumentTypeError("Value isn't represented by positive number")

    except ValueError:
        raise

    return value


def validate_rgr(value):
    """

    :param value:
    :return:
    """
    # TODO : chang eit to int and use validate int

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

    return value


def read_input(input_file):
    """

    :param input_file:
    :return:
    """
    verified_addresses = list()

    with open(input_file, 'r') as fp:

        for line in fp:
            address = line.rstrip('\n')

            # separate line to list which contains address and prefix length
            separated_line = address.split('/')

            try:
                _ = ipaddress.IPv6Address(separated_line[0])
                prefix_len = int(separated_line[1])

                # prefix value belongs to the interval <1, 64>
                if prefix_len < 3 or prefix_len > 64:
                    raise ValueError

                verified_addresses.append(address)

            except (ipaddress.AddressValueError, ValueError):
                continue

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

    parser.add_argument('--input', required=True, help="Input file, which contains seed prefixes "
                                                       "for building binary trie")
    parser.add_argument('--output', help="")

    parser.add_argument('--prefix_quantity', required=True, type=validate_int, help="")

    parser.add_argument('--rgr', required=True, type=validate_rgr, help="")

    # # TODO : ????
    # parser.add('--level')
    # parser.add('--depth')

    return vars(parser.parse_args())


if __name__ == "__main__":

    parsed_arguments = parse_args()

    if parsed_arguments['input'] and not validate_file(parsed_arguments['input'], 'r'):
        raise argparse.ArgumentError("input seed file doesn't exist or is not readable")

    if parsed_arguments['output'] and not validate_file(parsed_arguments['output'], 'r+'):
        raise TypeError("Output file doesn't exist or is not writable")

    binary_trie = Trie.Trie()

    input_prefixes = read_input(parsed_arguments['input'])

    for prefix in input_prefixes:
        binary_trie.add_node(get_binary_prefix(prefix))


    binary_trie.preorder(binary_trie.root_node)









