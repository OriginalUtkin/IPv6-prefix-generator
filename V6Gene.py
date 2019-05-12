from V6Gene.Generator.v6Generator import V6Generator
from Common.Validator.Validator import InputArgumentsValidator as validator
from typing import Dict

import argparse
import time
import math
import sys
import statistics


def validate_rgr(value: str) -> float:
    """
    Validate input value of rgr param
    :param value: input value of rgr parameter
    :raises ArgumentTypeError in case, when value incorrect
    :return: converted value which could be used in generator
    """

    try:
        value = float(value)

        if value < 0:
            raise argparse.ArgumentTypeError("RGR value should be a non-negative value")

        if value > 1:
            raise argparse.ArgumentTypeError("RGR value can't be greater than 100")

        if math.isnan(value) or math.isinf(value):
            raise argparse.ArgumentTypeError("RGR value is NaN or Inf value")

    except ValueError:
        raise

    return value


def parse_level_distribution(value: str) -> Dict:

    try:
        parsed = value.split(',')
        result = {key: 0 for key in range(6)}

        for value in parsed:
            separated_value = value.split(':')
            result[int(separated_value[0])] = int(separated_value[1])

        return result

    except Exception:
        raise argparse.ArgumentTypeError("Cannot parse level_distribution. Check if value of argument is correct or use level_distribution_parse")


def parse_level_distribution_file(path: str) -> Dict:
    """

    :param path:
    :return:
    """
    with open(path) as file:
        file_data = file.read()

        return parse_level_distribution(file_data)


def parse_args() -> Dict[str, str]:
    """
    Prepare argparse object for working with input arguments
    :return: dictionary which has a following format -> input_argument_name: argument_value
    """

    parser = argparse.ArgumentParser(description="Arguments parser for IPv6 prefix generator.")

    parser.add_argument('--input', required=True, help="Defines a path to input file, which contains seed file "
                                                       "with prefixes for building binary trie")

    parser.add_argument('--output', help="Defines a path to output file for printing generated prefixes. If isn't set"
                                         "prefixes will be print to standard output")

    parser.add_argument('--prefix_quantity', required=True, type=validator.validate_prefix_quantity, help="Defines number of "
                                                                                                "prefixes to generate."
                                                                                                "Should be defined by "
                                                                                                "positive integer value"
                        )

    parser.add_argument('--rgr', required=True, type=validate_rgr, help="Defines as the ratio of the number of prefixes"
                                                                        " to be generated without regarding to the "
                                                                        "seed prefix file to the number of all prefixes"
                                                                        " to be generated")

    parser.add_argument('--depth_distribution', type=validator.parse_depth_distribution, help="Defines a distribution by depth. "
                                                                                    "Can't be combined with "
                                                                                    "depth_distribution_path argument")

    parser.add_argument('--level_distribution', type=parse_level_distribution, help="Defines distribution by level."
                                                                                    " Can't be combined with "
                                                                                    "level_distribution_path argument."
                                                                                    "If not given, "
                                                                                    "level_distribution_path is "
                                                                                    "required")

    parser.add_argument('--depth_distribution_path', type=validator.parse_depth_distribution_file, help="Specify path to the "
                                                                                              "file which contains "
                                                                                              "depth distribution "
                                                                                              "data. Sample file could "
                                                                                              "be found in the "
                                                                                              "distributions/V6Gene "
                                                                                              "folder. This argument "
                                                                                              "can't be combined with "
                                                                                              "depth_distribution "
                                                                                              "argument. If not given"
                                                                                              ", depth_distribution is "
                                                                                              "required")

    parser.add_argument('--level_distribution_path', type=parse_level_distribution_file, help="Path to the file which "
                                                                                         "contains level distribution "
                                                                                         "data. Sample file could be "
                                                                                         "found in the "
                                                                                         "distributions/V6Gene folder. "
                                                                                         "This argument can't be "
                                                                                         "combined with level_"
                                                                                         "distribution argument. If not"
                                                                                         " given, level_distribution is"
                                                                                         " required")

    parser.add_argument('--graph', action='store_true', required=False, help="Allow to create output depth distribution graph. Graph will "
                                                                             "be saved to stats_output folder. After creating graph, "
                                                                             "additional information as level distribution will be printed"
                                                                             "to output."
    )

    parser.add_argument('--stats', action='store_true', required=False, help="Print information during the generating "
                                                                             "process")

    return vars(parser.parse_args())


def start_generator() -> None:
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

    if not parsed_arguments.get("level_distribution_path", None) and not parsed_arguments.get("level_distribution",
                                                                                              None):
        sys.exit("Argument level_distribution or level_distribution_path is required")

    if parsed_arguments.get("level_distribution_path", None) and parsed_arguments.get("level_distribution", None):
        sys.exit("Arguments level_distribution_path and level_distribution couldn't be combined")

    level_distribution = parsed_arguments.get("level_distribution_path") if \
        parsed_arguments.get("level_distribution_path", None) else \
        parsed_arguments.get("level_distribution")

    if parsed_arguments['input'] and not validator.validate_file(parsed_arguments['input'], 'r'):
        sys.exit("Input seed file doesn't exist or is not readable")

    if parsed_arguments['output'] and not validator.validate_file(parsed_arguments['output'], 'r+'):
        sys.exit("Output file doesn't exist or is not writable")

    input_prefixes = validator.read_seed_file(parsed_arguments['input'])

    generator = V6Generator(
        prefix_quantity=parsed_arguments['prefix_quantity'],
        rgr=parsed_arguments['rgr'],
        depth_distribution=depth_distribution,
        level_distribution=level_distribution,
        input_prefixes=input_prefixes
    )

    if parsed_arguments['stats']:
        print(f"[INFO] Number of prefixes in seed input file is {len(set(input_prefixes))}")
        print(f"[INFO] Constructed binary trie depth is {generator._binary_trie.trie_depth}")
        print(f"[INFO] Constructed binary trie level is {generator._binary_trie.trie_level}")

    new_prefixes = generator.start_generating()

    if parsed_arguments['graph']:
        statistics.create_stats(new_prefixes, 'v6gene', generator.get_root())

    if not parsed_arguments['output']:
        for prefix in new_prefixes:
            print(prefix)

    if parsed_arguments['stats']:
        print(f"[INFO] Number of prefixes after generating {len(new_prefixes)}")
        print(f"[INFO] Binary trie depth after generating is {generator._binary_trie.trie_depth}")
        print(f"[INFO] Binary trie level after generating is {generator._binary_trie.trie_level}")

    if parsed_arguments['output']:
        with open(parsed_arguments['output'], 'a') as file:
            for prefix in new_prefixes:
                file.write(prefix + '\n')

    end = time.time()

    if parsed_arguments['stats']:
        print(end - start)


if __name__ == "__main__":
    start_generator()
