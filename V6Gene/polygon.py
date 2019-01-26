# проверить сколько  префиксов вообще необзодимо сгенерировать и проверить не больше ли оно чем параметр
prefixes = 10 # number of prefixes which we want generate
rgr = 2

current = {1: 1,
           2: 0,
           3: 1,
           4: 3}  # current number of prefix leaf or prefix nodes on levels. Before generate

want = {1: 1,
        2: 0,
        3: 1,
        4: 4,
        5: 2,
        6: 0,
        7: 2,
        }  # what we want to see as result
# Check if count prefixes in want dictionary equal to prefixes param
counter = 0
for key, value in want.items():
    current_value = current.get(key)

    if current_value is None:   # level doesn't exist in trie
        counter += value
        continue

    counter += value - current_value

# print(counter)

# Известно сколько перфиксов в дереве после построения. Известно сколько мы хотим новых префиксов.
current_prefixes_in_trie = 0
for value in current.values():
    current_prefixes_in_trie+= value

will_generate_by_depth = 0
for value in want.values():
    will_generate_by_depth+= value

print(f"Before generate. Now in trie {current_prefixes_in_trie}")
print(f"after generate by depth {will_generate_by_depth}")

after_gen = current_prefixes_in_trie + prefixes
print(f"After generate prefixes in trie {after_gen}")


def check1(after_generate, want_generate):
    if after_generate - want_generate < 0:
        raise ValueError("we cant generate too much")


check1(after_gen, will_generate_by_depth)




