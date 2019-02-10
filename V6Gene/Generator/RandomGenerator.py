import attr
from V6Gene.Generator.Helper import Helper
from V6Gene.Trie import Trie

@attr.s
class RandomGenerator():
    # binary_trie = attr.ib(type=Trie)
    distribution_plan = attr.ib(factory=dict, type=dict)

    def random_generate(self):
        IANA = '0010'
        result = []

        for org_level in self.distribution_plan:
            org_level_plan = org_level['generated_info']

            for prefix_len, prefix_num in org_level_plan.items():
                for count in range(prefix_num):
                    # First 4 bits will be IANA part
                    new_bits = Helper.generate_new_bits(4, prefix_len)
                    result.append(IANA + new_bits)

        print([len(i) for i in result])

            # print(f'New prefix is {self.binary_to_hex(binary_repr)} with len {len(binary_repr)}')
            # TODO : Generate other prefixes for ISP and EU after LIR

    def binary_to_hex(self, binary_representation):
        # TODO: In progress
        tt = [hex(int(binary_representation[i:i + 4], 2))[-1] for i in range(0, len(binary_representation), 4)]
        hex_rep = "".join(tt)

        return hex_rep