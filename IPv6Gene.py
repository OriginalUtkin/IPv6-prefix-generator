# was developed by Utkin Kirill

import argparse
import statistics
import sys
import time

from Common.Validator.Validator import InputArgumentsValidator as validate
from IPv6Gene.Generator.v6Generator import V6Generator


def parse_args():
    """
    Prepare argparse object for working with input arguments
    :return: dictionary which has a following format -> input_argument_name: argument_value
    """

    parser = argparse.ArgumentParser(description="Arguments parser for IPv6 prefix generator")

    parser.add_argument('--input', required=True, help="Defines a path to input file, which contains seed prefixes for "
                                                       "building binary trie"
    )

    parser.add_argument('--output', help="Defines a path to output file for printing generated prefixes")

    parser.add_argument('--prefix_quantity', required=True, type=validate.validate_prefix_quantity, help="Number of prefixes in output dataset. "
                                                                                                "Defined by integer "
                                                                                                "positive value"
    )

    parser.add_argument('--depth_distribution', type=validate.parse_depth_distribution, help="Defines a distribution by depth. Sample depth distribution file could be found in distributions/depth_distribution folder")

    parser.add_argument('--max_level', required=True, type=validate.parse_level_distribution, help="Defines maximum possible node level in trie structure"

    )

    parser.add_argument('--depth_distribution_path', type=validate.parse_depth_distribution_file, help="Path to the file which "
                                                                                                        "contains depth distribution data. Example distribution file could be found "
                                                                                                        "in distributions/depth distribution folder"

    )

    parser.add_argument('--graph', action='store_true', required=False, help="Allow to create output depth and level distribution graph. Graph will "
                                                        "be saved to statistics folder"
    )

    parser.add_argument('--stats', action='store_true', required=False, help="Print information during the generating process")

    return vars(parser.parse_args())


def generator_start() -> None:

    start = time.time()
    try:
        parsed_arguments = parse_args()

    except Exception as exc:
        sys.exit(str(exc))

    if not parsed_arguments.get("depth_distribution_path", None) and not parsed_arguments.get("depth_distribution",
                                                                                              None):
        sys.exit("Argument depth distribution or depth distribution path is required")

    if parsed_arguments.get("depth_distribution_path", None) and parsed_arguments.get("depth_distribution", None):
        sys.exit("Arguments depth_distribution_path and depth_distribution couldn't be combined")

    depth_distribution = parsed_arguments.get("depth_distribution_path") if \
        parsed_arguments.get("depth_distribution_path", None) else \
        parsed_arguments.get("depth_distribution")

    if parsed_arguments['input'] and not validate.validate_file(parsed_arguments['input'], 'r'):
        sys.exit("Input seed file doesn't exist or is not readable")

    if parsed_arguments['output'] and not validate.validate_file(parsed_arguments['output'], 'r+'):
        sys.exit("Output file doesn't exist or is not writable")

    input_prefixes = validate.read_seed_file(parsed_arguments['input'])

    generator = V6Generator(
        prefix_quantity=parsed_arguments['prefix_quantity'],
        depth_distribution=depth_distribution,
        max_level=parsed_arguments['max_level'],
        input_prefixes=input_prefixes,
        stats=parsed_arguments['stats']
    )

    if parsed_arguments['stats']:
        print(f"[INFO] Number of prefixes in seed input file is {len(set(input_prefixes))}")
        print(f"[INFO] Number of prefixes in constructed binary trie is {generator.get_binary_trie_prefixes_num()}")
        print(f"[INFO] Constructed binary trie depth is {generator.get_binary_trie_depth()}")
        print(f"[INFO] Constructed binary trie level is {generator.get_binary_trie_level()}")

    new_prefixes = generator.start_generating()

    if parsed_arguments['graph']:
        statistics.create_stats(new_prefixes, 'ipv6gene', generator.get_root())

    if not parsed_arguments['output']:
        for prefix in new_prefixes:
            print(prefix)

    if parsed_arguments['stats']:
        print(f"[INFO] Number of prefixes after generating {len(new_prefixes)}")
        print(f"[INFO] Number of prefixes in constructed binary trie is {generator.get_binary_trie_prefixes_num()}")
        print(f"[INFO] Binary trie depth after generating is {generator.get_binary_trie_depth()}")
        print(f"[INFO] Binary trie level after generating is {generator.get_binary_trie_level()}")

    if parsed_arguments['output']:
        with open(parsed_arguments['output'], 'a') as file:
            for prefix in new_prefixes:
                file.write(prefix + '\n')

    end = time.time()

    if parsed_arguments['stats']:
        print(f"[INFO] Execution time: {end - start}")


if __name__ == "__main__":
    generator_start()
