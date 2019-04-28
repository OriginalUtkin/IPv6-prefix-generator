import Common.Abstract.AbstractHelper as tt
import matplotlib.pyplot as plt
import numpy as np
from Common.Abstract.AbstractHelper import AbstractHelper
from Common.Abstract.AbstractTrie import AbstractTrie

from V6Gene.Trie.Trie import Trie
from Common.Validator.Validator import InputArgumentsValidator
from typing import List


def bit_distribution(bit_value, prefix_set, set_name):
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
    plt.ylabel("Pravděpodobnost výskytu (%)")

    plt.savefig(f"stats_output/{set_name}/bit_distribution.png", format='png', dpi=850)

    plt.show()


def level_distribution(distribution, set_name):
    print(distribution)
    fig = plt.figure()
    ax1 = fig.add_subplot(1, 1, 1)

    xs = distribution.keys()
    y_pos = np.arange(len(distribution.keys()))
    ys = [100000, 10000, 1000, 100, 10, 1]
    plt.grid(linewidth=0.3)
    ax1.bar(xs, ys, align='center', alpha=0.5)
    plt.yticks(ys)

    plt.ylabel("Počet prefixu")
    plt.xlabel("Úroveň prefixu")

    plt.savefig(f"stats_output/{set_name}/level_distribution.png", format='png', dpi=1000)


def depth_distribution_graph(distribution, set_name):
    fig = plt.figure()
    ax1 = fig.add_subplot(1,1,1)

    xs = []
    ys = []

    convert_to_percent = {key: 0 for key in range(0, 64)}

    for i in range(len(convert_to_percent)):
        number_of_prefixes = distribution[i]
        convert_to_percent[i] = number_of_prefixes / len(prefixes) * 100

    for key, value in convert_to_percent.items():
        xs.append(key)
        ys.append(value)

    ax1.clear()
    ax1.bar(xs, ys, color='b')
    plt.grid(linewidth=0.3)
    plt.xticks(np.arange(0, 65, 4))
    plt.yticks(np.arange(0, 105, 5))

    plt.xlabel("Délka prefixu")
    plt.ylabel("Počet prefixu(%)")

    plt.savefig(f"stats_output/{set_name}/depth_distribution.png", format='png', dpi=850)

    plt.show()


def create_stats(output_prefixes: List[str], name: str, root_node):
    binary_prefixes = [AbstractHelper.get_binary_prefix(prefix) for prefix in output_prefixes]
    bit_distribution('1', binary_prefixes, name)
    # level_distribution_stats = AbstractTrie.level_stats(root_node)

if __name__ == '__main__':
    prefix_sets = ['dataset2007', 'dataset2019']

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
        level_distribution(level_distribution_stats, current_set)

        bit_distribution('1', prefixes, current_set)

    print()



