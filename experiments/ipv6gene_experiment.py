# was developed by Utkin Kirill

import statistics
import os

from IPv6Gene.Generator.v6Generator import V6Generator
from Common.Validator import Validator


if __name__ == '__main__':

    main_path = "/".join(os.path.dirname(__file__).split('/')[:-1])

    input_prefixes = Validator.InputArgumentsValidator.read_seed_file(main_path+'/formated_datasets/dataset2007')
    depth_distribution = Validator.InputArgumentsValidator.parse_depth_distribution_file(main_path+'/distributions/depth_distribution/2019_dataset.in')

    generator = V6Generator(
        prefix_quantity=68798,
        depth_distribution=depth_distribution,
        max_level=5,
        input_prefixes=input_prefixes,
        stats=True
    )

    new_prefixes = generator.start_generating()

    with open('output/ipv6gene', 'a') as file:
        for prefix in new_prefixes:
            file.write(prefix + '\n')

    statistics.create_stats(new_prefixes, 'ipv6gene', generator.get_root())


