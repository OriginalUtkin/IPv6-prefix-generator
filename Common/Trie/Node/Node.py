# was developed by Utkin Kirill


import attr

from typing import Optional


@attr.s
class Node:
    """
    Class that represents a node in binary trie
    """
    node_value = attr.ib(type=Optional[int])
    depth = attr.ib(type=int)

    left_child = attr.ib(default=None)
    right_child = attr.ib(default=None)
    prefix_flag = attr.ib(default=False, type=bool)
    level = attr.ib(default=0, type=int)
    path = attr.ib(default=None)
    is_visited = attr.ib(default=False, type=bool)
    allow_generate = attr.ib(default=True, type=bool)

    # is used just for debug purpose
    name = attr.ib(default=None, type=str)

    @node_value.validator
    def node_value_validator(self, attribute, value):
        if value not in (None, '0', '1'):
            raise ValueError(f"node value has to be 0, 1 or None value. Get {value} ")

