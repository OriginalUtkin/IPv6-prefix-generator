from Trie import Trie
import argparse
import ipaddress


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


def convert_hextet(hextet):
    """

    :param hextet:
    :return:
    """

    return ''.join([format(int(bin(int(symbol, 16))[2:], 2), '04b') for symbol in hextet])


def restore_hextet(hextet):
    """

    :param hextet:
    :return:
    """
    missing_bits = 4 - len(hextet)

    return ('0' * missing_bits) + hextet


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
    parsed_address = {'prefix':string[:string.find('/')],
                      'length':int(string[string.find('/')+1:])}

    hextets = parsed_address['prefix'].split(':')

    binary_prefix= []

    for hextet in hextets:

        if len(hextet) != 4:
            hextet = restore_hextet(hextet)

        binary_prefix.append(convert_hextet(hextet))

    binary_prefix = ''.join(binary_prefix)

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

    # TODO: change type
    # parser.add_argument('--prefix_quantity', required = True, type='' ,help="")

    # # TODO: change type
    # parser.add_argument('--rgr', required = True, type=, help="")
    #

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


    # current = binary_trie.root_node
    # iter = 0
    #
    # while True:
    #
    #     if not current.left and not current.right:
    #         print("Trie end")
    #         break
    #     else:
    #         if current.left:
    #             print(str(iter) + '->left')
    #             current = current.left
    #             iter += 1
    #             continue
    #
    #         if current.right:
    #             print(str(iter) + '->right')
    #             current = current.right
    #             iter += 1
    #             continue

    # prefix = "2407:8800:1::/35"
    # print(get_binary_prefix(prefix))
    # binary_trie.add_node(get_binary_prefix(prefix))
    #

    #


    # # Add left part of binary trie
    # binary_trie.add_node('0')
    # binary_trie.add_node('00')
    # binary_trie.add_node('000')
    # binary_trie.add_node('0000')
    # binary_trie.add_node('00000')
    # binary_trie.add_node('00000000')
    # binary_trie.add_node('00000001')
    #
    # # Add right part of binary trie
    # binary_trie.add_node('1')
    # binary_trie.add_node('11')
    # binary_trie.add_node('111')
    # binary_trie.add_node('1111')
    # binary_trie.add_node('110')
    # binary_trie.add_node('1100')
    # binary_trie.add_node('11000')

    # binary_trie.add_node('0')
    # binary_trie.add_node('00')
    # binary_trie.add_node('01')
    # binary_trie.add_node('010')
    # binary_trie.add_node('011')
    # binary_trie.add_node('1')
    # binary_trie.add_node('11')
    # binary_trie.add_node('110')
    binary_trie.preorder(binary_trie.root_node)

    # binary_trie.set_leaf()
    # print(binary_trie.leaf_nodes)









