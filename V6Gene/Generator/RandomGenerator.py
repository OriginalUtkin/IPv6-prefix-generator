import random

class RandomGenerator():


    def random_generate(self, number_of_prefixes):
        IANA = '0010'

        for counter in range(number_of_prefixes):
            # Generate other bits for LIR
            generated_part = random.getrandbits(28)
            binary_repr = IANA + format(generated_part, '0' + str(28) + 'b')

            print(f'New prefix is {self.binary_to_hex(binary_repr)} with len {len(binary_repr)}')
            # TODO : Generate other prefixes for ISP and EU after LIR

    def binary_to_hex(self, binary_representation):
        # TODO: In progress
        tt = [hex(int(binary_representation[i:i + 4], 2))[-1] for i in range(0, len(binary_representation), 4)]
        hex_rep = "".join(tt)

        return hex_rep