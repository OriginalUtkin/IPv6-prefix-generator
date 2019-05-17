# was developed by Utkin Kirill

import statistics
import os

from V6Gene.Generator.v6Generator import V6Generator
from Common.Validator import Validator


if __name__ == '__main__':
    # V6Gene_module = importlib.import_module()

    main_path = "/".join(os.path.dirname(__file__).split('/')[:-1])

    input_prefixes = Validator.InputArgumentsValidator.read_seed_file(main_path+'/formated_datasets/dataset2007')
    depth_distribution = Validator.InputArgumentsValidator.parse_depth_distribution_file(main_path+'/distributions/depth_distribution/2019_dataset.in')
    level_distribution = ()

    generator = V6Generator(
        prefix_quantity=68798,
        depth_distribution=depth_distribution,
        level_distribution= {0: 63754, 1: 4582, 2: 655, 3: 101, 4: 12, 5: 3, 6: 0},
        input_prefixes=input_prefixes,
        rgr=0.05,
    )

    new_prefixes = generator.start_generating()

    with open(main_path + '/experiments/output/v6gene', 'a') as file:
        for prefix in new_prefixes:
            file.write(prefix + '\n')

    statistics.create_stats(new_prefixes, 'v6gene', generator.get_root())