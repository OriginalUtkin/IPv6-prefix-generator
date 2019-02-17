import attr
from V6Gene.Generator.Helper import Helper
from V6Gene.Trie import Trie
from V6Gene.Exceptions.Exceptions import PrefixAlreadyExists, MaximumLevelException


@attr.s
class RandomGenerator:
    binary_trie = attr.ib(type=Trie)
    distribution_plan = attr.ib(factory=dict, type=dict)

    def random_generate(self):
        IANA = '0010'

        for org_level in self.distribution_plan:
            org_level_plan = org_level['generated_info']

            for prefix_len, prefix_num in org_level_plan.items():
                for count in range(prefix_num):
                    while True:
                        try:
                            # First 4 bits will be IANA part
                            new_bits = Helper.generate_new_bits(4, prefix_len)
                            new_prefix = IANA + new_bits
                            self.binary_trie.add_node(new_prefix, allow_generating=False)

                            break

                        except (PrefixAlreadyExists, MaximumLevelException):
                            continue
