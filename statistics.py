import Common.Abstract.AbstractHelper as tt
import matplotlib.pyplot as plt
import numpy as np
from Common.Abstract.AbstractTrie import AbstractTrie
from IPv6Gene.Generator.Helper import Helper

from V6Gene.Trie.Trie import Trie
from Common.Validator.Validator import InputArgumentsValidator
from typing import List, Dict


def bit_distribution(bit_value, prefix_set, set_name) -> None:
    """
    Create graphs according to bit distribution for particular dataset. More info could be found in
    Abstract.AbstractHelper.get_bit_position. Same as method in abstract trie class this method is unused
    :param bit_value: analysing bit value
    :param prefix_set: input prefix set with prefixes which will be used for analysing process
    :param set_name: folder name which will be used for storing output graph
    :return: None
    """
    fig = plt.figure()
    ax1 = fig.add_subplot(1, 1, 1)

    result = tt.AbstractHelper.get_bit_position(bit_value, prefix_set)

    xs = []
    ys = []

    for key, value in result.items():
        xs.append(key)
        ys.append(value)

    ax1.clear()
    ax1.plot(xs, ys, marker='x', mew=0.4, linewidth=0.6, color='b')
    plt.grid(linewidth=0.3)
    plt.xticks(np.arange(0, 65, 4))
    plt.yticks(np.arange(0, 105, 5))

    plt.xlabel("Pozice bitu")
    plt.ylabel("Pravděpodobnost výskytu [%]")

    plt.savefig(f"statistics/{set_name}/bit_distribution.png", format='png', dpi=850)

    plt.show()


def depth_distribution_graph(distribution: Dict, set_name: str) -> None:
    """
    Get statistics and create output graph according to depth distribution of prefix nodes
    :param distribution: output distribution
    :param set_name: path to the folder for saving output graph
    :return: None
    """
    fig = plt.figure()
    ax1 = fig.add_subplot(1,1,1)

    xs = []
    ys = []

    convert_to_percent = {key: 0 for key in range(0, 64)}
    all_prefixes = sum(distribution.values())
    for i in range(len(convert_to_percent)):
        number_of_prefixes = distribution[i]
        convert_to_percent[i] = number_of_prefixes / all_prefixes * 100

    for key, value in convert_to_percent.items():
        xs.append(key)
        ys.append(value)

    ax1.clear()
    ax1.bar(xs, ys, color='b')
    plt.grid(linewidth=0.3)
    plt.xticks(np.arange(0, 65, 4))
    plt.yticks(np.arange(0, 105, 5))

    plt.xlabel("Délka prefixu")
    plt.ylabel("Počet prefixů [%]")

    plt.savefig(f"statistics/{set_name}/depth_distribution.png", format='png', dpi=850)

    plt.show()


def get_prefix_nodes_info(root_node) -> None:
    """
    Calculate number of nodes which were allocated without regarding the allocation policy. Final result will be printed
    to the standard output
    :param root_node: pointer to the root node in trie structure, which represents address sapce
    :return: None. Just print final result
    """
    helper = Helper()
    if not root_node:
        return

    node_path = list()
    node_path.append(root_node)
    prefixes = list()

    while node_path:

        node = node_path.pop()

        if node.prefix_flag:
            prefixes.append(node)

        if node.right_child:
            node_path.append(node.right_child)

        if node.left_child:
            node_path.append(node.left_child)

    incorrect_nodes = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0}

    for prefix_node in prefixes:

        full_prefix_path = AbstractTrie.get_just_prefix_path(prefix_node)[1:]

        org_level = helper.get_organisation_level_by_depth(prefix_node.depth)

        if len(full_prefix_path) == 0:
            incorrect_nodes[org_level] += 1
            continue

        if org_level != 4:
            converted_to_org_level = [helper.get_organisation_level_by_depth(n.depth) for n in full_prefix_path if org_level - helper.get_organisation_level_by_depth(n.depth) == 1 ]
        else:
            converted_to_org_level = [helper.get_organisation_level_by_depth(n.depth) for n in full_prefix_path if org_level - helper.get_organisation_level_by_depth(n.depth) == 1 or org_level - helper.get_organisation_level_by_depth(n.depth == 2) ]

        if not converted_to_org_level:
            incorrect_nodes[org_level] += 1

    print(f"Number of nodes were allocated incorrectly: {incorrect_nodes}")


def create_stats(output_prefixes: List[str], name: str, root_node) -> None:
    """
    This method used for creating statistic information about dataset and run the same tests as __main__
    :param output_prefixes: prefix dataset which will be tested
    :param name: path to the output folder which will be used for saving graphs
    :param root_node: pointer to the root node
    :return: None
    """
    depth_distribution = {key: 0 for key in range(65)}

    get_prefix_nodes_info(root_node)

    for single_prefix in output_prefixes:
        prefix_len = int(single_prefix.split('/')[1])
        depth_distribution[prefix_len] += 1

    depth_distribution_graph(depth_distribution, name)

    level_distribution = AbstractTrie.level_stats(root_node)
    print(f"Level distribution in generated set: {level_distribution}")


def compare_memory() -> None:
    """
    Create graphs for comparing memory usage of generators.
    :return: None
    """
    number_of_prefixes = [68750, 150000, 250000, 450000]
    memory_v6Gene = [0.215, 0.470, 0.808, 1.41]
    memory_own = [0.500, 0.920, 1.55, 2.52]

    plt.plot(number_of_prefixes, memory_v6Gene, color='red', linewidth=1,
             marker='x', markerfacecolor='blue', markersize=12, label='V6Gene')

    plt.plot(number_of_prefixes, memory_own, color='blue', linewidth=1,
             marker='x', markerfacecolor='blue', markersize=12, label='Vlastní implementace')

    plt.xlim(0, 500000)
    plt.ylim(0, 3.5)

    plt.grid(linewidth=0.3)

    plt.xlabel('Počet adres')

    plt.ylabel('Spotřebovaná paměť [Gb]')
    plt.legend()
    plt.savefig(f"statistics/memory.png", format='png', dpi=850)


def time_complexity() -> None:
    """
    Create graphs for comparing time complexity of generators.
    :return: None
   """
    number_of_prefixes = [68750, 150000, 250000, 450000]
    v6gene_time = [6.43, 12.34, 21.11, 38.6]
    own_time = [6.96, 16.34, 28.1,47.42]

    plt.plot(number_of_prefixes, v6gene_time, color='red', linewidth=1,
             marker='x', markerfacecolor='blue', markersize=12, label='V6Gene')

    plt.plot(number_of_prefixes, own_time, color='blue', linewidth=1,
             marker='x', markerfacecolor='blue', markersize=12, label='Vlastní implementace')

    plt.xlim(0, 500000)
    plt.ylim(0, 60)

    plt.grid(linewidth=0.3)

    plt.xlabel('Počet adres')
    plt.ylabel('Spotřebovaný čas [s]')

    plt.legend()
    plt.savefig(f"statistics/time.png", format='png', dpi=850)


if __name__ == '__main__':
    prefix_sets = ['dataset2007','dataset2019']

    for current_set in prefix_sets:
        path = f"dataset/{current_set}"

        prefixes = InputArgumentsValidator.read_seed_file(path)

        binary_trie = Trie()
        depth_distribution_stats = {key: 0 for key in range(65)}

        for prefix in prefixes:
            depth_distribution_stats[len(prefix)] += 1
            binary_trie.add_node(prefix)

        depth_distribution_graph(depth_distribution_stats, current_set)

        level_distribution_stats = AbstractTrie.level_stats(binary_trie.root_node)
        print(level_distribution_stats)

