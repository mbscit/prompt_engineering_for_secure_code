import logging
import os
from abc import abstractmethod, ABC
from typing import List

from dotenv import load_dotenv

import utils
from project_types.custom_types import Prompt


class GetIDsBy(ABC):
    @abstractmethod
    def condition(self, prompt: Prompt) -> bool:
        pass

    def filtered(self, prompts: List[Prompt], print_ids=False) -> list[str]:
        remaining_ids = [prompt.id for prompt in prompts if self.condition(prompt)]
        if print_ids:
            print(f"Tasks that meet the condition (count: {len(remaining_ids)}): ")
            for id in remaining_ids:
                print(f"\"{id}\",")
        return remaining_ids

    def filtered_from_dataset(self, print_ids=False) -> list[str]:
        load_dotenv()
        dataset = utils.read_dataset_file(utils.relative_path_from_root(os.getenv("DATASET_FILE_PATH")))
        return self.filtered(dataset, print_ids)

    def filtered_from_ids(self, ids: list[str], print_ids=False) -> list[str]:
        load_dotenv()
        dataset = utils.read_dataset_file(utils.relative_path_from_root(os.getenv("DATASET_FILE_PATH")))
        dataset = [prompt for prompt in dataset if prompt.id in ids]
        if len(set(ids)) < len(dataset):
            logging.warning(f"IDs not found in the dataset: {set(ids) - set([prompt.id for prompt in dataset])}")
        return self.filtered(dataset, print_ids)
