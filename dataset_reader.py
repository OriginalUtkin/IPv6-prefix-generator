import os
from typing import List


def get_datasets(path_to_datasets: str):
    for dir_path, _, file in os.walk(path_to_datasets):
        return [dir_path + '/' + dataset for dataset in file]


def process_datasets(input_datasets_path: List[str]):

    for dataset in input_datasets_path:
        prefixes = set()

        with open(f'{dataset}') as input_dataset:
            for line in input_dataset:
                file_entry = line.split('\t')
                prefixes.add(file_entry[0] + "/" + file_entry[1])

        with open(f"dataset/{dataset.split('/')[1]}", 'w+') as output_dataset:
            for prefix in prefixes:
                output_dataset.write(prefix + '\n')

if __name__ == '__main__':
    datasets = get_datasets("CAIDA_datasets")
    process_datasets(datasets)
