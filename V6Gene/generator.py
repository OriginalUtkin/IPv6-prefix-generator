import random


def random_generate():
    IANA = '0010'

    # Generate other bits for LIR
    generated_part = random.getrandbits(28)
    binary_repr = IANA + format(generated_part, '0' + str(28) + 'b')
    print(len(binary_repr))
    print(binary_to_hex(binary_repr))

    # TODO : Generate other prefixes for ISP and EU

def binary_to_hex(binary_representation):
    tt = [hex(int(binary_representation[i:i+4], 2))[-1] for i in range(0,len(binary_representation),4)]
    hex_rep = "".join(tt)

    return(hex_rep)



if __name__ == '__main__':
    random_generate()