import attr

from IPv6Gene.Trie import Trie
from Common.Exceptions.Exceptions import PrefixAlreadyExists, MaximumLevelException
from Common.Abstract.AbstractHelper import AbstractHelper
from  IPv6Gene.Generator.Helper import Helper


@attr.s
class RandomGenerator:
    binary_trie = attr.ib(type=Trie)
    helper = attr.ib(type=Helper)
    distribution_plan = attr.ib(factory=dict, type=dict)

    def random_generate(self) -> None:
        IANA = '0010'
        generated_randomly = 0

        for org_level in self.distribution_plan:
            org_level_plan = org_level['generated_info']

            for prefix_len, prefix_num in org_level_plan.items():
                for count in range(prefix_num):
                    while True:
                        try:
                            # First 4 bits will be IANA part
                            new_bits = AbstractHelper.generate_new_bits(4, prefix_len)
                            new_prefix = IANA + new_bits

                            self.binary_trie.add_node(new_prefix, creating_phase=False)
                            generated_randomly += 1

                            break

                        except (PrefixAlreadyExists, MaximumLevelException):
                            continue
        print(f"[INFO] {generated_randomly} prefixes were generated randomly")
