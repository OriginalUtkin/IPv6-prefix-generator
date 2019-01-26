import attr

from typing import Union


@attr.s
class Node:
    node_value = attr.ib(type=Union[None, int])
    depth = attr.ib(type=int)

    left_child = attr.ib(default=None)
    right_child = attr.ib(default=None)

    prefix_flag = attr.ib(default=False, type=bool)
    level = attr.ib(default=0, type=int)

    @node_value.validator
    def node_value_validator(self, attribute, value):
        if value not in (None, '0', '1'):
            raise ValueError(f"node value has to be 0, 1 or None value. Get {value} ")
