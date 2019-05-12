# from V6Gene.Trie import Trie
#
# binary_trie = Trie.Trie()
# binary_trie.set_root_as_prefix()
#
# # Add right part of binary trie
# binary_trie.add_node('001')
# binary_trie.add_node('01')
# binary_trie.add_node('110')
# binary_trie.add_node('111')
#
# binary_trie.preorder(binary_trie.root_node, "statistic")
#
# # print(binary_trie.prefix_leaf_nodes)
# # print(binary_trie.prefix_nodes)
#
# new_prefixes_param = 100
#
#
# def check_depth_distribution(trie: Trie, new_depth_distribution: dict):
#     # Number of new prefixes depends on :param new_dept_distribution
#     new_prefixes_num = 0
#     current_depth_distribution = trie.prefix_nodes
#
#     for depth, prefixes_num in new_depth_distribution.items():
#         current_value = current_depth_distribution.get(depth)
#
#         if prefixes_num < 0:
#             raise ValueError("Number of prefixes can't be less than zero")
#
#         if depth < 0:
#             raise ValueError("Level value can't be less than zero")
#
#         if current_value is None:  # level doesn't exist in trie
#             current_value = 0
#             new_prefixes_num += prefixes_num
#
#         if prefixes_num - current_value < 0:
#             raise ValueError("Number of prefixes on generated depth can't be less than current ")
#
#         if prefixes_num - current_value > 0 and not trie.get_depths(depth):
#             raise ValueError(f"There is no leaf prefixes in trie for generate new prefixes on {depth} depth")
#
#         new_prefixes_num += prefixes_num - current_value
#
#     if new_prefixes_num > new_prefixes_param:
#         raise ValueError("Generated prefixes num is greater than expected")
#
# # Need fix -> if depth 1 = 1(FIXED_ but need tests)
# check_depth_distribution(binary_trie,  {0: 1,
#         1: 0,
#         2: 1,
#         3: 4,
#         4: 2,
#         5: 0,
#         6: 2,
#         })


test = {16:1,
17:0,
18:0,
19:2,
20:12,
21:4,
22:6,
23:5,
24:20,
25:6,
26:15,
27:17,
28:107,
29:2557,
30:231,
31:147,}

print(sum(test.values()))